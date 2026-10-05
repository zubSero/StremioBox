#define _GNU_SOURCE
#include <jni.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <pthread.h>

extern int __android_log_print(int, const char *, const char *, ...);
extern int __system_property_get(const char *, char *);
extern int32_t Java_local_nuc_player_PlayerActivity_nativeHdrSurface(void *,void *,uint8_t);
#define LOG(...) __android_log_print(4,"StremioHdr",__VA_ARGS__)
#define FAIL(...) __android_log_print(6,"StremioHdr",__VA_ARGS__)
#define NAME(method) Java_dev_jdtech_mpv_MPVLib_##method
#define EXPORT JNIEXPORT

static void *original;
static pthread_mutex_t lock=PTHREAD_MUTEX_INITIALIZER;
static jclass bridge;
static jmethodID prepare_method,restore_method,audio_method;
static uint64_t next_token;
struct state { jlong instance,token; int generation,active; jobject object; int gpu_revision; };
static struct state states[8];

static void *symbol(const char *name) {
    if(!original) original=dlopen("libplayer.nuc-original.so",RTLD_NOW|RTLD_LOCAL);
    void *result=original?dlsym(original,name):NULL;
    if(!result) FAIL("Original JNI adapter symbol unavailable: %s",name);
    return result;
}

static int exception(JNIEnv *env) {
    if(!(*env)->ExceptionCheck(env)) return 0;
    (*env)->ExceptionClear(env);return 1;
}

static jobject current_activity(JNIEnv *env,jclass unused) {
    (void)unused;
    jclass cls=(*env)->FindClass(env,"android/app/ActivityThread");
    if(exception(env) || !cls) return NULL;
    jmethodID current=(*env)->GetStaticMethodID(env,cls,"currentActivityThread","()Landroid/app/ActivityThread;");
    if(exception(env) || !current) { (*env)->DeleteLocalRef(env,cls);return NULL; }
    jobject thread=(*env)->CallStaticObjectMethod(env,cls,current);
    jfieldID activities=(*env)->GetFieldID(env,cls,"mActivities","Landroid/util/ArrayMap;");
    (*env)->DeleteLocalRef(env,cls);
    if(exception(env) || !thread || !activities) return NULL;
    jobject map=(*env)->GetObjectField(env,thread,activities);
    (*env)->DeleteLocalRef(env,thread);
    if(exception(env) || !map) return NULL;
    jclass map_class=(*env)->GetObjectClass(env,map);
    jmethodID size=(*env)->GetMethodID(env,map_class,"size","()I");
    jmethodID value=(*env)->GetMethodID(env,map_class,"valueAt","(I)Ljava/lang/Object;");
    if(exception(env) || !size || !value) return NULL;
    int count=(*env)->CallIntMethod(env,map,size);
    jobject result=NULL;
    for(int i=0;i<count;i++) {
        jobject record=(*env)->CallObjectMethod(env,map,value,i);
        jclass record_class=(*env)->GetObjectClass(env,record);
        jfieldID activity=(*env)->GetFieldID(env,record_class,"activity","Landroid/app/Activity;");
        if(!exception(env) && activity) {
            jobject found=(*env)->GetObjectField(env,record,activity);
            if(found) { if(result) (*env)->DeleteLocalRef(env,result);result=found; }
        }
        (*env)->DeleteLocalRef(env,record_class);(*env)->DeleteLocalRef(env,record);
    }
    (*env)->DeleteLocalRef(env,map_class);(*env)->DeleteLocalRef(env,map);
    if(exception(env)) return NULL;
    return result;
}

static struct state *by_instance(jlong instance) {
    for(unsigned n=0;n<8;n++) if(states[n].active && states[n].instance==instance) return states+n;
    return NULL;
}
static struct state *by_token(jlong token,int generation) {
    for(unsigned n=0;n<8;n++) if(states[n].active && states[n].token==token && states[n].generation==generation) return states+n;
    return NULL;
}

