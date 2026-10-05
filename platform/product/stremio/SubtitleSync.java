package local.nuc.stremio;

import android.os.Handler;
import android.util.Log;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.List;

/** Repair the external subtitle selection erased by MpvPlayer.setTrack(AUDIO). */
public final class SubtitleSync {
    private static volatile boolean reportedUnavailable;

    private static Object field(Object owner, String name) throws Exception {
        Field value=owner.getClass().getDeclaredField(name);
        value.setAccessible(true);
        return value.get(owner);
    }

    private static void unavailable(Exception failure) {
        if(reportedUnavailable) return;
        reportedUnavailable=true;
        // Reflection errors may include stream data in their messages.
        Log.w("StremioHdr", "SUBTITLE_UI_SYNC unavailable: "+failure.getClass().getSimpleName());
    }

    public static void afterAudioTrackChange(final Object mpv) {
        try {
            if(!mpv.getClass().getName().equals("dev.jdtech.mpv.MPVLib")) return;
            Object observers=field(mpv,"observers");
            if(!(observers instanceof List)) return;
            List<?> snapshot;
            synchronized(observers) { snapshot=new ArrayList<Object>((List<?>)observers); }
            for(Object observer:snapshot) {
                if(!observer.getClass().getName().equals("com.stremio.common.players.MpvPlayer$eventObserver$1"))
                    continue;
                final Object player=field(observer,"this$0");
                if(!player.getClass().getName().equals("com.stremio.common.players.MpvPlayer")
                    || field(player,"mpv")!=mpv) continue;
                Object handler=field(player,"mainHandler");
                if(!(handler instanceof Handler)) return;
                // setTrack clears the flags AFTER its JNI aid setter returns.
                // Run after that stack has finished, on the player's own handler.
                ((Handler)handler).post(new Runnable() { public void run() {
                    try { synchronize(player,mpv); }
                    catch(Exception failure) { unavailable(failure); }
                }});
            }
        } catch(Exception failure) { unavailable(failure); }
    }

    private static void synchronize(Object player,Object mpv) throws Exception {
        if(field(player,"mpv")!=mpv) return;
        Method get=mpv.getClass().getMethod("getPropertyString",String.class);
        String sid=(String)get.invoke(mpv,"sid");
        if(sid==null || sid.equals("auto") || sid.isEmpty()) return;
        String externalUri=null;
        if(!sid.equals("no")) {
            String countText=(String)get.invoke(mpv,"track-list/count");
            if(countText==null) return;
            int count=Integer.parseInt(countText);
            if(count<0 || count>512) return;
            boolean found=false;
            for(int i=0;i<count;i++) {
                String prefix="track-list/"+i+"/";
                if(!"sub".equals(get.invoke(mpv,prefix+"type"))
                    || !sid.equals(get.invoke(mpv,prefix+"id"))) continue;
                found=true;
                String external=(String)get.invoke(mpv,prefix+"external");
                if("yes".equals(external) || "true".equals(external)) {
                    externalUri=(String)get.invoke(mpv,prefix+"external-filename");
                    if(externalUri==null || externalUri.isEmpty()) return;
                }
                break;
            }
            if(!found) return;
        }
        Object value=field(player,"externalTextTracks");
        if(!(value instanceof List)) return;
        List<?> tracks=(List<?>)value;
        String selectedId=null;
        boolean mismatch=false;
        for(Object track:tracks) {
            Class<?> cls=track.getClass();
            Object uri=cls.getMethod("getUri").invoke(track);
            boolean selected=externalUri!=null && uri!=null && externalUri.equals(uri.toString());
            if(selected) selectedId=(String)cls.getMethod("getId").invoke(track);
            if(selected!=(Boolean)cls.getMethod("getSelected").invoke(track)) mismatch=true;
        }
        // An unrecognized external track must not overwrite the app's selection.
        if((externalUri!=null && selectedId==null) || !mismatch) return;
        String json=(String)get.invoke(mpv,"track-list");
        if(json==null) return;
        // JSON is supplied by Android; the small compile-time SDK excludes it.
        Class.forName("org.json.JSONArray").getConstructor(String.class).newInstance(json);
        if(!sid.equals(get.invoke(mpv,"sid"))) return;
        Method mark=player.getClass().getDeclaredMethod("setTrack$setExternalTrack",player.getClass(),String.class);
        if(mark.getReturnType()!=Void.TYPE || !Modifier.isStatic(mark.getModifiers())) return;
        mark.setAccessible(true);
        mark.invoke(null,player,selectedId);
        mpv.getClass().getMethod("eventProperty",String.class,String.class).invoke(mpv,"track-list",json);
        Log.i("StremioHdr", "SUBTITLE_UI_SYNC selected="+(selectedId==null?"none":"external"));
    }
}
