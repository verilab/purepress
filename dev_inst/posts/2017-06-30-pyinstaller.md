---
title: 使用 PyInstaller 将 Python 程序打包成无依赖的可执行文件
categories: [Dev]
tags: [Python, PyInstaller]
created: 2017-06-30 10:30:00
---

本文以 Windows 为例，其它系统上应该坑会更少一点。

## 安装

首先一点，截至目前（17 年 6 月），PyInstaller 还不兼容 Python 3.6，根据官方的说明，目前支持的版本是 2.7 和 3.3 到 3.5。当你看到这篇文章时，可能已经支持更新版本了，建议查看官方 repo 的 README：[pyinstaller/pyinstaller](https://github.com/pyinstaller/pyinstaller)。

用 pip 安装：

```sh
pip install pyinstaller
```

在 Windows 上，pip 会同时安装 pypiwin32 包，这是 PyInstaller 在 Windows 上的一个依赖。

这里就有了第一个坑，根据 [Requirements](http://pyinstaller.readthedocs.io/en/stable/requirements.html#windows)：

> It requires either the PyWin32 or pypiwin32 Python extension for Windows.

理论上应该默认情况下安装了 pypiwin32 就可以运行的，但其实并不行，直接用的话会报错 `ImportError: DLL load failed: The specified module could not be found.`。

根据 [#1840](https://github.com/pyinstaller/pyinstaller/issues/1840) 这个 issue，再安装个 PyWin32 就可以了。

前往 [Python for Windows Extensions](https://sourceforge.net/projects/pywin32/files/)，点进 `pywin32` 目录里面的最新 build，找到对应当前 Python 版本的 exe，下载安装。

## 使用

比如我们现在有一个脚本文件 `main.py`，要将它打包成可执行文件，直接运行：

```sh
pyinstaller -F main.py
```

这将会在 `main.py` 所在目录下生成一些其它目录，最终的可执行文件就在 `dist` 目录中。这条命令中 `-F` 表示生成单个可执行文件，如果不加 `-F`，则默认生成一个目录，其中除了可执行文件，还包括其它依赖文件。

总体来说用起来是非常简单的，不过在打包使用了 requests 包的程序时，出现了 `ImportError: No module named 'queue'` 的报错，发现 [这里](https://www.zhihu.com/question/53717334) 也有遇到了同样的问题。

这个问题只需要在打包时加入 `--hidden-import` 参数即可：

```sh
pyinstaller -F --hidden-import queue main.py
```

更多用法请参考 [Using PyInstaller](http://pyinstaller.readthedocs.io/en/stable/usage.html)。
