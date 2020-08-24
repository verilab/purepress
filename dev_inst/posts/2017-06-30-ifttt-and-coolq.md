---
title: 真正零门槛：使用 IFTTT 和酷 Q 制作你的专属 QQ 通知机器人（不需要写任何代码！）
categories: [Play, Detailed]
tags: [IFTTT, 酷Q, QQ Bot, 聊天机器人]
created: 2017-06-30 11:40:00
is_draft: true
---

如标题所说，本教程是真正的零基础教程，你不需要会编程，也不需要对聊天机器人的原理有什么深刻的理解，你只需要一台装有 Windows 7 或更新版的电脑，然后照着教程做完，就可以做出一个可以说是有一定实用性的 QQ 通知机器人，比如通过 QQ 推送特定用户的新微博，推送 Tumblr 账号的更新（你懂的），定时推送天气预报或其它提醒。

虽然本教程的步骤看起来有点多，但每个步骤都会尽量写得简单易懂，并在适当的地方配上截图，所以照着教程操作的话，基本上不会有太大困难，请放心^_^

## 0. 一些简介

对于本文用到的一些服务、技术，你有可能会有些陌生，不要紧，这一节会首先给出一些基本的介绍，在后面用到的时候，也会一步一步教你使用。

### 0.1 什么是 IFTTT？

