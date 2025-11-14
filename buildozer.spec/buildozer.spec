[app]
title = MyApp
package.name = myapp
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# main.py файл  
# main.py = main.py

# (str) Application versioning (method 1)
version = 0.1

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET

# (str) Target to build for
target = android

[buildozer]
log_level = 2
warn_on_root = 1
