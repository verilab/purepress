---
title: 在 OS X 上编译 AOSP 源码
updated: 2016-06-04
categories: [Misc, Detailed]
tags: [Android, AOSP]
---

昨天本来是想把 AOSP 的源码下下来方便查阅的，然后莫名其妙就突然打算自己编译一下试试，然后就编译了，中间遇到一些坑，在这里记录一下。

## 1. 准备环境

按道理来说官方是推荐用 Ubuntu LTS 来编译的，不过我也没装，所以就用 OS X 了，AOSP 官网也是有 OS X 的环境配置教程的（[Setting up a Mac OS build environment](https://source.android.com/source/initializing.html#setting-up-a-mac-os-x-build-environment)）。过程基本和官网的教程一致。

### 1.1 创建区分大小写的分区

OS X 默认的文件系统是「case-preserving but case-insensitive」的，也就是文件名保留大小写，但实际并不区分，而 AOSP 建议用区分大小写的文件系统，于是需要创建新分区，运行：

```sh
hdiutil create -type SPARSE -fs 'Case-sensitive Journaled HFS+' -size 100g ~/android.dmg
```

`-type SPARSE` 表示在使用中动态增加镜像的大小（而不是一次性占满），`-size 100g` 指定大小，官方声称「A size of 25GB is the minimum to complete the build」，不要信，我一开始创建的 50GB 都不够用，建议至少 100GB。

之后 `~` 目录（当然这个目录可以自己指定）下会生成一个 `android.dmg.sparseimage`。如果后期发现不够用，需要扩大空间，运行下面命令（注意别忘了先推出镜像）：

```sh
hdiutil resize -size <new-size-you-want>g ~/android.dmg.sparseimage
```

<!-- more -->

### 1.2 安装其它依赖程序

JDK 不用说，开发 Android 应用肯定是装了的。

另外还需要装 Xcode，是因为编译中需要用到一个 OS X SDK 以及一些工具链。装好 Xcode 检查一下你的环境变量里面有没有 `MAC_SDK_VERSION` 这个变量，如果没有，手动设置一下，赋值为你的 OS X 版本，比如 `export MAC_SDK_VERSION=10.11`，因为编译时需要根据这个环境变量找到 Xcode 里面那个 OS X SDK 的路径。

然后 `gmake`、`gnupg` 等程序，这些我是用 brew 装的，官方让用 ports，反正一个道理：

```sh
brew install libsdl gnupg coreutils findutils gnu-sed pngcrush xz
```

`make` 应该是 OS X 自带了的，没有的话，上面再加装一个 `gmake`。后面几个程序官网并没有要装，但是我在第一次编译时候遇到没有 `xz` 命令然后编译跪了的情况，所以后来搜了一些其它教程里面要装的就一起装上了，免得又编译到一半说缺依赖。

注意有一个坑，OS X 自带的 cURL 是基于 SecureTransport（运行 `curl --version` 如果输出里面包含「SecureTransport」那就是了），但是编译 Android M 以上会用到 Jack，然后 Jack 需要基于 OpenSSL 的 cURL，于是和自带的不兼容，解决办法是用 brew 再装一个 OpenSSL 的：

```sh
brew install curl --with-openssl
export PATH=$(brew --prefix curl)/bin:$PATH
```

注意新装的这个不会直接覆盖系统自带的，所以需要手动改一下 `PATH` 去改变默认的 cURL，也就是上面第二行干的事，把它放到 `.profile` 之类的里面，运行 `curl --version` 检查一下，输出里面有「OpenSSL」而不是「SecureTransport」就表示成功。

### 1.3 设置 ccache

就是简单按照官网的指示 [Optimizing a build environment](https://source.android.com/source/initializing.html#optimizing-a-build-environment)，没什么异常。

## 2. 下载源码

可以用 [清华 TUNA 源](https://mirrors.tuna.tsinghua.edu.cn/help/AOSP/) 或 [中科大 LUG 源](https://lug.ustc.edu.cn/wiki/mirrors/help/aosp)。

操作过程与官网教程（[Downloading the Source](https://source.android.com/source/downloading.html)）一致，除了把 Git 仓库链接换成镜像源而已。

源码很大，没记错有 20+GB，没什么注意事项，中间尽量别断网就行（虽然我断了一次，重新 `repo sync` 也没有什么奇怪的事发生）。

## 3. 编译

编译要求 Bash shell，其它 shell 不行。

```sh
. build/envsetup.sh
lunch aosp_arm-eng
```

官网给的代码的编译目标是针对模拟器的，也就是这里的 `aosp_arm-eng`，如果你需要给真机编译，需要填相应的编译目标（也可以先直接 `lunch` 然后选），具体的 Nexus 设备对应的编译目标参数见 [Selecting a device build](https://source.android.com/source/running.html#selecting-device-build)。

如果你打算编译真机的镜像，还需要额外下载相应机型的二进制驱动文件，如果编译 master 分支，在 [Binaries Preview for Nexus Devices](https://developers.google.com/android/nexus/blobs-preview) 下载，如果是指定的版本分支，在 [Google's Nexus driver page](https://developers.google.com/android/nexus/drivers) 下载。下载好的压缩文件解压后是一些脚本，放到 AOSP 源码的主目录分别运行，根据提示需要输入「I ACCEPT」来同意协议，运行结束后主目录下会多出 `vendor` 文件夹，里面就是相应的驱动。

然后就可以开始编译了：

```sh
make -j8
```

这里 `-j` 后面的数字一般设置成 CPU 线程数的一倍或两倍，用来支持多线程编译，比如四核心八线程的 CPU 可以用 `make -j8` 或 `make -j16`。

注意如果开启了多线程编译，编译中出错停止的话，出错的输出可能不在最下方，你需要判断到底是哪些输出提示了出错。

## 4. 刷机

编译成功之后，镜像文件在 `out/target/product/hammerhead`，这里的 `hammerhead` 也就是设备代号，我编译目标选的 Nexus 5，所以是 `hammerhead`，如果选的是模拟器则是 `generic`。

编译时自动设置了一些环境变量（比如 `ANDROID_PRODUCT_OUT`），所以完成后不用切换目录，直接 `adb reboot bootloader`、`fastboot flashall -w` 就可以刷进手机了，而如果编译目标是模拟器，则直接 `emulator` 就可以启动模拟器。

## 5. 遇到并解决的问题

这里记录我在编译过程中遇到的问题，在上面的过程记录中，我已经在可能出问题的地方写了正确的做法，如果你是自己编译时遇到问题，也许可以在这里找到解决办法。

### 5.1 报错找不到目录 -mmacosx-version-min=10.6

这个报错我搜了很久都没有找到解决办法，然后去源码的 `build` 目录搜关键词，找到了 `build/soong/cc/x86_darwin_host.go` 这个文件，分析后明白了，这个错误是因为在构建 shell 命令的时候，因为没找到 OS X SDK 路径，于是那个值返回了空，然后本来这条编译命令应该有这么一串参数 `-isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk -mmacosx-version-min=10.11`，但是中间那个 SDK 的路径没拿到，OS X 版本也没拿到，于是变成了 `-isysroot  -mmacosx-version-min=10.6`，导致报错，根源就是环境变量里没有 `MAC_SDK_VERSION`，运行 `export MAC_SDK_VERSION=10.11` 解决。

### 5.2 报错 Unsupported curl, please use a curl not based on SecureTransport

无法启动 Jack server，完整报错信息：

```sh
FAILED: /bin/bash -c "(prebuilts/sdk/tools/jack-admin install-server prebuilts/sdk/tools/jack-launcher.jar prebuilts/sdk/tools/jack-server-4.8.ALPHA.jar  2>&1 || (exit 0) ) && (JACK_SERVER_VM_ARGUMENTS=\"-Dfile.encoding=UTF-8 -XX:+TieredCompilation\" prebuilts/sdk/tools/jack-admin start-server 2>&1 || exit 0 ) && (prebuilts/sdk/tools/jack-admin update server prebuilts/sdk/tools/jack-server-4.8.ALPHA.jar 4.8.ALPHA 2>&1 || exit 0 ) && (prebuilts/sdk/tools/jack-admin update jack prebuilts/sdk/tools/jacks/jack-2.28.RELEASE.jar 2.28.RELEASE || exit 47; prebuilts/sdk/tools/jack-admin update jack prebuilts/sdk/tools/jacks/jack-3.36.CANDIDATE.jar 3.36.CANDIDATE || exit 47; prebuilts/sdk/tools/jack-admin update jack prebuilts/sdk/tools/jacks/jack-4.7.BETA.jar 4.7.BETA || exit 47 )"
Unsupported curl, please use a curl not based on SecureTransport
Jack server installation not found
Unsupported curl, please use a curl not based on SecureTransport
Unsupported curl, please use a curl not based on SecureTransport
```

这是因为 cURL 版本和 Jack 工具链不兼容，在 [这里](http://stackoverflow.com/questions/33318756/while-i-make-the-source-of-android-6-0-it-failed) 找到解决办法，`brew install curl --with-openssl` 来重新安装一个基于 OpenSSL 的 cURL，并修改环境变量以覆盖系统自带的版本：`export PATH=$(brew --prefix curl)/bin:$PATH`。

### 5.3 其它关于 Jack server 的错误

具体错误信息没有记下来，总之有时候会因为其它原因 Jack server 启动不了，一种可能性是因为已存在 `~/.jack-server`，把它删掉，并运行 `jack-admin kill-server` 杀掉进程（如果它确实在运行的话）。

### 5.4 磁盘空间不够

官网说 25GB 就够了，但其实远远不够，建议分 100GB。

### 5.5 报错 pointer being freed was not allocated

完整报错信息：

```sh
FAILED: /bin/bash -c "(mkdir -p out/target/product/hammerhead/obj/PACKAGING/recovery_patch_intermediates/ ) && (PATH=out/host/darwin-x86/bin:\$PATH out/host/darwin-x86/bin/imgdiff out/target/product/hammerhead/boot.img out/target/product/hammerhead/recovery.img out/target/product/hammerhead/obj/PACKAGING/recovery_patch_intermediates/recovery_from_boot.p )"
imgdiff(84118,0x7fff7443e000) malloc: *** error for object 0x10fdebf8a: pointer being freed was not allocated
*** set a breakpoint in malloc_error_break to debug
failed to reconstruct target deflate chunk 1 [(null)]; treating as normal
chunk 0: type 0 start 0 len 8452106
chunk 1: type 2 start 8452106 len 2593792
chunk 2: type 0 start 9897581 len 403
Construct patches for 3 chunks...
patch   0 is 206 bytes (of 8452106)
patch   1 is 618751 bytes (of 1445475)
patch   2 is 118 bytes (of 0)
chunk   0: normal   (         0,    8452106)         206
chunk   1: deflate  (   8452106,    2443136)      618751  (null)
chunk   2: raw      (  10895242,        118)
/bin/bash: line 1: 84118 Abort trap: 6
```

这个也是搜了很久未果，仔细观察发现是 `out/host/darwin-x86/bin/imgdiff` 这个程序运行时出现了多次释放同一个指针的问题，没找到好的解决办法，于是索性找到它的源码 `bootable/recovery/applypatch/imgdiff.cpp`，根据报错前后的输出，找到相应的代码段，是在 `main` 函数结尾的地方，把 `free(patch_data)` 以及之前的一个循环里释放指针的代码给注释掉，然后重新编译。

### 5.6 报错 error: cannot define category for undefined class 'NSUserActivity'

完整报错信息：

```sh
FAILED: /bin/bash -c "(prebuilts/misc/darwin-x86/ccache/ccache prebuilts/clang/host/darwin-x86/clang-2812033/bin/clang++    -I external/valgrind/include -I external/valgrind -I external/libchrome -I out/host/darwin-x86/obj32/SHARED_LIBRARIES/libchrome_intermediates -I out/host/darwin-x86/gen/SHARED_LIBRARIES/libchrome_intermediates -I libnativehelper/include/nativehelper \$(cat out/host/darwin-x86/obj32/SHARED_LIBRARIES/libchrome_intermediates/import_includes) -isystem system/core/include -isystem system/media/audio/include -isystem hardware/libhardware/include -isystem hardware/libhardware_legacy/include -isystem hardware/ril/include -isystem libnativehelper/include -isystem frameworks/native/include -isystem frameworks/native/opengl/include -isystem frameworks/av/include -isystem frameworks/base/include -isystem out/host/darwin-x86/obj/include -c  -fno-exceptions -Wno-multichar -fPIC -funwind-tables -D__STDC_FORMAT_MACROS -D__STDC_CONSTANT_MACROS -O2 -g -fno-strict-aliasing -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk -mmacosx-version-min=10.8 -DMACOSX_DEPLOYMENT_TARGET=10.8 -integrated-as -fstack-protector-strong -m32 -msse3 -DANDROID -fmessage-length=0 -W -Wall -Wno-unused -Winit-self -Wpointer-arith -DNDEBUG -UDEBUG -D__compiler_offsetof=__builtin_offsetof -Werror=int-conversion -Wno-reserved-id-macro -Wno-format-pedantic -Wno-unused-command-line-argument -fcolor-diagnostics   -target i686-apple-darwin  -Wsign-promo -Wno-inconsistent-missing-override   -Wall -Werror -D__ANDROID_HOST__ -DDONT_EMBED_BUILD_METADATA -D_FILE_OFFSET_BITS=64 -Wno-deprecated-declarations -fPIC -D_USING_LIBCXX -std=gnu++14 -nostdinc++  -Werror=int-to-pointer-cast -Werror=pointer-to-int-cast  -Werror=address-of-temporary -Werror=null-dereference -Werror=return-type    -MD -MF out/host/darwin-x86/obj32/SHARED_LIBRARIES/libchrome_intermediates/base/sys_info_mac.d -o out/host/darwin-x86/obj32/SHARED_LIBRARIES/libchrome_intermediates/base/sys_info_mac.o external/libchrome/base/sys_info_mac.mm ) && (cp out/host/darwin-x86/obj32/SHARED_LIBRARIES/libchrome_intermediates/base/sys_info_mac.d out/host/darwin-x86/obj32/SHARED_LIBRARIES/libchrome_intermediates/base/sys_info_mac.P; sed -e 's/#.*//' -e 's/^[^:]*: *//' -e 's/ *\\\\\$//' -e '/^\$/ d' -e 's/\$/ :/' < out/host/darwin-x86/obj32/SHARED_LIBRARIES/libchrome_intermediates/base/sys_info_mac.d >> out/host/darwin-x86/obj32/SHARED_LIBRARIES/libchrome_intermediates/base/sys_info_mac.P; rm -f out/host/darwin-x86/obj32/SHARED_LIBRARIES/libchrome_intermediates/base/sys_info_mac.d )"
In file included from external/libchrome/base/sys_info_mac.mm:20:
external/libchrome/base/mac/sdk_forward_declarations.h:505:12: error: cannot define category for undefined class 'NSUserActivity'
@interface NSUserActivity (YosemiteSDK)
           ^
../../../Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk/System/Library/Frameworks/AppKit.framework/Headers/NSApplication.h:21:8: note: forward declaration of class here
@class NSUserActivity;
       ^
1 error generated.
```

研究了错误输出以及出错的这条命令之后发现 `external/libchrome/base/sys_info_mac.mm`、`external/libchrome/base/mac/sdk_forward_declarations.h` 这两个文件里面会根据不同的 OS X 系统版本做一些不同的事情，可以看到出错的这条命令里面有 `-mmacosx-version-min=10.8 -DMACOSX_DEPLOYMENT_TARGET=10.8` 这样一些参数，这和问题 5.1 有点像，问题同样出在 `build/soong/cc/x86_darwin_host.go` 这个文件，查看该文件发现 `mmacosx-version-min` 和 `DMACOSX_DEPLOYMENT_TARGET` 这两个参数是由 `macSdkVersion` 这个变量来的，而这个变量默认值被设置成了 `darwinSupportedSdkVersions[0]`，而 `darwinSupportedSdkVersions` 是一个数组，内容如下：

```go
darwinSupportedSdkVersions = []string{
    "10.8",
    "10.9",
    "10.10",
    "10.11",
}
```

默认是第一个元素也就是 10.8，而我 OS X 版本是 10.11，于是把 `pctx.StaticVariable("macSdkVersion", darwinSupportedSdkVersions[0])` 改成 `pctx.StaticVariable("macSdkVersion", darwinSupportedSdkVersions[3])`，重新编译，就好了。

### 5.7 编译出来的镜像刷到手机后无法开机，卡在 Google 标志

这是因为没有打包设备的二进制驱动文件，需要额外下载并重新编译镜像。

如果编译 master 分支，在 [Binaries Preview for Nexus Devices](https://developers.google.com/android/nexus/blobs-preview) 下载，如果是 指定的版本分支，在 [Google's Nexus driver page](https://developers.google.com/android/nexus/drivers) 下载。下载好的压缩文件解压后是一些脚本，放到 AOSP 源码的主目录分别运行，根据提示需要输入「I ACCEPT」来同意协议，运行结束后主目录下会多出 `vendor` 文件夹，里面就是相应的驱动，然后重新运行编译即可。

## 6. 参考资料

- [AOSP 官方文档](https://source.android.com/source/initializing.html)
- [Android 镜像使用帮助](https://lug.ustc.edu.cn/wiki/mirrors/help/aosp)
- [在Mac 10.11中编译Android 6.0源码](https://seewhy.me/2016/01/01/aospcompilation/)
- [While I make the source of Android 6.0, it failed](http://stackoverflow.com/questions/33318756/while-i-make-the-source-of-android-6-0-it-failed)
- [Android 4.1 (Jelly Bean) 源码编译过程总结](http://blog.csdn.net/zjmdp/article/details/7737802)
