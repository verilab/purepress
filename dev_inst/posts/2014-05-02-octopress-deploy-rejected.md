---
title: Octopress 博客 deploy 失败的解决办法
categories: Misc
tags: [Octopress, Blog]
---

参考资料：[rake gen_deploy rejected in Octopress](http://stackoverflow.com/questions/17609453/rake-gen-deploy-rejected-in-octopress)

今天在新系统里面设置 `octopress` 的时候遇到一个问题，就是 `rake deploy` 总是失败，有形如下面的错误提示：

```sh
 ! [rejected]        master -> master (non-fast-forward)
error: failed to push some refs to 'git@github.com:richardchien/richardchien.github.io.git'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart. Integrate the remote changes (e.g.
hint: 'git pull ...') before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
```

经过各种搜索，似乎是远程仓库和本地的代码不一致，需要强行把本地的内容 `push` 到远程仓库，解决办法如下：

在 `octopress` 文件夹找到 `Rakefile` 文件，打开，找到 `system "git push origin #{deploy_branch}"` 这一行，改成 `system "git push origin +#{deploy_branch}"`，然后再执行 `rake deploy` 就可以成功了，之后远程仓库的代码就和本地一致了，然后把 `Rakefile` 文件改回原来的 `system "git push origin #{deploy_branch}"`，就 OK 了。
