plugins {
    id("com.android.application")
}

val gameSlug = (project.findProperty("gameSlug") as String?) ?: "portfolio"
val gameSource = (project.findProperty("gameSource") as String?) ?: "portfolio"
val gameTitle = (project.findProperty("gameTitle") as String?) ?: "Game Factory Quick Games"
val gameAppId = (project.findProperty("gameAppId") as String?) ?: "com.gamefactorylab.quickgames"
val gameStart = when {
    gameSlug == "portfolio" -> "index.html?app=android"
    gameSource == "release-candidates" -> "release-candidates/$gameSlug/index.html?app=android"
    else -> "games/$gameSlug/index.html?app=android"
}

android {
    namespace = "com.gamefactorylab.quickgames"
    compileSdk = 36

    defaultConfig {
        applicationId = gameAppId
        minSdk = 24
        targetSdk = 36
        versionCode = 1
        versionName = "0.2.0"

        resValue("string", "app_name", gameTitle)
        buildConfigField("String", "GAME_START", "\"$gameStart\"")
        buildConfigField("String", "GAME_SLUG", "\"$gameSlug\"")
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }

    buildFeatures {
        buildConfig = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
