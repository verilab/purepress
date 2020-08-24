---
title: 在 Android Studio 中使用 Android NDK
categories: Dev
tags: [Java, Android, NDK]
---

## 1. 环境

Android Studio 从 1.3 版本开始加入了 NDK 支持（见 [Android NDK Preview](http://tools.android.com/tech-docs/android-ndk-preview)），所以需要使用 NDK 的话，需更新到 >=1.3 的版本，本文中使用的是 1.5 版（写此文时最新版）。

NDK 版本要求 ndk-r10e（写此文时最新版），由于众所周知的原因，Android Studio 自带的 SDK 管理器下载 NDK 可能会失败，可以单独下载（可在 [这里](http://www.androiddevtools.cn/#ndk) 下载）。

本文的操作系统环境为 OS X，不过 Windows 和 Linux 中的操作应该也相似。

<!-- more -->

## 2. 配置 Android 项目

首先在 Android Studio 创建一个新的项目，从

![image](https://o33x5shzt.qnssl.com/16-2-7/22492684.jpg)

里的「Project Structure」或工具栏上的

![image](https://o33x5shzt.qnssl.com/16-2-7/14635854.jpg)

进入「Project Structure」配置窗口，在「Android NDK Location」那里手动选一下之前下载的 ndk 的目录，然后点「OK」保存。

接着我们需要修改三个文件，分别是 `./build.gradle`、`./app/build.gradle`、`./gradle/wrapper/gradle-wrapper.properties`，修改的内容如下：

- `./gradle/wrapper/gradle-wrapper.properties`

把 `distributionUrl` 的 gradle 版本设置为 2.8，即 `distributionUrl=https\://services.gradle.org/distributions/gradle-2.8-all.zip`

- `./build.gradle`

把 gradle 版本改为实验版：将 `classpath 'com.android.tools.build:gradle:1.5.0'` 改为 `classpath 'com.android.tools.build:gradle-experimental:0.4.0'`（0.4.0 为写此文时最新版），改完之后文件内容应该类似于下面这样：

```
buildscript {
    repositories {
        jcenter()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle-experimental:0.4.0'

        // NOTE: Do not place your application dependencies here; they belong
        // in the individual module build.gradle files
    }
}

allprojects {
    repositories {
        jcenter()
    }
}

task clean(type: Delete) {
    delete rootProject.buildDir
}
```

- `./app/build.gradle`

这个文件改动比较复杂，首先 `apply plugin: 'com.android.application'` 改为 `apply plugin: 'com.android.model.application'`，然后把 `android { }` 整个放在一个 `model { }` 中，然后把 `android { }` 中所有属性都加上 `=` 等号，然后 `buildTypes { }` 放到 `android { }` 的外面，也就是在 `model { }` 中和 `android { }` 并列，并在前面加上 `android.`，然后 `android { }` 里的 `defaultConfig` 后加上 `.with`，然后在 `minSdkVersion ` 和 `targetSdkVersion ` 后面加上 `.apiLevel`，然后把 `android.buildTypes { }` 中 `proguardFiles` 那行改为 `proguardFiles.add(file("proguard-rules.pro"))`，然后在 `model { }` 中加上下面的代码：

```
android.ndk {
    moduleName = "ndkdemo"
}
```

全部改完内容类似于下面这样：

```
apply plugin: 'com.android.model.application'

model {
    android {
        compileSdkVersion = 23
        buildToolsVersion = "23.0.2"

        defaultConfig.with {
            applicationId = "com.demo.ndk"
            minSdkVersion.apiLevel = 14
            targetSdkVersion.apiLevel = 23
            versionCode = 1
            versionName = "1.0"
        }
    }

    android.buildTypes {
        release {
            minifyEnabled = false
            proguardFiles.add(file("proguard-rules.pro"))
        }
    }

    android.ndk {
        moduleName = "ndkdemo"
    }
}

dependencies {
    compile fileTree(dir: 'libs', include: ['*.jar'])
    testCompile 'junit:junit:4.12'
    compile 'com.android.support:appcompat-v7:23.1.1'
}
```

## 3. 编写 C 代码

在 `./app/src/main` 目录中创建一个名为 `jni` 的文件夹，然后在 `MainActivity.java` 中加入导入动态库、声明 native 函数、测试的代码，`MainActivity.java` 内容如下：

```java
package com.demo.ndk;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity {
    static {
        System.loadLibrary("ndkdemo");
    }

    private native int test();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        TextView tv = (TextView) findViewById(R.id.textView);
        tv.setText(String.valueOf(test()));
    }
}
```

这时候点 native 函数声明边上的红色灯泡，会提示「Create function ...」来创建相应的 C 函数，点击后就会自动在 `jni` 目录下生成一个 `ndkdemo.c` 文件，内容如下：

```c
#include <jni.h>

JNIEXPORT jint JNICALL
Java_com_demo_ndk_MainActivity_test(JNIEnv *env, jobject instance) {

    // TODO

}
```

此时修改这个函数的内容即可，这里简便起见直接返回一个整数 3，编译运行即可看到文本框里显示「3」。

## 4. 如何用 C++ 写 native 函数

如果要用 C++ 写 native 函数的话，直接把 `ndkdemo.c` 后缀改成 `cpp` 是不行的，还需要把所有函数声明（如果没有声明就把定义）都放在 `extern "C" { }` 中，如下：

```cpp
#include <jni.h>

extern "C" {

JNIEXPORT jint JNICALL
Java_com_demo_ndk_MainActivity_test(JNIEnv *env, jobject instance) {
    return 3;
}

}
```

如果需要使用 STL，则要在 `./app/build.gradle` 中的 `android.ndk { }` 里加入 `stl = "gnustl_shared"`（见 [C++ Library Support](http://developer.android.com/intl/zh-cn/ndk/guides/cpp-support.html)）。

## 5. 参考资料

- [Android Studio1.4.x JNI开发基础-基本环境配置](http://www.cnblogs.com/zhuyp1015/p/4976116.html)
- [Experimental Plugin User Guide](http://tools.android.com/tech-docs/new-build-system/gradle-experimental)（推荐深入阅读）
- [Android NDK Preview](http://tools.android.com/tech-docs/android-ndk-preview)
- [C++ Library Support](http://developer.android.com/intl/zh-cn/ndk/guides/cpp-support.html)
