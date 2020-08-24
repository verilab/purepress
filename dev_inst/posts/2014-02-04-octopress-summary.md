---
title: Octopress 搭建博客总结以及可选功能
categories: Misc
tags: [Octopress, Blog]
---

## 1. 总结

写博客基本步骤如下：

```sh
# 创建新文章
rake new_post[‘title’]

# 编辑 Markdown 文件

# 生成静态页面
rake generate

# 在本地预览
rake preview

# 发布到 GitHub
rake deploy

# 将修改的源码推送到 source 分支
git add .
git commit -am 'your commit message'
git push origin source
```

## 2. 添加新页面（可选）

添加一个新页面其实和添加文章一样简单，同样是在终端／命令提示符，`cd` 进去 `octopress` 目录之后，执行下面命令：

```sh
rake new_page[super-awesome]
```

或

```sh
rake new_page[super-awesome/page.html]
```

两条命令都会在 `source` 目录创建一个 `super-awesome` 文件夹，差别在于，上面的命令创建的目录里面有一个 `index.markdown` 文件，访问它的链接为 `root_url/super-awesome/`，后者创建的目录里面是 `page.html`，访问方式 `root_url/super-awesome/page.html`，当然如果你输入的是 `super-awesome/index.html` 那么也是可以通过 `root_url/super-awesome/` 访问的。

新创建的页面采用的页面布局是 `page`，如果你仔细观察的话，会发现之前创建的文章的页面布局是 `post`，页面布局的HTML在 `source/_layouts` 目录中，有能力的话可以自行修改布局。

<!-- more -->

## 3. 添加评论框（可选）

评论框见的比较多的是 Disqus 和多说。

如果要添加 Disqus 评论框，那只需要有账号，然后在 `_config.yml` 文件里面填上 `disqus_short_name` 就可以了。

如果要添加多说评论框，那么除了账号还需要做些别的事：

在 `_config.yml` 文件中添加下面内容：

```yaml
# Duoshuo Comments
duoshuo_comments: true
duoshuo_short_name: yourname
```

在 `source/_layouts/post.html` 中添加下面代码：

```html
{% if site.duoshuo_short_name and site.duoshuo_comments == true and page.comments == true %}
  <section>
    <h1>Comments</h1>
    <div id="comments" aria-live="polite">{% include post/duoshuo.html %}</div>
  </section>
{% endif %}
```

在 `source/_includes/post/` 目录新建 `duoshuo.html`，并添加下面内容：

```html
<!-- Duoshuo Comment BEGIN -->
<div class="ds-thread"></div>
<script type="text/javascript">
  var duoshuoQuery = {short_name:"yourname"};
  (function() {
    var ds = document.createElement('script');
    ds.type = 'text/javascript';ds.async = true;
    ds.src = 'http://static.duoshuo.com/embed.js';
    ds.charset = 'UTF-8';
    (document.getElementsByTagName('head')[0]
    || document.getElementsByTagName('body')[0]).appendChild(ds);
  })();
</script>
<!-- Duoshuo Comment END -->
```

上面所有代码里的 `yourname` 都要换成你自己的多说 `shortname`。

然后只要执行总结的 3、5、6 步骤就可以了。

## 4. 添加分享按钮（可选）

方法跟添加评论框的大同小异，如下：

在 `_config.yml` 文件中添加下面内容：

```yaml
# Jia This Share
weibo_share: true
```

在 `source/_includes/post/sharing.html` 中添加下面内容：

```html
{% if site.weibo_share %}
     {% include post/weibo.html %}
{% endif %}
```

在 `source/_includes/post/` 目录新建 `weibo.html`，然后在 [加网](http://www.jiathis.com/) 获取分享按钮的代码，把代码添加到 `weibo.html` 中。

同样执行总结的 3、5、6 步骤就可以了。

## 5. 绑定独立域名（可选）

如果你有自己的域名，给你的博客绑定一个独立域名是很不错的选择。GitHub 支持指定顶级域名或二级域名。

不管绑定什么域名，需要在 `source` 目录新建一个没有扩展名的文件 `CNAME`，在里面填上一行你要绑定的域名，保存之后发布到 GitHub。

接着，如果你要绑定顶级域名比如 `example.com`，那么在你的 DNS 中添加一条 A 记录，主机记录填 `@`，记录值填 `204.232.175.78`。

如果你要绑定二级域名比如 `sub.example.com`，那么在你的 DNS 中添加一条 CNAME 记录，主机记录填你想要的二级域名如 `sub`，记录值填 `username.github.io`。

这样你的域名就和博客绑定好了。（DNS 有时会有较长延迟，请耐心等待）

## 6. 添加百度统计或 Google Analytics

添加百度统计：从百度统计获取代码，然后添加到文件 `source/_includes/after_footer.html` 文件中。

添加 Google Analytics：从 Google Analytics 获取跟踪 ID，然后将这个 ID 添加到 `_config.yml` 文件的 `google_analytics_tracking_id` 后面。
