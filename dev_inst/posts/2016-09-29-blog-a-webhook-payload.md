---
title: BlogA 添加 Webhook 回调的支持
categories: Misc
tags: [BlogA, Webhook, Backend]
---

刚刚给 BlogA 支持了 Webhook 回调，其实也就是开了一个支持 POST 的 URL 然后去执行自定义脚本而已。

因为之前把博客的内容和 BlogA 框架本身分离了，内容放在 [richardchien/blog-content](https://github.com/richardchien/blog-content)，然后 BlogA 跑在 docker，后台用脚本每 100 秒 pull 一次，不过这样还是有一种很不爽的感觉，于是这次直接加了 Webhook 回调，在 GitHub 添加一个 Webhook 然后在发生 push 时通知 BlogA，从而执行我的更新博客内容的脚本，这样看起来要清爽很多。

所以这篇就算水完了……主要算是测试一下效果。
