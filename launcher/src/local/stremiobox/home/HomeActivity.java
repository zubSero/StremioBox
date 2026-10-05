/* SPDX-License-Identifier: MIT */
package local.stremiobox.home;

import android.app.Activity;
import android.content.Intent;
import android.content.pm.ResolveInfo;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.os.Handler;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.widget.*;
import java.text.DateFormat;
import java.util.*;

/** Dependency-free Android TV home, controlled entirely with the D-pad. */
public final class HomeActivity extends Activity {
    private final Handler handler = new Handler();
    private TextView clock;
    private LinearLayout apps;
    private View primary;
    private boolean firstResume = true;
    private final Runnable tick = new Runnable() {
        @Override public void run() {
            if (clock != null) clock.setText(DateFormat.getTimeInstance(DateFormat.SHORT).format(new Date()));
            handler.postDelayed(this, 15000);
        }
    };

    private int dp(float n) { return Math.round(n * getResources().getDisplayMetrics().density); }
    private TextView text(String s, int size, int color) {
        TextView t = new TextView(this); t.setText(s); t.setTextSize(size);
        t.setTextColor(color); t.setFontFeatureSettings("kern"); return t;
    }
    private GradientDrawable background(int color, int stroke) {
        GradientDrawable d = new GradientDrawable(); d.setColor(color); d.setCornerRadius(dp(14));
        if (stroke != 0) d.setStroke(dp(2), stroke); return d;
    }
    private void focusable(View tile, final boolean hero) {
        tile.setFocusable(true); tile.setClickable(true);
        tile.setBackground(background(hero ? 0xd9382a78 : 0xd9171938, 0x444f5287));
        tile.setOnFocusChangeListener((v, focused) -> {
            v.setBackground(background(focused ? 0xf0443190 : (hero ? 0xd9382a78 : 0xd9171938), focused ? 0xffbbc1ff : 0x444f5287));
            v.animate().scaleX(focused ? 1.025f : 1f).scaleY(focused ? 1.025f : 1f).setDuration(120).start();
            v.setElevation(focused ? dp(8) : 0);
        });
    }
    private Intent launchFor(String pkg) {
        Intent i = getPackageManager().getLeanbackLaunchIntentForPackage(pkg);
        return i != null ? i : getPackageManager().getLaunchIntentForPackage(pkg);
    }
    private void open(Intent intent) {
        try {
            if (intent == null) throw new IllegalStateException();
            startActivity(intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
        } catch (RuntimeException e) {
            Toast.makeText(this, "Deze app is nog niet beschikbaar.", Toast.LENGTH_SHORT).show();
        }
    }
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().getDecorView().setSystemUiVisibility(5894);
        FrameLayout root = new FrameLayout(this);
        ImageView backdrop = new ImageView(this);
        try { backdrop.setImageDrawable(android.graphics.drawable.Drawable.createFromStream(getAssets().open("tv-wallpaper.png"), null)); }
        catch (java.io.IOException e) { backdrop.setBackgroundColor(0xff06071b); }
        backdrop.setScaleType(ImageView.ScaleType.CENTER_CROP);
        root.addView(backdrop, new FrameLayout.LayoutParams(-1, -1));
        LinearLayout content = new LinearLayout(this); content.setOrientation(LinearLayout.VERTICAL);
        content.setClipChildren(false); content.setClipToPadding(false);
        content.setPadding(dp(56), dp(32), dp(56), dp(46));
        root.addView(content, new FrameLayout.LayoutParams(-1, -1));

        LinearLayout header = new LinearLayout(this); header.setGravity(Gravity.CENTER_VERTICAL);
        TextView home = text("THUIS", 13, 0xffb0b2d6); home.setLetterSpacing(0.20f);
        header.addView(home, new LinearLayout.LayoutParams(0, dp(30), 1));
        clock = text("", 15, 0xffe7e8fa); header.addView(clock);
        content.addView(header);
        TextView title = text("Filmavond begint hier.", 32, Color.WHITE);
        title.setTypeface(Typeface.create("sans-serif", Typeface.BOLD));
        LinearLayout.LayoutParams titleParams = new LinearLayout.LayoutParams(-1, -2);
        titleParams.topMargin = dp(33); content.addView(title, titleParams);
        TextView hint = text("Films en series, klaar op het grote scherm.", 15, 0xffb2b7d8);
        LinearLayout.LayoutParams hintParams = new LinearLayout.LayoutParams(-1, -2);
        hintParams.topMargin = dp(8); content.addView(hint, hintParams);

        LinearLayout hero = new LinearLayout(this); hero.setGravity(Gravity.CENTER_VERTICAL);
        hero.setPadding(dp(25), dp(13), dp(24), dp(13));
        ImageView logo = new ImageView(this); logo.setImageResource(getResources().getIdentifier("logo", "drawable", getPackageName()));
        hero.addView(logo, new LinearLayout.LayoutParams(dp(59), dp(59)));
        TextView play = text("Open Stremio  \u203a", 23, Color.WHITE); play.setTypeface(null, Typeface.BOLD);
        LinearLayout.LayoutParams pp = new LinearLayout.LayoutParams(-2, -2); pp.leftMargin = dp(18); hero.addView(play, pp);
        focusable(hero, true); hero.setOnClickListener(v -> open(launchFor("com.stremio.one")));
        hero.setContentDescription("Open Stremio"); primary = hero;
        LinearLayout.LayoutParams hp = new LinearLayout.LayoutParams(dp(395), dp(94)); hp.topMargin = dp(23);
        content.addView(hero, hp);
        TextView appLabel = text("Apps en instellingen", 14, 0xffbec2e0);
        LinearLayout.LayoutParams ap = new LinearLayout.LayoutParams(-1, -2); ap.topMargin = dp(28); ap.bottomMargin = dp(13);
        content.addView(appLabel, ap);
        HorizontalScrollView scroll = new HorizontalScrollView(this);
        scroll.setHorizontalScrollBarEnabled(false); scroll.setClipToPadding(false); scroll.setClipChildren(false);
        apps = new LinearLayout(this); apps.setGravity(Gravity.CENTER_VERTICAL); apps.setPadding(dp(5), dp(5), dp(8), dp(7));
        scroll.addView(apps); content.addView(scroll, new LinearLayout.LayoutParams(-1, dp(78)));
        setContentView(root);
    }
    private void fillApps() {
        apps.removeAllViews();
        Intent settings = new Intent(Settings.ACTION_SETTINGS);
        addApp("Instellingen", getDrawable(android.R.drawable.ic_menu_preferences), settings);
        Map<String, ResolveInfo> found = new TreeMap<>();
        for (String category : new String[]{Intent.CATEGORY_LEANBACK_LAUNCHER, Intent.CATEGORY_LAUNCHER}) {
            for (ResolveInfo r : getPackageManager().queryIntentActivities(new Intent(Intent.ACTION_MAIN).addCategory(category), 0)) {
                String pkg = r.activityInfo.packageName;
                if (!pkg.equals(getPackageName()) && !pkg.equals("com.stremio.one") && !pkg.equals("com.android.tv.settings") && !pkg.equals("org.lineageos.tv.launcher")) found.putIfAbsent(pkg, r);
            }
        }
        List<ResolveInfo> ordered = new ArrayList<>(found.values());
        ordered.sort((a,b) -> a.loadLabel(getPackageManager()).toString().compareToIgnoreCase(b.loadLabel(getPackageManager()).toString()));
        for (ResolveInfo r : ordered) addApp(r.loadLabel(getPackageManager()).toString(), r.loadIcon(getPackageManager()), launchFor(r.activityInfo.packageName));
    }
    private void addApp(String label, android.graphics.drawable.Drawable icon, Intent launch) {
        LinearLayout tile = new LinearLayout(this); tile.setGravity(Gravity.CENTER_VERTICAL); tile.setPadding(dp(17), dp(10), dp(18), dp(10));
        ImageView image = new ImageView(this); image.setImageDrawable(icon); tile.addView(image, new LinearLayout.LayoutParams(dp(30), dp(30)));
        TextView name = text(label, 15, Color.WHITE); name.setSingleLine(true);
        LinearLayout.LayoutParams np = new LinearLayout.LayoutParams(-2, -2); np.leftMargin = dp(12); tile.addView(name, np);
        focusable(tile, false); tile.setOnClickListener(v -> open(launch)); tile.setContentDescription(label);
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-2, dp(60)); p.rightMargin = dp(16); apps.addView(tile, p);
    }
    @Override protected void onResume() {
        super.onResume(); getWindow().getDecorView().setSystemUiVisibility(5894);
        fillApps(); handler.removeCallbacks(tick); tick.run();
        if (firstResume) { primary.requestFocus(); firstResume = false; }
    }
    @Override protected void onPause() { handler.removeCallbacks(tick); super.onPause(); }
    @Override public void onBackPressed() { primary.requestFocus(); }
}
