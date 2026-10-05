package local.nuc.stremio;

import android.app.Activity;
import android.app.Application;
import android.media.MediaExtractor;
import android.media.MediaFormat;
import android.os.Bundle;
import android.util.Log;
import android.view.Window;
import android.view.WindowManager;
import java.lang.ref.WeakReference;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

/** Loaded only by the pinned native adapter in the existing Stremio process. */
public final class HdrBridge {
    private static volatile WeakReference<Activity> current = new WeakReference<Activity>(null);
    private static long activeId;
    private static int previousMode;
    private static int previousColor;
    private static WeakReference<Activity> configured = new WeakReference<Activity>(null);
    private static volatile long redrawAfterPause;
    private static volatile int resumeGeneration;
    private static native Activity currentActivity();
    private static native Object currentMpv(long id,int generation);
    private static native boolean alive(long id,int generation);
    private static native String metrics(long id,int generation);
    private static native void redraw(long id);
    private static native void ready(long id, int generation, String[] command,
        boolean hdr, int transfer, int standard, int width, int height, float fps);

    public static void afterAudioTrackChange(Object mpv) {
        SubtitleSync.afterAudioTrackChange(mpv);
    }

    public static void install(Application app) {
        app.registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks() {
            public void onActivityResumed(final Activity activity) {
                current=new WeakReference<Activity>(activity);
                final int generation=++resumeGeneration;
                final long id=redrawAfterPause;
                Log.i("StremioHdr", "ACTIVITY_RESUME configured="+(configured.get()==activity)
                    +" recovery="+(id!=0)+" generation="+generation);
                if(id==0 || configured.get()!=activity) return;
                redrawAfterPause=0;
                // Let the existing player reattach its Android Surface first.
                new Thread(new Runnable() { public void run() {
                    try { Thread.sleep(500); }
                    catch(InterruptedException interrupted) { Thread.currentThread().interrupt();return; }
                    if(generation==resumeGeneration && current.get()==activity && !activity.isFinishing())
                        redraw(id);
                }}, "stremio-wake-redraw").start();
            }
            public void onActivityCreated(Activity activity, Bundle state) {}
            public void onActivityStarted(Activity activity) {}
            public void onActivityPaused(Activity activity) {
                ++resumeGeneration;
                if(configured.get()==activity) redrawAfterPause=activeId;
                Log.i("StremioHdr", "ACTIVITY_PAUSE configured="+(configured.get()==activity)
                    +" recovery="+(redrawAfterPause!=0)+" generation="+resumeGeneration);
            }
            public void onActivityStopped(Activity activity) {}
            public void onActivitySaveInstanceState(Activity activity, Bundle state) {}
            public void onActivityDestroyed(Activity activity) {
                if(current.get()==activity) current=new WeakReference<Activity>(null);
            }
        });
        Activity activity=currentActivity();
        if(activity!=null) current=new WeakReference<Activity>(activity);
        Log.i("StremioHdr", "Bridge installed; activity="+(activity==null?"pending":activity.getClass().getName()));
    }

    public static void prepare(final long id, final int generation, final String[] command) {
        new Thread(new Runnable() { public void run() {
            int transfer=0,standard=0,width=0,height=0;
            float fps=24;
            MediaExtractor extractor=new MediaExtractor();
            try {
                extractor.setDataSource(command[1]);
                for(int n=0;n<extractor.getTrackCount();n++) {
                    MediaFormat format=extractor.getTrackFormat(n);
                    String mime=format.getString("mime");
                    if(mime==null || !mime.startsWith("video/")) continue;
                    if(format.containsKey("color-transfer")) transfer=format.getInteger("color-transfer");
                    if(format.containsKey("color-standard")) standard=format.getInteger("color-standard");
                    width=format.getInteger("width");height=format.getInteger("height");
                    if(format.containsKey("frame-rate")) {
                        try { fps=format.getFloat("frame-rate"); }
                        catch(RuntimeException integerValue) { fps=format.getInteger("frame-rate"); }
                    }
                    break;
                }
            } catch(Exception failure) {
                // Do not log the stream URL or exception message: they may contain credentials.
                Log.w("StremioHdr", "Container probe failed: "+failure.getClass().getSimpleName());
            } finally { extractor.release(); }
            if(!alive(id,generation)) return;
            Activity activity=activityForMpv(currentMpv(id,generation));
            if(activity==null) activity=current.get();
            if(activity==null) activity=currentActivity();
            boolean hdr=transfer==6 && standard==6 && hasHdr10(activity);
            if(!configureWindow(activity,id,hdr,fps)) hdr=false;
            ready(id,generation,command,hdr,transfer,standard,width,height,fps);
            try {
                while(alive(id,generation)) {
                    Thread.sleep(5000);
                    String values=metrics(id,generation);
                    if(values!=null) Log.i("StremioHdr", "METRICS "+values);
                }
            } catch(InterruptedException interrupted) { Thread.currentThread().interrupt(); }
        }}, "stremio-hdr-probe").start();
    }

    // App-owned fields are available without reflecting into ActivityThread.
    private static Object playerField(Object owner,String name) throws Exception {
        java.lang.reflect.Field field=owner.getClass().getDeclaredField(name);
        field.setAccessible(true);
        return field.get(owner);
    }

    private static Activity activityForMpv(Object mpv) {
        try {
            if(mpv==null || !mpv.getClass().getName().equals("dev.jdtech.mpv.MPVLib")) return null;
            Object observers=playerField(mpv,"observers");
            if(!(observers instanceof java.util.List)) return null;
            java.util.List<?> snapshot;
            synchronized(observers) {
                snapshot=new java.util.ArrayList<Object>((java.util.List<?>)observers);
            }
            for(Object observer:snapshot) {
                if(observer==null || !observer.getClass().getName().equals(
                        "com.stremio.common.players.MpvPlayer$eventObserver$1")) continue;
                Object player=playerField(observer,"this$0");
                if(player==null || !player.getClass().getName().equals("com.stremio.common.players.MpvPlayer")
                    || playerField(player,"mpv")!=mpv) continue;
                Activity activity=activityForContext(playerField(player,"context"));
                if(activity!=null) return activity;
                // The signed TV APK deliberately gives MpvPlayer an Application.
                // Its listener points back to the screen's PlaybackManager.
                Object listener=playerField(player,"playerListener");
                if(listener==null || !listener.getClass().getName().equals(
                    "com.stremio.common.players.PlaybackManager$playerListener$1")) continue;
                Object manager=playerField(listener,"this$0");
                if(manager==null || !manager.getClass().getName().equals(
                    "com.stremio.common.players.PlaybackManager")) continue;
                if(manager.getClass().getMethod("getPlayer").invoke(manager)!=player) continue;
                activity=activityForContext(playerField(manager,"context"));
                if(activity!=null) return activity;
            }
        } catch(Exception unavailable) {
            Log.w("StremioHdr", "Player activity lookup unavailable: "+unavailable.getClass().getSimpleName());
        }
        return null;
    }

    private static Activity activityForContext(Object value) {
        for(int depth=0;depth<16 && value instanceof android.content.Context;depth++) {
            if(value instanceof Activity) {
                Activity activity=(Activity)value;
                return activity.isFinishing()?null:activity;
            }
            if(!(value instanceof android.content.ContextWrapper)) break;
            value=((android.content.ContextWrapper)value).getBaseContext();
        }
        return null;
    }

    private static boolean hasHdr10(Activity activity) {
        if(activity==null) return false;
        try {
            Object display=activity.getWindowManager().getDefaultDisplay();
            Object caps=display.getClass().getMethod("getHdrCapabilities").invoke(display);
            int[] types=(int[])caps.getClass().getMethod("getSupportedHdrTypes").invoke(caps);
            for(int type:types) if(type==2) return true;
        } catch(Exception failure) {}
        return false;
    }

    private static int hdrMode(Activity activity,float fps) throws Exception {
        Object display=activity.getWindowManager().getDefaultDisplay();
        Object[] modes=(Object[])display.getClass().getMethod("getSupportedModes").invoke(display);
        int width=fps>31?1920:3840,height=fps>31?1080:2160;
        float rate=fps>55?60:fps>31?50:fps>27?30:fps>24.5f?25:24;
        for(Object mode:modes) {
            Class<?> cls=mode.getClass();
            int w=(Integer)cls.getMethod("getPhysicalWidth").invoke(mode);
            int h=(Integer)cls.getMethod("getPhysicalHeight").invoke(mode);
            float hz=(Float)cls.getMethod("getRefreshRate").invoke(mode);
            if(w==width && h==height && Math.abs(hz-rate)<0.1f)
                return (Integer)cls.getMethod("getModeId").invoke(mode);
        }
        throw new IllegalStateException("No verified HDMI mode for HDR");
    }

    private static boolean configureWindow(final Activity activity,final long id,
                                          final boolean hdr,final float fps) {
        if(activity==null) return !hdr;
        final CountDownLatch done=new CountDownLatch(1);
        final boolean[] succeeded={false};
        activity.runOnUiThread(new Runnable() { public void run() {
            try {
                Window window=activity.getWindow();
                WindowManager.LayoutParams params=window.getAttributes();
                java.lang.reflect.Field field=WindowManager.LayoutParams.class.getField("preferredDisplayModeId");
                if(configured.get()!=activity) {
                    previousMode=field.getInt(params);
                    previousColor=(Integer)Window.class.getMethod("getColorMode").invoke(window);
                    configured=new WeakReference<Activity>(activity);
                }
                field.setInt(params,hdr?hdrMode(activity,fps):previousMode);
                Window.class.getMethod("setColorMode",int.class).invoke(window,hdr?2:previousColor);
                window.setAttributes(params);
                activeId=id;
                succeeded[0]=true;
            } catch(Exception failure) {
                Log.e("StremioHdr", "Window configuration failed: "+failure.getClass().getSimpleName());
            } finally { done.countDown(); }
        }});
        try { return done.await(3,TimeUnit.SECONDS) && succeeded[0]; }
        catch(InterruptedException interrupted) { Thread.currentThread().interrupt();return false; }
    }

    public static void restore(final long id) {
        final Activity activity=configured.get();
        if(activity==null) return;
        activity.runOnUiThread(new Runnable() { public void run() {
            if(activeId!=id) return;
            try {
                Window window=activity.getWindow();
                WindowManager.LayoutParams params=window.getAttributes();
                WindowManager.LayoutParams.class.getField("preferredDisplayModeId").setInt(params,previousMode);
                Window.class.getMethod("setColorMode",int.class).invoke(window,previousColor);
                window.setAttributes(params);
            } catch(Exception failure) {
                Log.e("StremioHdr", "Window restore failed: "+failure.getClass().getSimpleName());
            }
            configured=new WeakReference<Activity>(null);activeId=0;
        }});
    }
}
