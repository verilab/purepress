---
title: 从 DLL 文件生成 LIB 文件
categories: [Dev, Detailed]
tags: [动态链接库, Windows, 酷Q]
---

标题可能有一定误导嫌疑，首先这里的 lib 文件不是指静态编译的 lib 文件，而是和 dll 配套使用的用来通过链接的 lib 文件；另外也不是从 dll 生成，而是直接生成，只是需要先通过 dll 来查看有哪些导出函数。

## 故事背景

在做酷 Q 插件开发的时候，发现官方的 C++ SDK 很久没有更新了，找了一圈发现其实它的函数实现都在安装目录的 `CQP.dll`，我要做的就是能让 C++ 代码去调用里面的函数，根据官方 SDK 的结构，光使用头文件来声明是没有用的，还需要一个 `.lib` 文件，研究了一圈发现其实 SDK 所谓的 `.lib` 文件并不是真正的函数实现，而只是用来通过编译的一个东西，它内部实际上是对 dll 中的函数的一些描述。于是就有了后面的折腾。

## 方法和坑……

**需要说明的是，这里主要说的是针对酷 Q 的 dll 的情况，似乎编译 dll 的时候，函数的修饰符会影响很多结果，我也不太清楚酷 Q 具体是怎么修饰的导出函数，所以，这里说的方法可能不具有普适性。**

我本来以为那个 `.lib` 文件是把 dll 转换成静态编译的，但似乎这其实是做不到的（或者我没找到办法），然后发现只是一个对 dll 里函数的描述，于是找到了生成 lib 文件的办法。

### 获取 DLL 文件的导出函数列表

首先需要知道代码里面会调用那些函数的函数名称和参数列表，这也就需要知道 dll 里面有哪些函数。打开 VS 附带的一个「Visual Studio Developer Command Prompt」（可以在开始菜单搜索到），然后进入 dll 文件所在目录，运行 `dumpbin.exe /exports Some.dll > dump` 即可把导出函数等一堆信息 dump 到 `dump` 文件中，类似下面这样：

```
Microsoft (R) COFF/PE Dumper Version 14.10.25019.0
Copyright (C) Microsoft Corporation.  All rights reserved.


Dump of file .\CQP.dll

File Type: DLL

  Section contains the following exports for CQP.dll

    00000000 characteristics
    590B3029 time date stamp Thu May  4 21:44:09 2017
        0.00 version
           1 ordinal base
          36 number of functions
          36 number of names

    ordinal hint RVA      name

          1    0 0006F0D2 CQ_addLog
          2    1 0006F1D2 CQ_getAppDirectory
          3    2 0006F12C CQ_getCookies
          4    3 0006F160 CQ_getCsrfToken

......
```

从这里就可以知道 dll 的导出函数有哪些，不过只有函数名，我这里遇到的情况，还需要知道参数列表（准确地说是参数列表所占用的字节数）。

<!-- more -->

### 手动编辑 DEF 文件

然后就是把这些函数名写到一个 `.def` 文件中，如：

```
LIBRARY Some
EXPORTS
CQ_addLog@16
CQ_getAppDirectory@4
CQ_getCookies@4
CQ_getCsrfToken@4
```

这里，前两行是固定的，`Some` 换成你的链接库的名字。第三行开始，每行一个函数，结尾的 `@` 加数字是参数列表占用的字节数，应该是用于在调用时的参数压栈。

### 生成 LIB 文件

有了 `.def` 文件之后，使用 `lib.exe` 命令来生成 `.lib` 文件：

```bat
lib.exe /def:Some.def /out:Some.lib
```

网上搜到的所有文章都是这么说，然而对于酷 Q 这个情况，到这里是不行的，生成的 lib 可以通过链接，但酷 Q 无法加载。

于是我 dump 了这个生成的 lib 文件和酷 Q 官方 SDK 的 lib 文件，来看区别，发现了问题所在。

我生成的 lib：

```
Microsoft (R) COFF/PE Dumper Version 14.10.25019.0
Copyright (C) Microsoft Corporation.  All rights reserved.


Dump of file .\CQP.lib

File Type: LIBRARY

Archive member name at 8: /
591022E1 time/date Mon May  8 15:48:49 2017
         uid
         gid
       0 mode
     11E size
correct header end

    11 public symbols

      2C6 __IMPORT_DESCRIPTOR_CQP
      4E0 __NULL_IMPORT_DESCRIPTOR
      612 CQP_NULL_THUNK_DATA
      75C _CQ_addLog@16
      75C __imp__CQ_addLog@16
      7C2 _CQ_getAppDirectory@4
      7C2 __imp__CQ_getAppDirectory@4

......

String Table Size = 0x19 bytes

Archive member name at 75C: CQP.dll/
591022E1 time/date Mon May  8 15:48:49 2017
         uid
         gid
       0 mode
      2A size
correct header end

  Version      : 0
  Machine      : 14C (x86)
  TimeDateStamp: 591022E1 Mon May  8 15:48:49 2017
  SizeOfData   : 00000016
  DLL name     : CQP.dll
  Symbol name  : _CQ_addLog@16
  Type         : code
  Name type    : no prefix
  Hint         : 0
  Name         : CQ_addLog@16

Archive member name at 7C2: CQP.dll/
591022E1 time/date Mon May  8 15:48:49 2017
         uid
         gid
       0 mode
      32 size
correct header end

  Version      : 0
  Machine      : 14C (x86)
  TimeDateStamp: 591022E1 Mon May  8 15:48:49 2017
  SizeOfData   : 0000001E
  DLL name     : CQP.dll
  Symbol name  : _CQ_getAppDirectory@4
  Type         : code
  Name type    : no prefix
  Hint         : 1
  Name         : CQ_getAppDirectory@4

......
```

