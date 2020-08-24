---
title: 更换电脑或多台电脑同时使用 Octopress
categories: Misc
tags: [Octopress, Blog]
---

如果你的电脑上的 Octopress 文件夹被误删了，或者你换电脑了，或者你想在多台电脑上同时都可以写博客，那么本教程将教你如何解决。

下面内容翻译自 [Clone Your Octopress to Blog From Two Places](http://blog.zerosharp.com/clone-your-octopress-to-blog-from-two-places/#disqus_thread)。

## 重新创建本地 Octopress 仓库

下面的内容将教你如何为已有的 Octopress 博客重新创建本地目录结构。

<!-- more -->

### 将你的博客克隆到新设备

首先你需要将仓库的 `source` 分支克隆到本地的 `octopress` 文件夹。

```sh
git clone -b source git@github.com:username/username.github.com.git octopress
```

然后将 `master` 分支克隆到 `_deploy` 子文件夹。

```sh
cd octopress
git clone git@github.com:username/username.github.com.git _deploy
```

接着运行 rake 安装命令来完成配置。

```sh
gem install bundler
rbenv rehash # If you use rbenv, rehash to be able to run the bundle command
bundle install
rake setup_github_pages
```

它会提示你输入仓库的 URL。

```sh
Enter the read/write url for your repository
(For example, 'git@github.com:your_username/your_username.github.com')
```

到这里你就成功地将 Octopress 博客拷贝到了本地。

### 从两个不同设备推送变更

如果你想在多台电脑上写博客，你需要确保在切换电脑之前把所有变更的内容都推送到 GitHub。即，在切换前，一旦变更了内容，就要执行下面命令：

```sh
rake generate
git add .
git commit -am "some comment here."
git push origin source #更新远程仓库的 source 分支
rake deploy            #更新远程仓库的 master 分支
```

接着，切换到另一台电脑后，你需要拉取之前推送的改变。

```sh
cd octopress
git pull origin source #更新本地仓库的 source 分支
cd ./_deploy
git pull origin master #更新本地仓库的 master 分支
```

当然如果把 Octopress 安装到U盘的话部署会更简单。
