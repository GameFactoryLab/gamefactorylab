package com.gamefactorylab.quickgames;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {
    private static final String LOCAL_ROOT = "file:///android_asset/www/";
    private static final String WEB_HOST = "gamefactorylab.github.io";
    private static final String WEB_PREFIX = "/gamefactorylab/";
    private WebView webView;

    @SuppressLint({"SetJavaScriptEnabled", "AddJavascriptInterface"})
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(15, 23, 42));

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setMediaPlaybackRequiresUserGesture(true);

        webView.addJavascriptInterface(new NativeShare(), "GameFactoryNative");
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return route(view, request.getUrl());
            }

            @Override
            @SuppressWarnings("deprecation")
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return route(view, Uri.parse(url));
            }
        });

        setContentView(webView);
        webView.loadUrl(LOCAL_ROOT + BuildConfig.GAME_START);
    }

    private boolean route(WebView view, Uri uri) {
        String scheme = uri.getScheme();
        if ("file".equalsIgnoreCase(scheme)) {
            return false;
        }

        if ("https".equalsIgnoreCase(scheme)
                && WEB_HOST.equalsIgnoreCase(uri.getHost())
                && uri.getPath() != null
                && uri.getPath().startsWith(WEB_PREFIX)) {
            String relative = uri.getPath().substring(WEB_PREFIX.length());
            if (relative.isEmpty()) {
                relative = "index.html";
            } else if (relative.endsWith("/")) {
                relative += "index.html";
            }
            String local = LOCAL_ROOT + relative;
            if (uri.getEncodedQuery() != null && !uri.getEncodedQuery().isEmpty()) {
                local += "?" + uri.getEncodedQuery();
            }
            view.loadUrl(local);
            return true;
        }

        try {
            startActivity(new Intent(Intent.ACTION_VIEW, uri));
        } catch (Exception ignored) {
            // Keep the game usable even if no external handler exists.
        }
        return true;
    }

    public class NativeShare {
        @JavascriptInterface
        public void share(String title, String text, String url) {
            runOnUiThread(() -> {
                Intent intent = new Intent(Intent.ACTION_SEND);
                intent.setType("text/plain");
                intent.putExtra(Intent.EXTRA_SUBJECT, title == null ? "Game Factory" : title);
                String body = (text == null ? "" : text) + (url == null || url.isEmpty() ? "" : " " + url);
                intent.putExtra(Intent.EXTRA_TEXT, body.trim());
                startActivity(Intent.createChooser(intent, "Share challenge"));
            });
        }
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.removeJavascriptInterface("GameFactoryNative");
            webView.destroy();
        }
        super.onDestroy();
    }
}
