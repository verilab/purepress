---
title: 把博客迁移到 VeriPress 了
categories: Misc
tags: [Blog, VeriPress]
---

好几天前就写好了 [VeriPress](https://github.com/veripress/veripress) 的初始版本（说初始版本是因为有一些功能在写之前就打算放在第二版来实现，不过目前看来，这个就当个 flag 好了……），一直没空把自己博客迁移过来，刚刚抽空把 VPS 全整理了一下，然后终于迁移了博客。

不得不说我之前真的蠢，竟然直接拿 Flask 的 `run()` 来跑，这次是用 uWSGI 和 nginx 跑的 Flask 的 app 对象，并开启了 HTTP/2 支持。

不过由于新的 VeriPress 和原来的 BlogA 在给评论框提供文章的唯一标识不一样了，原来的 Disqus 评论在新的上也就看不到了，虽然 Disqus 官方有一个迁移工具，但我想本来也没有几个评论，也就不折腾了吧，况且 Disqus 被墙了，感觉其实不是一个好的选择，就先这样吧。

再说一下我现在跑 VeriPress 的方法，首先在 VPS 用 virtualenv 来安装，VeriPress 实例放在主目录，然后通过 uWSGI 指定 virtualenv 的路径和工作目录，文章和页面在本地电脑上保存，写新文章之后用 sftp 同步到 VPS。这样整个流程基本上用起来还算舒服，缺点就是需要手动同步文章等数据，但现在实在懒得配置 GitHub 的 webhook 来自动更新了。

其实还是非常想后面有空给 VeriPress 加上数据库存储支持的，同时加上后台管理页面，这样也就不用费心同步文件了。

另外就是博客主题，由于不是很有空，就先用着之前写的默认主题了，后面有机会要重新写个好一点的主题。

嗯，来数数这篇文章里一共立了多少 flag。
