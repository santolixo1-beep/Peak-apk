[app]

title = Peak Predictor
package.name = peakpredictor
package.domain = org.peakpredictor

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0
requirements = python3,kivy

orientation = portrait
fullscreen = 0

icon.filename = icono.png

android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a, armeabi-v7a

android.permissions = INTERNET,ACCESS_NETWORK_STATE

[buildozer]
log_level = 2
warn_on_root = 1
