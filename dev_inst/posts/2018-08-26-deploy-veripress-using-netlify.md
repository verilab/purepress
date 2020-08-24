---
title: 使用 Netlify 部署 VeriPress
categories: Misc
tags: [Blog, VeriPress, Netlify]
created: 2018-08-26 14:14:00
---

博客好久没更新，最近突然想重整一下，于是重新写了个 [主题](https://github.com/richardchien/veripress-theme-light)，样式是抄的以前 LiveChat 的官方博客的样式（现在他们的博客已经不长这样了）。

然后之前把博客迁移到 GitHub Pages，用 [VeriPress](https://github.com/veripress/veripress) 的 `generate` 命令生成之后 push 到 GitHub，现在觉得还是有点麻烦，从 [VuePress](https://vuepress.vuejs.org/) 那边学到了部署到 [Netlify](https://www.netlify.com/) 这招，就想着能不能把 VeriPress 也部署到 Netlify，后来折腾了一下发现可行。

首先需要看 VeriPress 生成静态文件的步骤（已经创建 instance 目录的情况下）：

```bash
veripress theme install theme-name
veripress generate
```

这里安装主题这一步是必须的，所以导致 VeriPress 最少也需要两行命令，再加上主题允许自定义的 `custom` 目录，实际可能需要更多命令才能完成静态文件的生成，于是考虑用一个 shell 脚本，这样在 Netlify 那边的 build 命令就只需要填写 `bash build.sh` 就行了，我的 `build.sh` 如下：

```bash
#!/usr/bin/env bash

veripress theme install richardchien/veripress-theme-light --name light

theme=`python -c "import config; print(config.THEME)"`
rm -rf ./themes/$theme/templates/custom
cp -R ./theme-custom ./themes/$theme/templates/custom

veripress generate --app-root=/
```

然后再添加两个文件 `runtime.txt`：

```
3.6
```

和 `requirements.txt`：

```
veripress
```

分别告诉 Netlify 运行所需的 Python 版本和依赖项。

最后去 Netlify 添加站点，build command 填 `bash build.sh`，publish directory 填 `_deploy` 就可以了。

以后写博客只需要将 VeriPress 实例的目录整个 push 到 GitHub（我忽略了 `themes` 目录），之后 Netlify 会自动生成静态文件然后部署，可以说非常棒了～
