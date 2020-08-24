---
title: 情人节要到了，手把手教你写个 QQ 机器人给女朋友玩
categories: [Dev, Detailed]
tags: [酷Q, QQ Bot, Mojo-Webqq, HTTP API]
---

其实 QQ 机器人写起来很简单的，对于本教程中使用的 QQ 机器人框架，你需要一点点 C/C++ 基础，或者了解其它任何语言的 HTTP 库（开启 HTTP 服务端、发起 HTTP 请求两种）的使用。

## QQ 机器人框架简介

也就是对 QQ 协议分析之后封装出来的一个完整的 QQ 客户端及开发框架，通过对这个客户端的事件的处理和接口的调用，即可实现诸如自动回复、主动通知等功能。

目前网上各种机器人框架很多，本教程主要以 [酷 Q](https://cqp.cc/) 和 [Mojo-Webqq](https://github.com/sjdy521/Mojo-Webqq) 为例。

这两个框架差别还是蛮大的：酷 Q 是闭源的，使用 Android QQ 协议，似乎是易语言写的，只能在 Windows 上跑（最新版本也支持在 Wine 里面跑），且必须在图形界面操作，官方提供易语言和 C++ 的 SDK；Mojo-Webqq 是开源的，使用 SmartQQ 协议，用 Perl 写的，全平台基本都能跑，比较方便用脚本来自动化，官方提供 Perl 的接口以及 HTTP 接口。

另外，酷 Q 由于是 Android QQ 协议，要比 SmartQQ 稳定很多，且可以接收图片、语音等。

这两者的差别还有很多，可以分别去看它们的文档。

下面分别讲如何使用这两个客户端框架来编写简易的 QQ 机器人。

<!-- more -->

## 使用酷 Q 开发（C/C++）

酷 Q 这玩意官方似乎是比较建议用易语言来写插件的，然而易语言这坑，我反正是不想进……

所以这里用它的 C++ SDK 来写，如果你不会 C/C++，可以直接跳到下个标题，通过 HTTP 接口来开发。

### 安装酷 Q

好现在开始，首先在 [https://cqp.cc/](https://cqp.cc/) 下载最新版的酷 Q Air，下载下来是 zip 包，直接解压就能运行。其实酷 Q 的图灵版和小 i 版都是自带了 AI 的插件的，可以去 [图灵机器人](http://www.tuling123.com/) 或 [小 i 机器人](http://cloud.xiaoi.com/) 注册获得一个 API Key，就可以直接自动 AI 回复了。这里主要讲如何自己开发。

如果没用过酷 Q，可以先走一遍它的首次启动教程。

### 写点 C/C++

官方的 C++ SDK 是直接给了一个 demo 工程，直接在 [这里]([https://github.com/CoolQ/cqsdk-vc](https://github.com/CoolQ/cqsdk-vc)) 下载完整的工程目录，然后用 Visual Studio 打开，一般情况下基本上可以直接编译成功的。

然后就可以开始写了，其实这个 demo 工程里面注释给的也基本上很清楚。

对于一个自动回复的机器人来说，我们主要需要关注的是 `appmain.cpp` 文件，这个文件就是用来处理接收到的酷 Q 事件的（比如私聊消息、群组消息、群成员变动等等），主要视需求修改 `__eventGroupMsg`、`__eventGroupMsg`、`__eventDiscussMsg` 这三个事件的处理代码。

然后还需要看一下 `cqp.h` 这个文件，这里声明了酷 Q 的 C++ 接口，发送消息、处理请求等就是通过调用这里声明的函数来实现。

通过这些就可以开始实现一些简单的功能了，比如要让机器人直接重复对方发的内容，代码如下：

```cpp
/*
* Type=21 私聊消息
* subType 子类型，11/来自好友 1/来自在线状态 2/来自群 3/来自讨论组
*/
CQEVENT(int32_t, __eventPrivateMsg, 24)(int32_t subType, int32_t sendTime, int64_t fromQQ, const char* msg, int32_t font)
{
    //如果要回复消息，请调用酷Q方法发送，并且这里 return EVENT_BLOCK - 截断本条消息，不再继续处理  注意：应用优先级设置为"最高"(10000)时，不得使用本返回值
    //如果不回复消息，交由之后的应用/过滤器处理，这里 return EVENT_IGNORE - 忽略本条消息
    CQ_sendPrivateMsg(ac, fromQQ, msg);
    return EVENT_IGNORE;
}
```

`__eventPrivateMsg` 事件的几个参数含义分别是：

- `subType`：消息子类型，见注释；
- `sendTime`：消息发送时间的 Unix 时间戳；
- `fromQQ`：发送者的 QQ 号；
- `msg`：收到的消息内容；
- `font`：字体……我也不知道这有啥用；

上面代码通过调用 `CQ_sendPrivateMsg(ac, fromQQ, msg);` 即可把消息原样发送出去了，其中 `ac` 是酷 Q 授权码，在 `Initialize` 事件里获得，每个接口都需要传入这个授权码才能调用。

编译成功后会得到一个 `.dll` 文件，把它和工程目录下面那个 `.json` 文件一起放到酷 Q 的 app 文件夹里面，并且在 conf 文件夹的 `CQP.cfg` 文件里加上如下配置：

```ini
[Debug]
DeveloperMode=1
```

这时候重启酷 Q 就可以看到刚刚自己的插件了。

限于篇幅这里只给出这个示例了，如果你有一些 C/C++ 基础的话就可以对消息内容字符串进行匹配、请求网络数据、构造回复内容等等。但是我突然觉得就这么一个简单的示例可能也没啥用，你可以看一下这几个文档：[Pro/开发/快速入门](http://d.cqp.me/Pro/%E5%BC%80%E5%8F%91/%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8)、[Pro/开发](http://d.cqp.me/Pro/%E5%BC%80%E5%8F%91)、[酷Q机器人开发笔记（C++）](https://cqp.cc/t/28730)。注意一个坑，就是事件参数中的 `msg` 是 GBK 编码的，你可能需要转换到 UTF-8 才能正常处理，可以看一下 [这里](https://github.com/richardchien/coolq-http-api/blob/master/src/encoding.cpp) 的实现。

## 使用酷 Q 开发（任意语言）

说实话用 C++ 开发插件，还是太累了（当然如果你说你会易语言，那当我没说……），而且必要性也不是很大，你说一个 QQ 机器人要啥性能呢……

然后我写了个 [CoolQ HTTP API 插件](https://github.com/richardchien/coolq-http-api)，于是就可以用其它语言来开发插件了。如果你喜欢酷 Q 的稳定以及更多的功能，又不想用易语言或 C++ 开发插件，那么你可以尝试用用这个 HTTP API 插件。

### 安装 HTTP API 插件

在 [这里](https://github.com/richardchien/coolq-http-api/releases) 下载最新的 cpk 文件放到酷 Q 的 app 文件夹，然后重启酷 Q，启用插件，然后插件会在 `app\io.github.richardchien.coolqhttpapi` 目录下生成一个默认的 `config.cfg` 配置文件，然后开了一个 HTTP 服务端监听 `0.0.0.0:5700`。

### 编写实际的插件功能

启用插件之后你就可以通过请求 `http://192.168.1.100:5700/send_private_msg` 来调用酷 Q 的发送私聊消息的功能，其它功能也都和这个类似。

你还需要用你想用的语言开启一个 HTTP 服务端，用来接收 HTTP API 插件的消息、事件上报（POST 请求），然后把 URL 填到 `config.cfg` 配置文件的 `post_url` 配置项，比如 `post_url=http://192.168.1.200:8888`。

然后就可以写逻辑了。

我们这里以 Python 为例（我只会 Python……）给出一个重复消息内容的 demo：

```python
import requests
from flask import Flask
from flask import request as flask_req

app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    data = flask_req.json or {}
    if data.get('post_type') == 'message' and data.get('message_type') == 'private':
        requests.post('http://192.168.1.100:5700/send_private_msg', json={
            'user_id': data.get('user_id'),
            'message': data.get('message')
        })
    return '', 204


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
```

这里从收到的上报消息（JSON 格式）里取出 `post_type` 和 `message_type` 判断消息类型为私聊消息，然后发送 POST 请求到 `http://192.168.1.100:5700/send_private_msg`，以 JSON 传入参数，其实也可以用 GET 请求通过 URL 参数传入，或者 POST 请求通过 url-encoded-form 传入。

另外，所有传递的数据全都是 UTF-8 编码。

总之通过这个插件可以直接使用其它几乎任何语言来编写插件了，要写更复杂的功能你可能还需要阅读 [CoolQ HTTP API 插件文档](https://richardchien.github.io/coolq-http-api/)。

## 使用 Mojo-Webqq 开发（任意语言）

[Mojo-Webqq](https://github.com/sjdy521/Mojo-Webqq) 是用 Perl 编写的，你可以直接用 Perl 写插件，同时它也支持通过 HTTP 来上报消息事件和调用接口，因此也可以用几乎任意语言来写。

另外这个是运行在命令行的，因此相比酷 Q 更方便进行自动化部署（不过它需要扫码登录，毕竟改变不了是 SmartQQ 的事实……）。

### 运行 Mojo-Webqq

安装和运行 Mojo-Webqq 的方法可以看它的 [文档](https://github.com/sjdy521/Mojo-Webqq#安装方法)，写的非常清晰（这也是 Mojo-Webqq 的一个很大的优点之一，另外遇到问题还可以加入它的交流群提问，作者人还是很不错的）。

一般情况下如果只是简单的跑个小机器人，Windows 上直接用它官方给的打包好的 [Mojo-StrawberryPerl](https://github.com/sjdy521/Mojo-StrawberryPerl) 就行了，修改一下它的 `mojo_webqq.pl` 里的 `$post_api` 即可，其它配置基本上不用改。使用 [Docker](https://github.com/sjdy521/Mojo-Webqq/blob/master/Docker.md) 来运行也是一种比较建议的办法，基本上可以一条命令运行起来。

###  编写实际的插件功能

同样还是用 Python 为例，同样写一个重复消息内容的 demo：

```python
import requests
from flask import Flask
from flask import request as flask_req

app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    data = flask_req.json or {}
    if data.get('post_type') == 'receive_message' and data.get('type') == 'friend_message':
        requests.post('http://192.168.1.100:5000/openqq/send_friend_message', data={
            'uid': data.get('sender_uid'),
            'content': data.get('content')
        })
    return '', 204


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
```

实际上这跟上面的「使用酷 Q 开发（任意语言）」标题下的代码几乎一样，基本上只有数据的字段名不太一样。

总的来说还是很简单的，要深入了解的话，可以看它的 [API](https://github.com/sjdy521/Mojo-Webqq/blob/master/API.md) 文档。

## 最后

好了，简单的示例都给完了，就看各位老司机的发挥了。现在问题来了，我的女朋友呢？
