---
title: 树莓派上手三天总结
categories: Misc
tags: [Raspberry Pi, Linux]
---

7 月 25 日，伴随着一点冲动，就下单买了最新的树莓派 B+ 以及入门必备的一些配件，26 日下午送到，就开始了这三天的折腾。

## 1. 启动

首先要启动，到 [树莓派官网](http://www.raspberrypi.org/downloads) 下载最新的固件，我下载的是 `Raspbian June 2014` 版本，下载好是 `zip` 文件，解压得到 `img` 镜像文件。然后要把 `img` 文件写入到 SD 卡里面。方法如下：

- 在 Windows 上可以用一个叫 Win32DiskImager 的软件（[这里下载](http://sourceforge.net/projects/win32diskimager/)），这个软件用起来超简单，只需要选好 `img` 文件和要写入的 SD 卡盘符，点「Write」等它写入完就可以了。
- 在 OS X 上比 Windows 要麻烦一点，先用 `df -h` 命令查看当前挂载的卷，找到 SD 卡的分区对应的设备文件，如 `/dev/disk1s1`，然后用 `diskutil unmount /dev/disk1s1` 将这些分区卸载，再执行 `diskutil list`，记住 SD 卡对应的设备文件，如 `/dev/disk1`，然后用 `dd bs=4m if=2014-06-20-wheezy-raspbian.img of=/dev/rdisk1` 来写入镜像文件，当然 if 和 of 指向的地址都要改成你自己的，这个命令执行的时候没有提示，就卡住不动，一定要耐心等待，写入好了之后就会提示你。

于是装有 Raspbian 的 SD 卡就制作完成了，插到树莓派里，插上网线，接上电源，树莓派就会开机，如果有显示器，就从 HDMI 接口接过去就有显示了，不过据说如果要 HDMI 转 VGA 的话，千万不能用没有自带电源的转换线，一定要用自带电源接口的。当然我这里没有 HDMI 转 VGA 线，也没有 HDMI 接口的显示器，这种情况下要想连接到树莓派可以通过 SSH。

<!-- more -->

## 2. 远程登录

Raspbian 系统默认是开启 SSH 的，也就是说它一开机你就可以用 SSH 连接它，SSH 需要提供系统的用户名和密码，Raspbian 默认用户名是 `pi`，密码是 `raspberry`。到路由器网页，一般默认是 `192.168.1.1`，找到树莓派分配到的 IP 地址，记下待用。

* Windows 上连 SSH 可以用 PuTTY（[官网下载](http://www.putty.org)），图形界面，操作简单，填上树莓派的 IP 地址，其他默认，点打开，然后按照提示输入账号密码登录，这里如果告诉连不上，可以稍微等一会儿再试试。
* OS X 上可在终端连接 SSH，用 `ssh pi@192.168.10.106` 命令，当然换成你的树莓派的 IP，如果不出意外，会提示你输密码，然后就会登录成功，再次强调**不出意外**，OS X 上这一步似乎经常容易出意外，有时候树莓派重启后如果分配到了不同于上次的 IP，这边就会登录不上，提示没有访问权限，好像是 `SSH Key` 的问题，但是一直没搞清楚。

登录成功后，树莓派就到嘴边了。

## 3. 配置

不过要先稍微配置一下，先 `sudo raspi-config` 命令进入一个比较简陋的配置界面，选择「Expand Filesystem」，这样会把整个系统的可用空间扩充到储存卡的大小，据说不扩充的话，多余的空间用不了，不过我没尝试。扩充完成后会提示你重启，回车重启。

然后电脑上的 SSH 连接就断了（这句废话）。

过个几十秒，再一次 SSH。

执行 `ping baidu.com` 试试看能不能连上网（一定要 ping 百度哈哈，这已经是百度存在的大部分意义了）。

我个人感觉是最好设置个静态 IP，就像之前说的 OS X 上面好像如果树莓派换 IP 的就会出问题，所以还是设置个静态 IP 靠谱。`sudo vi /etc/network/interfaces` 进入网络接口配置文件（我看了好多教程，里面大部分都是用 `nano` 来编辑文件，不知为何，我感觉还是 `vi` 用着顺手，我是装了个 `vim`，`sudo apt-get install vim` 可安装 `vim`），把 `iface eth0 inet dhcp` 中的 `dhcp` 改成 `static`，并在这行下面加上四行：

```sh
address 192.168.10.123
netmask 255.255.255.0
gateway 192.168.10.1
dns-nameservers 192.168.10.1
```

IP 地址和网关要换成你自己的，网关填路由器地址，DNS 域名服务器也填路由器地址好了，改好后保存退出。

## 4. 远程桌面

`sudo apt-get install tightvncserver` 命令安装 `vncserver`，安装成功后 `vncpasswd` 命令设置一个密码，然后执行 `vncserver :1 -geometry 800x600` 即可启动 1 号桌面，同理 `:2` 就是 2 号桌面，后面的 `-geometry 800x600` 就是设置分辨率。这个地方其实直接 `vncserver` 命令就好了，不加参数就是默认启动 1 号桌面，分辨率 1024x768。

电脑上下载 VNC Viewer（[官网下载](http://www.realvnc.com/download/viewer/)），下好打开输入树莓派 IP 地址及桌面号，形如 `192.168.10.123:1`，点「Connect」，之后输入密码即可登录，`vncserver -kill :1` 命令可关闭 1 号桌面，不常用。

要让 1 号桌面开机启动，先 `sudo vi /etc/init.d/tightvncserver` 创建一个新文件，把下面内容复制进去：

```sh
#!/bin/sh
### BEGIN INIT INFO
# Provides:          tightvncserver
# Required-Start:    $local_fs
# Required-Stop:     $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start/stop tightvncserver
### END INIT INFO
# More details see:
# http://www.penguintutor.com/linux/tightvnc
### Customize this entry
# Set the USER variable to the name of the user to start tightvncserver under
export USER=’pi’
### End customization required
eval cd ~$USER
case ”$1” in
  start)
    # 启动命令行。此处自定义分辨率、控制台号码或其它参数。
    su $USER -c ’/usr/bin/tightvncserver -geometry 800x600 :1’
    echo ”Starting TightVNC server for $USER ”
    ;;
  stop)
    # 终止命令行。此处控制台号码与启动一致。
    su $USER -c ’/usr/bin/tightvncserver -kill :1’
    echo ”Tightvncserver stopped”
    ;;
  *)
    echo ”Usage: /etc/init.d/tightvncserver {start|stop}”
    exit 1
    ;;
esac
exit 0
```

保存退出。

再执行下面两行命令：

```sh
sudo chmod 755 /etc/init.d/tightvncserver
sudo update-rc.d tightvncserver defaults
```

不过……话说，上面的方法我试了，但每次开机并没有自动启动桌面，不过很简单啦，在 `/etc/rc.local` 文件里面加上一行 `vncserver :1 -geometry 800x600` 就是开机启动了。

## 5. 更改键盘布局及语言和地区

因为树莓派是英国产的嘛，所以默认键盘布局是英国的，于是有些符号你会发现打不出来，所以我们要换成美式键盘。

`sudo raspi-config` 进入配置界面，选「International」，进去后再选「Change Keyboard」，进入后，找到「Generic 104-key PC」（说到这里的`104-key`，我看了两个教程，一个说 101，一个说 105，于是我数了一下我的键盘，是 104 个键，于是就选了 104），回车确定进入「Keyboard layout」，放眼望去全是「UK」，所以选「Other」，进去后找到「English(US)」（可能要翻不少页才能找到），回车确定，然后再选「English(US, alternative international)」，然后一路 OK，退出后，重启系统（如果你不知道重启的命令的话……Google 去吧）即可。这里说是要重启系统，不过我没重启的时候就已经可以正常用了。

然后还要改一个地区，同样是 `sudo raspi-config` 进入配置界面，选「International」，然后「Change Locale」，去掉「en\_GB.UTF-8 UTF-8」，勾上「en\_US.UTF-8 UTF-8」、「zh\_CN.UTF-8 UTF-8」和「zh\_CN.GBK GBK」，空格键是打勾或取消勾，Tab 键跳到 Ok 按钮，回车进入下一页，然后就是选系统默认语言了，我选了「en\_US.UTF-8」，貌似如果选「zh\_CN.UTF-8」那么桌面就是中文界面（虽然这样真的很奇怪）。至于中文输入法，反正我还没装，据说一个叫 Scim 的输入法不错，`sudo apt-get -y install scim-pinyin` 可安装，要加装五笔则再执行 `sudo apt-get -y install scim-tables-zh`。

## 6. 总结

先写这么多，都是把别人的教程里面可用的部分拿过来的，本文的参考资料在下面，后面有空的话，再写一篇关于那几个配件的。

## 7. 参考资料

- [树莓派无显示器上手步骤](http://ltext.tumblr.com/post/49580927299)
- [mac 下给树莓派安装 raspbian 系统](http://zhangshenjia.com/it/raspberry_pi/mac-raspbian/)
- [树莓派(raspberry pi)学习4: 更改键盘布局](http://blog.csdn.net/c80486/article/details/8460271)
- [Raspbian 系统中文化（中文支持、中文字体、中文输入法）](http://bbs.shumeipai.org/thread-80-1-1.html)
