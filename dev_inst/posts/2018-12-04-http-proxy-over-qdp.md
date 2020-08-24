---
title: 基于 QDP 协议实现 HTTP 代理
categories: [Dev]
tags: [QDP, 代理, HTTP代理, 通信协议, QQ, 酷Q, CQHTTP]
created: 2018-12-04 21:21:00
---

## 动机

简单实现了 QDP 之后，想通过这个协议寻求对计算机网络一些知识的深入学习，通过跟朋友们的交流，知道了可以通过实现 TUN/TAP 虚拟网络设备来兼容现有的 TCP/IP 协议栈，这是一个有趣的方向，不过还是打算先验证一下自己最开始的想法，也就是基于 QDP 实现一个 HTTP 代理，算是学习和实践一下 HTTP 代理的原理吧。

## 思路

根据 [HTTP 代理原理及实现（一）](https://imququ.com/post/web-proxy.html)，HTTP 代理的原理，分为两种：第一种，浏览器将请求直接发送给 HTTP 代理，后者将 HTTP 请求转发给服务端（以客户端的身份），随后再将服务端的响应转发给浏览器（以服务端的身份）；第二种，浏览器通过 `CONNECT` 方法请求代理建立一条隧道，通过该隧道转发 TCP 数据。

QDP 协议在这个实验中的作用，实际上是用于在「与浏览器通信的本地 HTTP 代理」（后面称此为「代理前端」）和「用于转发请求到真实目标站点的伪客户端」（后面称此为「代理后端」）之间传输数据，从而让真实的流量通过 QQ 消息传送。

由于 QDP 被用在代理程序的两个部分之间的通信，因此还需要设计一种数据交换协议（实际上是一种 RPC）（后面称此为「代理协议」）来作为 QDP 的有效载荷。

到这里，从思路上来说，整个工作流程已经比较清晰了：代理前端开放 HTTP 代理端口，接受浏览器的代理请求，然后进行必要的处理，再通过代理协议，把必要的数据和指令发送给代理后端，后者根据这些数据和指令，向代理请求的实际目标网站发起连接，并继续通过代理协议在代理前端和目标网站之间转发数据。

## 实现

第一步首先根据 Jerry Qu 的博客内容来实现一个正常的 HTTP 代理，源码见 [demo/http_proxy.py](https://github.com/richardchien/qdp/blob/master/demo/http_proxy.py)。这一步遇到了一些坑，最后因为没有适当的第三方 HTTP 库，转而直接使用 asyncio 自带的流 API，也算是粗糙地实现了。

接着就是要把代理的前端和后端拆开。

先设计它们的通信协议（上面说的代理协议），为了简便起见，直接使用 JSON 来定义：

```json
{
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "method": "connect",
    "params": {
        "host": "www.example.com",
        "port": 443
    }
}
```

```json
{
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "method": "transfer",
    "params": {
        "data": "<base64 encoded bytes>"
    }
}
```

```json
{
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "method": "close",
    "params": {}
}
```

上面的 `id` 字段是 UUID，用于唯一标识一个代理请求。`method` 字段定义了代理协议的三个方法，分别是 `connect`、`transfer`、`close`，这三个方法是通过分析先前实现的 HTTP 代理所进行的操作得来的，首先代理前端需要通知后端连接目标站点（使用 `connect` 方法），然后两端需要互相转发数据（使用 `transfer` 方法），最后请求完成后还需要关闭连接（使用 `close` 方法）。`params` 字段是相应方法所需的参数。

有了代理协议之后，就可以开始分别实现代理前端和代理后端了。

代理前端非常简单，直接在正常的 HTTP 代理的代码上修改。接受代理请求的部分不用动，当需要建立连接的时候，向代理后端发送 `connect` 协议包；然后当从代理请求的连接中读取数据之后，使用 `transfer` 协议包向代理后端发送数据，与此同时，当后端发来数据（同样是 `transfer` 方法）时，从中读取数据并转发给代理请求方（浏览器）。源码见 [demo/http_proxy_frontend.py](https://github.com/richardchien/qdp/blob/master/demo/http_proxy_frontend.py)。

代理后端不能直接从正常的 HTTP 代理代码修改，需要写一些新的逻辑，主要就是不断地接收代理前端发来的协议包，如果是 `connect`，就开启一个协程，向目标网站建立连接，然后不断接收对应 `id` 的协议包，如果是 `transfer` 则转发，`close` 则关闭，实际代码不是很多。源码见 [demo/http_proxy_backend.py](https://github.com/richardchien/qdp/blob/master/demo/http_proxy_backend.py)。

上面代码虽然说起来简单，但实际编写的时候还是经历了一些艰难的 debug 的……由于代码量不算非常多，就没怎么加注释了，阅读起来应该不会很困难。

## 效果

编写代码时代理前后端都是跑在本地的，测试成功后，将后端和其对应的 QQ 移到阿里云上海的某个 VPS，成功运行，访问 `ip.cn` 来验证 IP 地址确实已经是阿里云上海的地址：

![](https://i.loli.net/2018/12/04/5c067d3f8deb1.png)

从上图的 DevTools 可以看出，这个代理的速度基本上慢到不可用了（本来 QDP 就已经足够慢了，现在代理协议又需要占用额外的空间），但作为一个概念验证已经足够了。

## 参考资料

- [HTTP 代理原理及实现（一）](https://imququ.com/post/web-proxy.html)
- [Streams (coroutine based API)](https://docs.python.org/3.5/library/asyncio-stream.html)