static void option(JNIEnv *env,jobject obj,jlong instance,const char *name,const char *value) {
    typedef jint (*function)(JNIEnv *,jobject,jlong,jstring,jstring);
    function fn=symbol("Java_dev_jdtech_mpv_MPVLib_nativeSetOptionString");
    if(!fn) return;
    jstring key=(*env)->NewStringUTF(env,name),argument=(*env)->NewStringUTF(env,value);
    int status=fn(env,obj,instance,key,argument);
    (*env)->DeleteLocalRef(env,key);(*env)->DeleteLocalRef(env,argument);
    if(status<0) FAIL("Option %s rejected (%d)",name,status);
}
static void property(JNIEnv *env,jobject obj,jlong instance,const char *name,const char *value) {
    typedef void (*function)(JNIEnv *,jobject,jlong,jstring,jstring);
    function fn=symbol("Java_dev_jdtech_mpv_MPVLib_nativeSetPropertyString");
    if(!fn) return;
    jstring key=(*env)->NewStringUTF(env,name),argument=(*env)->NewStringUTF(env,value);
    fn(env,obj,instance,key,argument);
    (*env)->DeleteLocalRef(env,key);(*env)->DeleteLocalRef(env,argument);
}

static jobject current_mpv(JNIEnv *env,jclass cls,jlong token,jint generation) {
    (void)cls;
    pthread_mutex_lock(&lock);
    struct state *state=by_token(token,generation);
    jobject result=state?(*env)->NewLocalRef(env,state->object):NULL;
    pthread_mutex_unlock(&lock);
    return result;
}

static jboolean alive(JNIEnv *env,jclass cls,jlong token,jint generation) {
    (void)env;(void)cls;
    pthread_mutex_lock(&lock);int valid=by_token(token,generation)!=NULL;pthread_mutex_unlock(&lock);
    return valid;
}

static jstring metrics(JNIEnv *env,jclass cls,jlong token,jint generation) {
    (void)cls;
    pthread_mutex_lock(&lock);struct state *state=by_token(token,generation);
    if(!state) { pthread_mutex_unlock(&lock);return NULL; }
    typedef jstring (*function)(JNIEnv *,jobject,jlong,jstring);
    function fn=symbol("Java_dev_jdtech_mpv_MPVLib_nativeGetPropertyString");
    const char *names[]={"time-pos","hwdec-current","video-params/pixelformat",
        "video-out-params/primaries","video-out-params/gamma","estimated-vf-fps",
        "frame-drop-count","decoder-frame-drop-count","pause","vo","sid","secondary-sid"};
    char text[2048];size_t used=0;text[0]=0;
    if(fn) for(unsigned i=0;i<sizeof(names)/sizeof(*names);i++) {
        jstring key=(*env)->NewStringUTF(env,names[i]);
        jstring value=fn(env,state->object,state->instance,key);
        const char *content=value?(*env)->GetStringUTFChars(env,value,NULL):NULL;
        int written=snprintf(text+used,sizeof(text)-used,"%s=%s ",names[i],content?content:"unavailable");
        if(content) (*env)->ReleaseStringUTFChars(env,value,content);
        if(value) (*env)->DeleteLocalRef(env,value);
        (*env)->DeleteLocalRef(env,key);
        if(written<0 || (size_t)written>=sizeof(text)-used) break;
        used+=(size_t)written;
    }
    pthread_mutex_unlock(&lock);return (*env)->NewStringUTF(env,text);
}

static void redraw(JNIEnv *env,jclass cls,jlong token) {
    (void)cls;
    pthread_mutex_lock(&lock);
    struct state *state=NULL;
    for(unsigned n=0;n<8;n++)
        if(states[n].active && states[n].token==token && states[n].generation>0) state=states+n;
    if(!state) { pthread_mutex_unlock(&lock);return; }
    typedef jstring (*getter)(JNIEnv *,jobject,jlong,jstring);
    getter get=symbol("Java_dev_jdtech_mpv_MPVLib_nativeGetPropertyString");
    const char *names[]={"video-params/pixelformat","seekable","pause"};
    int video=0,seekable=0,paused=0;
    if(get) for(unsigned n=0;n<3;n++) {
        jstring key=(*env)->NewStringUTF(env,names[n]);
        jstring value=get(env,state->object,state->instance,key);
        const char *text=value?(*env)->GetStringUTFChars(env,value,NULL):NULL;
        if(n==0) video=text && text[0];
        if(n==1) seekable=text && !strcmp(text,"yes");
        if(n==2) paused=text && !strcmp(text,"yes");
        if(text) (*env)->ReleaseStringUTFChars(env,value,text);
        if(value) (*env)->DeleteLocalRef(env,value);
        (*env)->DeleteLocalRef(env,key);
    }
    if(video) {
        // mpv ignores an unchanged vo list. Alternate equivalent GPU lists to
        // reopen EGL against the resumed Surface without a null/SDR stage.
        // mpv restores its frame itself; preserve pause, audio and position.
        state->gpu_revision=!state->gpu_revision;
        property(env,state->object,state->instance,"vo",state->gpu_revision?"gpu,gpu":"gpu");
        LOG("WAKE_REDRAW video=%d seekable=%d paused=%d",video,seekable,paused);
    }
    pthread_mutex_unlock(&lock);
}

