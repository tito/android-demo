Android Demo
------------

Compile with python-for-android::

    ./build.py --package org.kivy.android.demo --name 'Android Demo' \
        --version 1 --private ~/code/android-demo/ \
        --permission ACCESS_FINE_LOCATION \
        --permission  ACCESS_COARSE_LOCATION \
        --permission  INTERNET \
        debug installd