IFTTT 是一个国外的网络服务平台（[官网](https://ifttt.com/)），它提供的服务是通过接入网络上的各种其它平台的服务来触发一定的自定义操作，例如在发送微博时自动同步发送到 Twitter、当 iOS 上新增联系人时自动同步到 Google 联系人账号、每天早上 8 点发送当天的天气预报到社交网络等。可以看出它的服务可以概括为「当一件事情发生时，触发另一件事情」，这也正是 IFTTT 这个名字以及他们的口号「if this then that」的由来。

### 0.2 什么是酷 Q？

由于 QQ 官方并没有直接支持普通用户制作 QQ 机器人，因此要实现 QQ 机器人，通常需要使用一些方式来登录 QQ 机器人的账号，从而可以接受和自动发送消息。酷 Q 正是一种可以登录 QQ 号的软件（[官网](https://cqp.cc/)），并且向软件开发者提供一系列接收和发送消息的接口，不过在本教程中，你不需要知道这些接口是怎么工作的。

### 0.3 什么是内网穿透？

「内网穿透」是一种将没有公网 IP 的设备上的网络服务共享到公网的技术，简单来说，就是可以让互联网上其它设备访问你的电脑上的某个服务，本教程后面会使用内网穿透来将酷 Q 的接口暴露到公网，从而可以让 IFTTT 来触发，这听起来可能有点复杂，不过你并不需要知道这具体是怎么工作的，因为工具使用起来其实非常简单。

<!-- more -->

## 1. 安装酷 Q 和 HTTP API 插件

你可能要问了，刚刚不是就说了酷 Q 吗，这个 HTTP API 插件又是啥？不要慌，理论上讲，它是一个「把酷 Q 提供的接口转换到 HTTP」的插件，但这跟我们这个教程的主题没有什么主要关系，只需要简单安装一下就可以。

首先到酷 Q 官方论坛下载酷 Q Air，网址 [https://cqp.cc/t/23253](https://cqp.cc/t/23253)，我们这里选择「酷 Q Air 图灵版」：

![](https://ooo.0o0.ooo/2017/06/30/59560defc27dc.png)

你可以自行查看一下版本区别（实际上区别不大）。

下载之后直接解压：

![](https://ooo.0o0.ooo/2017/06/30/59560eae379a2.png)

`CQA.exe` 就是酷 Q 的主程序，先不急着运行，我们先前往 [https://github.com/richardchien/coolq-http-api/releases](https://github.com/richardchien/coolq-http-api/releases) 下载最新版本（比如目前最新版为图中的 v2.1.2）的 `io.github.richardchien.coolqhttpapi.cpk` 文件：

![](https://ooo.0o0.ooo/2017/06/30/59560f2f269b8.png)

这就是标题中所说的「HTTP API 插件」，下载好之后直接把它放到刚刚酷 Q 的 `app` 文件夹。

接着还不要急，再前往 [https://www.visualstudio.com/zh-hans/downloads/?q=redist](https://www.visualstudio.com/zh-hans/downloads/?q=redist) 下载安装 VC++ 2017 运行库，注意一定要选择「x86」：

![](https://ooo.0o0.ooo/2017/06/30/59560fdb10344.png)

装好之后，就可以运行 `CQA.exe` 了，首次启动会有如下提示：

![](https://ooo.0o0.ooo/2017/06/30/59561061dc430.png)

点确定即可到登录界面：

![](https://ooo.0o0.ooo/2017/06/30/5956108a6488f.png)

输入你要作为 QQ 机器人的 QQ 号和密码，登录，如果只是先尝试一下，还没有专门的号，就随便用一个小号登录吧，或者去 [https://ssl.zc.qq.com/chs/index.html](https://ssl.zc.qq.com/chs/index.html) 注册一个新的 QQ 号。

登录之后可以看到桌面上有一个悬浮窗：

![](https://ooo.0o0.ooo/2017/06/30/5956113ced448.png)

并且酷 Q 提示你进行一个互动式教程，你可以跟着教程玩一次，也可以选择「下次再说」。

然后右击悬浮窗，选择「应用」-「应用管理」进入插件管理界面：

![](https://ooo.0o0.ooo/2017/06/30/5956122cdda84.png)

![](https://ooo.0o0.ooo/2017/06/30/5956130960845.png)

如果你不想玩那个互动式教程，那么在这里最好选择「互动式教程」，并选择「停用」。然后选择「HTTP API」，并选择而「启用」，酷 Q 会提示你一些关于语音模块和插件权限的问题，全选「是」即可。完成之后 HTTP API 插件即启用了，可以右击悬浮窗，选择「日志」，查看是否有输出「HTTP API 插件已启用」。

到目前为止，酷 Q 这边的操作已经全部做完，现在你的 QQ 机器人已经在线了，不过它还没有功能，你可以先在浏览器中打开 `http://127.0.0.1:5700/send_private_msg?user_id={你的QQ号}&message=主人你好` 来测试酷 Q 及 HTTP API 插件是否正常运行，其中 `{你的QQ号}` 要换成你的 QQ 号。如果一切 OK，你的机器人会给你发送一条消息「主人你好」。

## 2. 配置内网穿透

这一步对于没有什么计算机基础知识的同学来说可能看起来非常可怕，但其实本质上是非常简单的。

我们这里使用一个叫「魔法隧道」的服务来配置内网穿透，首先去 [官网](http://www.mofasuidao.cn/) 注册一个账号，然后进入「控制中心」：

![](https://ooo.0o0.ooo/2017/06/30/595615d487769.png)

![](https://ooo.0o0.ooo/2017/06/30/5956163080ff1.png)

我这里已经开了一个隧道，所以下面可以看到已经有一个项。你需要点击上面的加号来创建隧道，「地域」随便选，「隧道名称」随便填，「隧道协议」选「http+https」，「IP 地址和端口」填 `127.0.0.1:5700`，二级域名不用填，然后点「立即创建」即可创建成功。

![](https://ooo.0o0.ooo/2017/06/30/595616ac7c5e4.png)

创建完成之后，去 [http://www.mofasuidao.cn/rest/page/download](http://www.mofasuidao.cn/rest/page/download) 下载魔法隧道的客户端，如果你不知道你的系统是多少位，就下「32 位」即可。

下好之后直接就是一个 `mofasuidao.exe`，先不急着点开，先打开记事本，然后粘贴下面的代码：

```
CreateObject("WScript.Shell").Run "C:\Users\richard\Desktop\mofasuidao.exe xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",1
```

这里的 `C:\Users\richard\Desktop\mofasuidao.exe` 要换成你刚刚下载的 `mofasuidao.exe` 所在的路径，然后 `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` 替换成你创建的魔法隧道给出的 token：

![](https://ooo.0o0.ooo/2017/06/30/595618a14f4c3.png)

然后把这个文件随便保存到一个地方，命名为 `mofasuidao.vbs`，注意后缀是 `.vbs`，记事本默认可能是 `.txt` 需要改一下：

![](https://ooo.0o0.ooo/2017/06/30/59561a1d518f7.png)

上面那段代码是用来快速启动魔法隧道客户端的，你不需要知道它具体在干什么。现在双击 `mofasuidao.vbs` 会打开一个黑的命令行窗口，稍等片刻当你看到窗口上显示有「suidaoStat online」时，即表示启动成功：

![](https://ooo.0o0.ooo/2017/06/30/59561af80d884.png)

这个时候，找到魔法隧道给你的隧道域名：

![](https://ooo.0o0.ooo/2017/06/30/59561b74c3fec.png)

在后面加上 `/send_private_msg?user_id={你的QQ号}&message=主人你好`，然后到浏览器打开，就像前面的 `http://127.0.0.1:5700/send_private_msg?user_id={你的QQ号}&message=主人你好` 一样，只不过变成了 `http://xxxx.mofasuidao.cn/send_private_msg?user_id={你的QQ号}&message=主人你好`

如果还是一切 OK，此时你的机器人应该会又给你发了一条消息。

至此内网穿透就配置好了，那个命令行窗口关闭即可关闭魔法隧道客户端，再次打开也是运行 `mofasuidao.vbs`。

## 3. 配置 IFTTT

前往 IFTTT 官网 [https://ifttt.com/](https://ifttt.com/) 注册一个账号并登录，进入账号的「Settings」页面：

![](https://ooo.0o0.ooo/2017/06/30/5956293eea7ac.png)

往下滚动修改时区为北京：

![](https://ooo.0o0.ooo/2017/06/30/5956297914de6.png)

然后前往 [Maker Webhooks](https://ifttt.com/maker_webhooks)，点击「Connect」，之后可以看到如下页面：

![](https://ooo.0o0.ooo/2017/06/30/5956259563990.png)

右上角有「Settings」表示已经成功开启 Maker Webhooks。

然后进入「My Applets」页面：

![](https://ooo.0o0.ooo/2017/06/30/5956264ae85e3.png)

我们马上就要开始创建核心功能了。

下面提供了两个示例玩法，你可以任选或都选，当然这两个不是所有的可能，更多有趣的玩法还要你自己去发掘。

### 3.1 自动推送每天的天气预报

首先进入「Services」页面，找到并进入「Weather Underground」，点右上角「Settings」进入服务设置页面：

![](https://ooo.0o0.ooo/2017/06/30/59562fa8b5eaa.png)

然后点「Edit connection」，在跳转到的页面中搜索（用拼音）并选择你需要关注天气的城市，然后点「Connect」。

然后回到「My Applets」，点击「New Applet」，再点「this」：

![](https://ooo.0o0.ooo/2017/06/30/59562e72080a8.png)

搜索并选择「Weather Underground」服务：

![](https://ooo.0o0.ooo/2017/06/30/59562e918e64a.png)

然后选择「Today's weather report」，并设定推送时间：

![](https://ooo.0o0.ooo/2017/06/30/59562f0548591.png)

然后点击「Create trigger」。

继续点「that」，搜索并选择「Maker Webhooks」：

![](https://ooo.0o0.ooo/2017/06/30/595631f18ffbb.png)

选择「Make a web request」，「URL」填写 `http://xxxx.mofasuidao.cn/send_private_msg`，这里的 `xxxx.mofasuidao.cn` 替换成魔法隧道给你的隧道域名，「Method」选「POST」，「Content Type」选「application/x-www-form-urlencoded」，「Body」填：

```
user_id={你的QQ号}&message=<<<今天最高气温 {{HighTempCelsius}}°C，最低气温 {{LowTempCelsius}}°C，现在气温 {{CurrentTempCelsius}}°C>>>
```

这里 `{你的QQ号}` 换成你要接收推送的 QQ 号（必须是机器人号的好友），`<<<` 和 `>>>` 中的内容也就是推送内容，可以自由修改，点击「Add ingredient」可以添加你想要的其它天气信息，注意所有内容一定都要在 `<<<>>>` 中间，且内容中不能出现其它尖括号。填写完如下：

![](https://ooo.0o0.ooo/2017/06/30/595633f04526c.png)

最后点「Create action」、「Finish」大功告成，可以等着在你指定的时间收到推送啦！不过注意这个推送可能会有些许延迟，属于正常现象。

### 3.2 新微博 QQ 提醒

首先在浏览器打开要通知到 QQ 的微博用户的主页，我们以薛之谦的微博为例：[http://weibo.com/xuezhiqian]()，然后按 F12 进入「开发者工具」，进入「控制台」标签，在下方的文本框中粘贴如下代码并回车：

```js
/uid=(\d+)/. exec(document.querySelector('.opt_box .btn_bed').getAttribute('action-data'))[1]
```

![](https://ooo.0o0.ooo/2017/06/30/59563599a0d75.png)

可以看到输出了一串数字：

![](https://ooo.0o0.ooo/2017/06/30/595635dbdc1df.png)

将这个数字复制出来，先暂时保存起来（或者页面先不要关）。

然后点 IFTTT 的「New Applet」，点「this」，找到并选择「RSS Feed」：

![](https://ooo.0o0.ooo/2017/06/30/595636579025c.png)

然后点击「Connect」（如果出现的话），接着选择「New feed item」，在「Feed URL」中填写：

```
https://api.prprpr.me/weibo/rss/{微博博主的uid}
```

其中 `{微博博主的uid}` 换成刚刚在微博用户主页输出的那串数字：

![](https://ooo.0o0.ooo/2017/06/30/5956370f68766.png)

然后点「Create trigger」创建。

继续点「that」，搜索并选择「Maker Webhooks」：

![](https://ooo.0o0.ooo/2017/06/30/595631f18ffbb.png)

选择「Make a web request」，「URL」填写 `http://xxxx.mofasuidao.cn/send_private_msg`，这里的 `xxxx.mofasuidao.cn` 替换成魔法隧道给你的隧道域名，「Method」选「POST」，「Content Type」选「application/x-www-form-urlencoded」，「Body」填：

```
user_id={你的QQ号}&message=<<<薛之谦又发段子了，去微博看看吧 {{EntryUrl}}>>>
```

这里 `{你的QQ号}` 换成你要接收推送的 QQ 号（必须是机器人号的好友），`<<<` 和 `>>>` 中的内容也就是推送内容，可以自由修改，不过注意所有内容一定都要在 `<<<>>>` 中间，且内容中不能出现其它尖括号。填写完如下：

![](https://ooo.0o0.ooo/2017/06/30/595639164556c.png)

最后点「Create action」、「Finish」大功告成，等薛之谦发微博之后，你在 QQ 上就可以收到机器人的推送了！

不过，这个玩法的延迟比较高，在发出微博后，大约需要等 5 到 10 分钟左右才会收到推送，不过也不错啦～

## 4. 特别提醒

**需要注意的一点是，IFTTT 的这些推送生效的前提条件是，酷 Q 和魔法隧道客户端都一直在运行，假设你设置了上午 7 点推送，要能够正确收到推送，这个时间点，你的酷 Q 和 魔法隧道必须是运行着的。**

通常情况下，建议使用一台可以长期开机不关闭的电脑来运行酷 Q 和魔法隧道。当然你也可以把酷 Q 和魔法隧道添加到开机启动，对于酷 Q，首先右击悬浮窗，在你的账号那个选项中，勾选「快速登录」，提示是否创建快捷方式，选「是」，然后将这个快捷方式加入开机启动，对于魔法隧道，直接将 `mofasuidao.vbs` 加入开机启动。

## 5. 锦上添花

上面的示例全都是发送推送给自己，当然也是可以发送到 QQ 群的，只需要把「Make a web request」中填写的「URL」的 `send_private_msg` 换成 `send_group_msg`，并把「Body」中的 `user_id={你的QQ号}` 换成 `group_id={群号}` 就行了。

另外，IFTTT 所支持的大部分服务都是国外的，例如 Facebook、Twitter、Instagram 等，如果你也玩这些社交网站的话，那么可以搞出的功能就更多了，总之更多功能还看你的创造力。

最后，如果你有一些编程基础的话，甚至可以在「Make a web request」中不直接调用发送消息的接口，而是 POST 代码到一些在线运行代码的网站（例如 [https://compiler.run/](https://compiler.run/)），在这个代码中再去执行更复杂的逻辑，然后再 POST 到发消息的接口，这样自由度将会更大（当然你也可以让 IFTTT 直接 POST 到你自己的服务端）。

总之将 IFTTT 和酷 Q 搭配起来会是一种非常有趣的玩法，可以创造很多可能性，而且整个过程不需要自己配置服务器运行环境。

如果觉得光推送通知太无聊的话，也可以启用酷 Q 的图灵机器人插件，还记得当时我们下载的是图灵版吗，在「应用管理」中找到「图灵机器人」，启用，然后点「菜单」-「设置」，根据他的提示申请一个图灵机器人的 API Key 并填入，就可以获得聊天自动回复功能了。另外，图灵机器人的网站上也提供了一些有趣的自定义的途径，同样可以发挥你的创造力来做不一样的聊天机器人。