static void ready(JNIEnv *env,jclass cls,jlong token,jint generation,jobjectArray command,
                  jboolean hdr,jint transfer,jint standard,jint width,jint height,jfloat fps) {
    (void)cls;
    pthread_mutex_lock(&lock);
    struct state *state=by_token(token,generation);
    if(!state) {
        pthread_mutex_unlock(&lock);
        (*env)->CallStaticVoidMethod(env,bridge,restore_method,token);
        exception(env);return;
    }
    jobject obj=state->object;jlong instance=state->instance;
    state->gpu_revision=0;
    // Recreate the GPU output so SDR/HDR transitions select a fresh EGL config.
    option(env,obj,instance,"force-window","no");
    property(env,obj,instance,"vo","null");
    if(Java_local_nuc_player_PlayerActivity_nativeHdrSurface(env,NULL,hdr)!=0) hdr=0;
    option(env,obj,instance,"egl-output-format",hdr?"rgb10_a2":"auto");
    char surface[64];
    snprintf(surface,sizeof(surface),"%dx%d",hdr && width>0?width:0,hdr && height>0?height:0);
    option(env,obj,instance,"android-surface-size",surface);
    char hardware_ready[96]={0};
    // This image includes the matching native-buffer decoder source port.
    __system_property_get("ro.vendor.nuc.p010_gpu_only",hardware_ready);
    int hardware_hdr=hdr && !strcmp(hardware_ready,"true");
    option(env,obj,instance,"hwdec",hdr?(hardware_hdr?"mediacodec,no":"no"):"mediacodec,mediacodec-copy,no");
    option(env,obj,instance,"profile","fast");
    option(env,obj,instance,"target-prim",hdr?"bt.2020":"bt.709");
    option(env,obj,instance,"target-trc",hdr?"pq":"bt.1886");
    option(env,obj,instance,"target-peak",hdr?"10000":"auto");
    option(env,obj,instance,"tone-mapping",hdr?"clip":"bt.2390");
    option(env,obj,instance,"hdr-compute-peak","no");
    const char *filter=standard==6 && transfer==6?"format=gamma=pq:primaries=bt.2020:colormatrix=bt.2020-ncl":
                       standard==6 && transfer==7?"format=gamma=hlg:primaries=bt.2020:colormatrix=bt.2020-ncl":"";
    option(env,obj,instance,"vf",filter);
    property(env,obj,instance,"vo","gpu");
    option(env,obj,instance,"force-window","yes");
    LOG("Source HDR=%d transfer=%d standard=%d size=%dx%d fps=%.3f software=%d",hdr,transfer,standard,width,height,fps,hdr && !hardware_hdr);
    typedef void (*function)(JNIEnv *,jobject,jlong,jobjectArray);
    function fn=symbol("Java_dev_jdtech_mpv_MPVLib_nativeCommand");
    if(fn) fn(env,obj,instance,command);
    pthread_mutex_unlock(&lock);
}

