import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Looper;
import java.io.*;
import java.nio.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.*;

/** Checks the actual Java/native ABI, rather than a particular APK version. */
public final class UpdateGuard {
    static final String OWNER="Ldev/jdtech/mpv/MPVLib;";
    static final Map<String,String> API=new TreeMap<String,String>();
    static {
        API.put("nativeCreate","("+OWNER+"Landroid/content/Context;)J");
        API.put("nativeInit","(J)V"); API.put("nativeDestroy","(J)V");
        API.put("nativeAttachSurface","(JLandroid/view/Surface;)V");
        API.put("nativeDetachSurface","(J)V");
        API.put("nativeCommand","(J[Ljava/lang/String;)V");
        API.put("nativeSetOptionString","(JLjava/lang/String;Ljava/lang/String;)I");
        for(String type:new String[]{"Int","Double","Boolean","String"}) {
            String boxed=type.equals("Int")?"Integer":type;
            API.put("nativeGetProperty"+type,"(JLjava/lang/String;)Ljava/lang/"+boxed+";");
            String value=type.equals("Int")?"I":type.equals("Double")?"D":type.equals("Boolean")?"Z":"Ljava/lang/String;";
            API.put("nativeSetProperty"+type,"(JLjava/lang/String;"+value+")V");
        }
        API.put("nativeObserveProperty","(JLjava/lang/String;I)V");
    }
    static void require(boolean good,String why) throws IOException { if(!good) throw new IOException(why); }
    static byte[] read(InputStream in) throws IOException {
        ByteArrayOutputStream out=new ByteArrayOutputStream(); byte[] buf=new byte[65536];int n;
        while((n=in.read(buf))!=-1) { require(out.size()+n<=128*1024*1024,"oversized input");out.write(buf,0,n); }
        return out.toByteArray();
    }
    static byte[] read(File f) throws IOException { try(InputStream in=new FileInputStream(f)) { return read(in); } }
    static int uleb(byte[] b,int[] p) throws IOException {
        int v=0;for(int s=0;s<35;s+=7) { int n=b[p[0]++]&255;v|=(n&127)<<s;if(n<128)return v; }
        throw new IOException("invalid dex integer");
    }
    static String zero(byte[] b,int start) throws IOException {
        int end=start;while(end<b.length && b[end]!=0)end++;
        require(start>=0 && end<b.length,"invalid string");return new String(b,start,end-start,"UTF-8");
    }
    static Map<String,String> dex(byte[] data) throws IOException {
        require(data.length>=112 && data[0]=='d' && data[1]=='e' && data[2]=='x',"unsupported dex");
        ByteBuffer b=ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN);
        int ns=b.getInt(56),os=b.getInt(60);String[] strings=new String[ns];
        for(int i=0;i<ns;i++) { int[] p={b.getInt(os+4*i)};uleb(data,p);strings[i]=zero(data,p[0]); }
        int nt=b.getInt(64),ot=b.getInt(68);String[] types=new String[nt];
        for(int i=0;i<nt;i++)types[i]=strings[b.getInt(ot+4*i)];
        int op=b.getInt(76),om=b.getInt(92),nc=b.getInt(96),oc=b.getInt(100);
        Map<String,String> found=new TreeMap<String,String>();
        for(int i=0;i<nc;i++) {
            int c=oc+i*32;if(!types[b.getInt(c)].equals(OWNER))continue;
            int[] p={b.getInt(c+24)};require(p[0]!=0,"missing MPV class data");
            int sf=uleb(data,p),inf=uleb(data,p),dm=uleb(data,p),vm=uleb(data,p);
            for(int f=0;f<sf+inf;f++){uleb(data,p);uleb(data,p);}
            for(int count:new int[]{dm,vm}) {
                int id=0;for(int m=0;m<count;m++) {
                    id+=uleb(data,p);int access=uleb(data,p);uleb(data,p);
                    if((access&0x100)==0)continue;
                    require((access&8)==0,"static native method ABI changed");
                    int method=om+id*8,proto=op+(b.getShort(method+2)&65535)*12;
                    require(types[b.getShort(method)&65535].equals(OWNER),"native owner mismatch");
                    int params=b.getInt(proto+8);StringBuilder desc=new StringBuilder("(");
                    if(params!=0)for(int k=0;k<b.getInt(params);k++)desc.append(types[b.getShort(params+4+k*2)&65535]);
                    desc.append(')').append(types[b.getInt(proto+4)]);
                    String name=strings[b.getInt(method+4)];require(!found.containsKey(name),"overloaded native ABI");
                    found.put(name,desc.toString());
                }
            }
        }
        return found;
    }
    static Set<String> symbols(byte[] data,boolean defined) throws IOException {
        require(data.length>=64 && data[0]==127 && data[1]=='E' && data[2]=='L' && data[3]=='F' && data[4]==2 && data[5]==1,"expected ELF64 little endian");
        ByteBuffer b=ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN);
        require(b.getShort(18)==62,"expected x86_64");
        int so=(int)b.getLong(40),se=b.getShort(58)&65535,sn=b.getShort(60)&65535;
        Set<String> found=new HashSet<String>();
        for(int i=0;i<sn;i++) {
            int s=so+i*se;if(b.getInt(s+4)!=11)continue;
            int strings=so+b.getInt(s+40)*se,base=(int)b.getLong(strings+24);
            int off=(int)b.getLong(s+24),size=(int)b.getLong(s+32),entry=(int)b.getLong(s+56);
            require(entry>=24,"invalid symbol table");
            for(int p=off;p<off+size;p+=entry) {
                int binding=(data[p+4]&255)>>4,visibility=data[p+5]&3;
                if((b.getShort(p+6)!=0)==defined && (!defined || (binding!=0 && visibility==0)))found.add(zero(data,base+b.getInt(p)));
            }
        }
        require(!found.isEmpty(),"missing ELF symbols");return found;
    }
    static final Map<String,String> PLAYER_FIELDS=new TreeMap<String,String>();
    static {
        String p="Lcom/stremio/common/players/MpvPlayer;";
        String manager="Lcom/stremio/common/players/PlaybackManager;";
        PLAYER_FIELDS.put(OWNER+":observers","Ljava/util/List;");
        PLAYER_FIELDS.put(p+":mpv",OWNER);
        PLAYER_FIELDS.put(p+":context","Landroid/content/Context;");
        PLAYER_FIELDS.put(p+":mainHandler","Landroid/os/Handler;");
        PLAYER_FIELDS.put(p+":externalTextTracks","Ljava/util/List;");
        PLAYER_FIELDS.put(p+":playerListener","Lcom/stremio/common/players/PlayerListener;");
        PLAYER_FIELDS.put("Lcom/stremio/common/players/MpvPlayer$eventObserver$1;:this$0",p);
        PLAYER_FIELDS.put(manager+":context","Landroid/content/Context;");
        PLAYER_FIELDS.put("Lcom/stremio/common/players/PlaybackManager$playerListener$1;:this$0",manager);
    }
    static Map<String,String> playerFields(byte[] data) throws IOException {
        ByteBuffer b=ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN);
        int ns=b.getInt(56),os=b.getInt(60);String[] strings=new String[ns];
        for(int i=0;i<ns;i++) { int[] p={b.getInt(os+4*i)};uleb(data,p);strings[i]=zero(data,p[0]); }
        int nt=b.getInt(64),ot=b.getInt(68);String[] types=new String[nt];
        for(int i=0;i<nt;i++)types[i]=strings[b.getInt(ot+4*i)];
        int fields=b.getInt(84),nc=b.getInt(96),oc=b.getInt(100);
        Map<String,String> found=new TreeMap<String,String>();
        for(int i=0;i<nc;i++) {
            int c=oc+i*32;String owner=types[b.getInt(c)];
            boolean wanted=false;
            for(String key:PLAYER_FIELDS.keySet())if(key.startsWith(owner+":")) {wanted=true;break;}
            if(!wanted || b.getInt(c+24)==0)continue;
            int[] p={b.getInt(c+24)};int sf=uleb(data,p),inf=uleb(data,p);
            uleb(data,p);uleb(data,p);
            for(int count:new int[]{sf,inf}) {
                int id=0;
                for(int f=0;f<count;f++) {
                    id+=uleb(data,p);uleb(data,p);int field=fields+id*8;
                    String key=owner+":"+strings[b.getInt(field+4)];
                    if(PLAYER_FIELDS.containsKey(key))found.put(key,types[b.getShort(field+2)&65535]);
                }
            }
        }
        return found;
    }

    static void verify(String apk,String original,String mpv) throws Exception {
        Map<String,String> natives=new TreeMap<String,String>();
        Map<String,String> layout=new TreeMap<String,String>();
        try(ZipFile z=new ZipFile(apk)) {
            Enumeration<? extends ZipEntry> entries=z.entries();
            while(entries.hasMoreElements()) {
                ZipEntry e=entries.nextElement();if(!e.getName().matches("classes[0-9]*\\.dex"))continue;
                try(InputStream in=z.getInputStream(e)) { byte[] data=read(in);Map<String,String> next=dex(data);layout.putAll(playerFields(data));
                    if(!next.isEmpty()) { require(natives.isEmpty(),"duplicate MPV class");natives.putAll(next); }
                }
            }
            require(natives.equals(API),"MPV native method signatures changed");
            require(layout.equals(PLAYER_FIELDS),"Player context/subtitle fields changed");
            byte[] player=read(new File(original)),mpvBytes=read(new File(mpv));
            Set<String> exports=symbols(player,true),needed=new HashSet<String>();
            for(String name:API.keySet())needed.add("Java_dev_jdtech_mpv_MPVLib_"+name);
            require(exports.containsAll(needed),"missing original player JNI exports");
            require(!exports.contains("JNI_OnLoad"),"new JNI initializer requires adapter review");
            Set<String> available=symbols(mpvBytes,true),imports=symbols(mpvBytes,false);
            require(available.containsAll(Arrays.asList("mpv_create","mpv_initialize","mpv_command","mpv_set_option_string","mpv_set_property","mpv_get_property_string")),"mpv API changed");
            require(imports.contains("eglCreateWindowSurface"),"mpv EGL surface API changed");
            // Originals must match the signed APK; mounted repair libraries are never treated as originals.
            for(String name:new String[]{"libplayer.so","libmpv.so"}) {
                ZipEntry e=z.getEntry("lib/x86_64/"+name);require(e!=null,"native library extraction unavailable");
                try(InputStream in=z.getInputStream(e)) { require(Arrays.equals(read(in),name.equals("libplayer.so")?player:mpvBytes),"installed library differs from APK"); }
            }
        }
        System.out.println("COMPATIBLE native-methods="+API.size()+" player-sha256="+sha(new File(original)));
    }
    static String sha(File f) throws Exception {
        MessageDigest md=MessageDigest.getInstance("SHA-256");try(InputStream in=new FileInputStream(f)) {
            byte[] buf=new byte[65536];int n;while((n=in.read(buf))!=-1)md.update(buf,0,n);
        }
        StringBuilder s=new StringBuilder();for(byte v:md.digest())s.append(String.format("%02x",v&255));return s.toString();
    }
    static synchronized void reconcile() {
        try {
            Process p=new ProcessBuilder("/system/bin/sh","/system/etc/nuc-stremio/reconcile.sh").redirectErrorStream(true).start();
            try(InputStream in=p.getInputStream()) { byte[] out=read(in);if(out.length>0)System.out.print(new String(out,"UTF-8")); }
            if(p.waitFor()!=0)System.out.println("Reconciliation failed; retry on next check.");
        } catch(Exception e) { System.out.println("Reconciliation unavailable: "+e.getClass().getSimpleName()); }
    }
    public static void main(String[] args) throws Exception {
        if(args.length==4 && args[0].equals("check")) {
            try { verify(args[1],args[2],args[3]); } catch(Exception e) {
                System.out.println("INCOMPATIBLE "+e.getMessage());System.exit(1);
            }
            return;
        }
        require(args.length==1 && args[0].equals("watch"),"usage: check APK original-player libmpv | watch");
        Looper.prepare();
        try {
            Class<?> cls=Class.forName("android.app.ActivityThread");Object thread=cls.getMethod("systemMain").invoke(null);
            Context ctx=(Context)cls.getMethod("getSystemContext").invoke(thread);
            IntentFilter filter=new IntentFilter();filter.addAction(Intent.ACTION_PACKAGE_ADDED);filter.addAction(Intent.ACTION_PACKAGE_REPLACED);filter.addDataScheme("package");
            ctx.registerReceiver(new BroadcastReceiver() {
                public void onReceive(Context c,Intent i) {
                    if(i.getData()!=null && "com.stremio.one".equals(i.getData().getSchemeSpecificPart()))
                        new Thread(new Runnable(){public void run(){reconcile();}},"Stremio-update-repair").start();
                }
            },filter);
            System.out.println("Package update receiver registered.");
        } catch(Exception e) { System.out.println("Package receiver unavailable; periodic fallback active."); }
        Thread fallback=new Thread(new Runnable(){public void run(){
            while(!new File("/data/local/nuc-stremio-update/disabled").exists()) {
                reconcile();try { Thread.sleep(30000); } catch(InterruptedException e) {return;}
            }
            System.exit(0);
        }},"Stremio-repair-check");fallback.start();Looper.loop();
    }
}