酷 Q 的 lib：

```
Microsoft (R) COFF/PE Dumper Version 14.10.25019.0
Copyright (C) Microsoft Corporation.  All rights reserved.


Dump of file .\CQP-Good.lib

File Type: LIBRARY

Archive member name at 8: /
558FB3E8 time/date Sun Jun 28 16:44:24 2015
         uid
         gid
       0 mode
     792 size
correct header end

    67 public symbols

      FAE __IMPORT_DESCRIPTOR_CQP
     11C8 __NULL_IMPORT_DESCRIPTOR
     12FA CQP_NULL_THUNK_DATA
     1444 _CQ_addLog@16
     1444 __imp__CQ_addLog@16
     14AA _CQ_getAppDirectory@4
     14AA __imp__CQ_getAppDirectory@4

......

String Table Size = 0x19 bytes

Archive member name at 1444: CQP.dll/
558FB3E8 time/date Sun Jun 28 16:44:24 2015
         uid
         gid
       0 mode
      2A size
correct header end

  Version      : 0
  Machine      : 14C (x86)
  TimeDateStamp: 558FB3E8 Sun Jun 28 16:44:24 2015
  SizeOfData   : 00000016
  DLL name     : CQP.dll
  Symbol name  : _CQ_addLog@16
  Type         : code
  Name type    : undecorate
  Hint         : 0
  Name         : CQ_addLog

Archive member name at 14AA: CQP.dll/
558FB3E8 time/date Sun Jun 28 16:44:24 2015
         uid
         gid
       0 mode
      32 size
correct header end

  Version      : 0
  Machine      : 14C (x86)
  TimeDateStamp: 558FB3E8 Sun Jun 28 16:44:24 2015
  SizeOfData   : 0000001E
  DLL name     : CQP.dll
  Symbol name  : _CQ_getAppDirectory@4
  Type         : code
  Name type    : undecorate
  Hint         : 1
  Name         : CQ_getAppDirectory

......
```

对比这两者，发现函数的「Symbol name」其实是没有问题的，问题出在「Name type」和「Name」，酷 Q 的 lib 文件，「Name type」都是 `undecorate`，「Name」也没有结尾的 `@` 加数字。

一开始我觉得可能是 `lib.exe` 的参数不太对，或者 def 文件写的不太对，于是搜了好久，尝试了各种方法，例如函数别名、删掉 `@`、使用 MinGW 的 `dlltool.exe` 等等，但无一例外没有什么用，使用函数别名只会在生成一个单独的函数描述，不会改变「Name type」，删掉 `@` 也就导致函数「Symbol name」不对，MinGW 的 `dlltool.exe` 更是似乎生成的结构完全不对（可能不兼容）。

当我准备放弃的时候，搜到了 [这篇](https://social.msdn.microsoft.com/Forums/vstudio/en-US/d5685e3d-a3f7-4268-9dfe-c7bc2f638972/important-undecorated-dll-import?forum=vcgeneral) 帖子，内心惊呼卧槽，这发帖人的描述就和我想要的情况一样啊！也是要让「Symbol name」带 `@` 而「Name」不带，虽然底下的回答没有什么有价值的信息，但发帖人倒是给出了一种办法——把函数描述区域的某个字节从 `0x08` 改成 `0x0C`。

于是用 Hex 编辑器查看了我生成的 lib 和酷 Q 的 lib 文件，找了一圈，找到了这个字节的位置，，并发现通过 `0x08 0x00 0x5F` 这个序列即可直接确定它们的位置，其中 `0x5F` 是下划线 `_`，也就是生成 lib 文件之后自动加的前缀，这样一来事情就简单很多，直接写一个脚本来替换即可：

```py
def fix_lib_file():
    with open('Some.lib', 'rb') as lib_f:
        binary = lib_f.read()

    binary = binary.replace(b'\x08\x00\x5f', b'\x0c\x00\x5f')

    with open('Some.lib', 'wb') as lib_f:
        lib_f.write(binary)
```

至此，修复之后的 lib 文件终于可以用了。

## 总结

这玩意折腾了我整整两天时间……不过时间也没有白费，最后也成功了，然后写了个完整的脚本来从 `.h` 头文件生成酷 Q `.lib` 文件，放在 [richardchien/coolq-cpp-sdk
](https://github.com/richardchien/coolq-cpp-sdk) 了。

## 参考资料

- [How to make a .lib file when have a .dll file and a header file
](http://stackoverflow.com/questions/9360280/how-to-make-a-lib-file-when-have-a-dll-file-and-a-header-file)
- [How To Create 32-bit Import Libraries Without .OBJs or Source](https://qualapps.blogspot.com/2007/08/how-to-create-32-bit-import-libraries.html)
- [Exporting from a DLL Using DEF Files](https://msdn.microsoft.com/en-us/library/d91k01sh.aspx)
- [Important: Undecorated DLL import](https://social.msdn.microsoft.com/Forums/vstudio/en-US/d5685e3d-a3f7-4268-9dfe-c7bc2f638972/important-undecorated-dll-import?forum=vcgeneral)
