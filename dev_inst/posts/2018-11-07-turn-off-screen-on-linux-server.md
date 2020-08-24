---
title: 在笔记本上使用 Proxmox（或其它 Linux 服务器版）时关闭屏幕
categories: Ops
tags: [Linux, Proxmox]
created: 2018-11-07 23:22:00
---

给吃灰许久的 12 年款 MacBook Pro 装了个 Proxmox 玩玩，发现启动后屏幕一直亮着，提示登录，搜了一圈找到 AskUbuntu 上有个同样的问题，[这个答案](https://askubuntu.com/a/1076734) 完美的解决了问题：

```sh
setterm --blank 1
```

这条命令的效果是，不操作一分钟后自动关闭屏幕。

另外，一直开着盖子，键盘上会落灰，盖上之后发现机子掉线了，也搜了一下，发现 [这个答案](https://askubuntu.com/a/594417) 完美解决了问题：

修改 `/etc/systemd/logind.conf` 中的

```sh
#HandleLidSwitch=suspend
```

为

```sh
HandleLidSwitch=ignore
```

然后

```sh
service systemd-logind restart
```

之后合盖就不会睡眠了。