static int install_bridge(JNIEnv *env,jobject context) {
    if(bridge) return 1;
    jclass context_class=(*env)->GetObjectClass(env,context);
    jmethodID get_loader=(*env)->GetMethodID(env,context_class,"getClassLoader","()Ljava/lang/ClassLoader;");
    jobject parent=(*env)->CallObjectMethod(env,context,get_loader);
    (*env)->DeleteLocalRef(env,context_class);
    jclass loader_class=(*env)->FindClass(env,"dalvik/system/DexClassLoader");
    jmethodID constructor=(*env)->GetMethodID(env,loader_class,"<init>","(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/ClassLoader;)V");
    jstring path=(*env)->NewStringUTF(env,"/data/user/0/com.stremio.one/files/nuc-hdr/hdr-bridge.jar");
    jstring cache=(*env)->NewStringUTF(env,"/data/user/0/com.stremio.one/code_cache");
    jobject loader=(*env)->NewObject(env,loader_class,constructor,path,cache,NULL,parent);
    jmethodID load=(*env)->GetMethodID(env,loader_class,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;");
    jstring name=(*env)->NewStringUTF(env,"local.nuc.stremio.HdrBridge");
    jclass local=(*env)->CallObjectMethod(env,loader,load,name);
    (*env)->DeleteLocalRef(env,name);(*env)->DeleteLocalRef(env,path);(*env)->DeleteLocalRef(env,cache);
    (*env)->DeleteLocalRef(env,parent);(*env)->DeleteLocalRef(env,loader);(*env)->DeleteLocalRef(env,loader_class);
    if(exception(env) || !local) { FAIL("HDR helper could not be loaded");return 0; }
    JNINativeMethod methods[]={
        {"currentActivity","()Landroid/app/Activity;",(void *)current_activity},
        {"currentMpv","(JI)Ljava/lang/Object;",(void *)current_mpv},
        {"alive","(JI)Z",(void *)alive},
        {"metrics","(JI)Ljava/lang/String;",(void *)metrics},
        {"redraw","(J)V",(void *)redraw},
        {"ready","(JI[Ljava/lang/String;ZIIIIF)V",(void *)ready}
    };
    if((*env)->RegisterNatives(env,local,methods,6)!=0) { exception(env);return 0; }
    prepare_method=(*env)->GetStaticMethodID(env,local,"prepare","(JI[Ljava/lang/String;)V");
    restore_method=(*env)->GetStaticMethodID(env,local,"restore","(J)V");
    audio_method=(*env)->GetStaticMethodID(env,local,"afterAudioTrackChange","(Ljava/lang/Object;)V");
    jmethodID install=(*env)->GetStaticMethodID(env,local,"install","(Landroid/app/Application;)V");
    if(exception(env) || !prepare_method || !restore_method || !audio_method || !install) return 0;
    bridge=(*env)->NewGlobalRef(env,local);
    (*env)->CallStaticVoidMethod(env,local,install,context);
    (*env)->DeleteLocalRef(env,local);
    if(exception(env)) { FAIL("HDR helper install failed");return 0; }
    return 1;
}

EXPORT jlong NAME(nativeCreate)(JNIEnv *env,jobject self,jobject object,jobject context) {
    typedef jlong (*function)(JNIEnv *,jobject,jobject,jobject);
    function fn=symbol("Java_dev_jdtech_mpv_MPVLib_nativeCreate");
    if(!fn) return 0;
    jlong instance=fn(env,self,object,context);
    if(!instance || !install_bridge(env,context)) return instance;
    pthread_mutex_lock(&lock);
    for(unsigned n=0;n<8;n++) if(!states[n].active) {
        states[n]=(struct state){.instance=instance,.token=++next_token,.active=1,
            .object=(*env)->NewGlobalRef(env,self)};break;
    }
    pthread_mutex_unlock(&lock);
    return instance;
}

EXPORT void NAME(nativeCommand)(JNIEnv *env,jobject self,jlong instance,jobjectArray command) {
    if(bridge && (*env)->GetArrayLength(env,command)>=2) {
        jstring first=(*env)->GetObjectArrayElement(env,command,0);
        const char *text=(*env)->GetStringUTFChars(env,first,NULL);
        int load=text && !strcmp(text,"loadfile");
        (*env)->ReleaseStringUTFChars(env,first,text);(*env)->DeleteLocalRef(env,first);
        if(load) {
            pthread_mutex_lock(&lock);struct state *state=by_instance(instance);
            jlong token=state?state->token:0;int generation=state?++state->generation:0;
            pthread_mutex_unlock(&lock);
            if(token) {
                (*env)->CallStaticVoidMethod(env,bridge,prepare_method,token,generation,command);
                if(!exception(env)) return;
                FAIL("Asynchronous source preparation failed; original playback used");
            }
        }
    }
    typedef void (*function)(JNIEnv *,jobject,jlong,jobjectArray);
    function fn=symbol("Java_dev_jdtech_mpv_MPVLib_nativeCommand");
    if(fn) fn(env,self,instance,command);
}

EXPORT void NAME(nativeDestroy)(JNIEnv *env,jobject self,jlong instance) {
    pthread_mutex_lock(&lock);struct state *state=by_instance(instance);jlong token=0;
    if(state) { token=state->token;state->active=0;(*env)->DeleteGlobalRef(env,state->object); }
    pthread_mutex_unlock(&lock);
    typedef void (*function)(JNIEnv *,jobject,jlong);
    function fn=symbol("Java_dev_jdtech_mpv_MPVLib_nativeDestroy");
    if(fn) fn(env,self,instance);
    if(token) { (*env)->CallStaticVoidMethod(env,bridge,restore_method,token);exception(env); }
    pthread_mutex_lock(&lock);int remaining=0;
    for(unsigned n=0;n<8;n++) remaining+=states[n].active;
    if(!remaining) Java_local_nuc_player_PlayerActivity_nativeHdrSurface(env,NULL,0);
    pthread_mutex_unlock(&lock);
}

// Preserve the exact existing JNI API. Controls, subtitles and event delivery
// are delegated to the original adapter and the existing Stremio interface.
#define PASS_VOID(method,extra,args) \
EXPORT void NAME(method)(JNIEnv *env,jobject self,jlong instance extra) { \
    typedef void (*function)(JNIEnv *,jobject,jlong extra); \
    function fn=symbol("Java_dev_jdtech_mpv_MPVLib_" #method); \
    if(fn) fn(env,self,instance args); }
#define PASS_RESULT(type,method,extra,args) \
EXPORT type NAME(method)(JNIEnv *env,jobject self,jlong instance extra) { \
    typedef type (*function)(JNIEnv *,jobject,jlong extra); \
    function fn=symbol("Java_dev_jdtech_mpv_MPVLib_" #method); \
    return fn?fn(env,self,instance args):0; }
#define COMMA ,
PASS_VOID(nativeInit,,)

EXPORT void NAME(nativeAttachSurface)(JNIEnv *env,jobject self,jlong instance,jobject surface) {
    typedef void (*function)(JNIEnv *,jobject,jlong,jobject);
    function fn=symbol("Java_dev_jdtech_mpv_MPVLib_nativeAttachSurface");
    LOG("SURFACE_ATTACH begin");
    if(fn) fn(env,self,instance,surface);
    LOG("SURFACE_ATTACH complete");
}

EXPORT void NAME(nativeDetachSurface)(JNIEnv *env,jobject self,jlong instance) {
    typedef void (*function)(JNIEnv *,jobject,jlong);
    function fn=symbol("Java_dev_jdtech_mpv_MPVLib_nativeDetachSurface");
    LOG("SURFACE_DETACH begin");
    if(fn) fn(env,self,instance);
    LOG("SURFACE_DETACH complete");
}

PASS_RESULT(jint,nativeSetOptionString,COMMA jstring name COMMA jstring value,COMMA name COMMA value)
PASS_RESULT(jobject,nativeGetPropertyInt,COMMA jstring name,COMMA name)
PASS_RESULT(jobject,nativeGetPropertyDouble,COMMA jstring name,COMMA name)
PASS_RESULT(jobject,nativeGetPropertyBoolean,COMMA jstring name,COMMA name)
PASS_RESULT(jstring,nativeGetPropertyString,COMMA jstring name,COMMA name)
PASS_VOID(nativeSetPropertyInt,COMMA jstring name COMMA jint value,COMMA name COMMA value)
PASS_VOID(nativeSetPropertyDouble,COMMA jstring name COMMA jdouble value,COMMA name COMMA value)
PASS_VOID(nativeSetPropertyBoolean,COMMA jstring name COMMA jboolean value,COMMA name COMMA value)
EXPORT void NAME(nativeSetPropertyString)(JNIEnv *env,jobject self,jlong instance,jstring name,jstring value) {
    const char *key=(*env)->GetStringUTFChars(env,name,NULL);
    int audio=key && !strcmp(key,"aid");
    if(key) (*env)->ReleaseStringUTFChars(env,name,key);
    typedef void (*function)(JNIEnv *,jobject,jlong,jstring,jstring);
    function fn=symbol("Java_dev_jdtech_mpv_MPVLib_nativeSetPropertyString");
    if(fn) fn(env,self,instance,name,value);
    if(audio && bridge && !(*env)->ExceptionCheck(env)) {
        (*env)->CallStaticVoidMethod(env,bridge,audio_method,self);
        if(exception(env)) FAIL("Subtitle menu synchronization unavailable");
    }
}
PASS_VOID(nativeObserveProperty,COMMA jstring name COMMA jint format,COMMA name COMMA format)
