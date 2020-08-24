---
title: 用 Octopress 在 GitHub 上搭建博客
updated: 2014-02-05
categories: Misc
tags: [Octopress, Blog]
---

## 1. Octopress 是什么

Octopress 官网给出的引言如下：

> First, I want to stress that Octopress is a blogging framework for hackers. You should be comfortable running shell commands and familiar with the basics of Git. If that sounds daunting, Octopress probably isn't for you.

意思是：首先，我想强调一下，Octopress 是为黑客而生的博客框架。你需要熟悉如何运行 shell 命令以及 Git 的一些基础知识。如果这些前提技能你听到就头疼，那么 Octopress 可能并不适合你。

其实，这个引言绝对有点夸张了，那么我的理解是，你只需要有一个经得起折腾的心脏和大脑，知道怎么在网上搜索，那么用 Octopress 就没什么问题。即使你没有它说的那些基础，只要照着步骤做就可以完成，甚至通过搭建博客这个过程，你会收获「熟悉如何运行 shell 命令以及 Git 的一些基础知识」这样一个结果，只要你肯动脑。

本教程适用于 Windows 和 OS X 系统。

<!-- more -->

## 2. 安装依赖程序（Windows）

使用 Windows 平台的话，需要安装的依赖程序较多。

首先把下面 4 个全下载好：

- [Git](https://msysgit.googlecode.com/files/Git-1.8.5.2-preview20131230.exe)
- [Ruby](http://dl.bintray.com/oneclick/rubyinstaller/rubyinstaller-1.9.3-p484.exe)
- [DevKit](https://github.com/downloads/oneclick/rubyinstaller/DevKit-tdm-32-4.5.2-20111229-1559-sfx.exe)
- [Python](http://www.python.org/ftp/python/2.7.5/python-2.7.5.msi)

注：如果这些链接失效你可以自行谷歌，很容易找到下载。

### 安装 Git

双击刚下载的 `Git-1.8.5.2-preview20131230.exe`，一路 Next。

### 安装 Ruby

同样一路 Next，不过要勾选「Add Ruby executables to your PATH」，将 Ruby 的执行路径加入到环境变量中，如果忘记勾选，也可以手动设置。安装完后可以在命令提示符中输入 `cd c:\` 进入 C 盘目录之后执行 `ruby –version` 来确认是否安装成功。

### 安装 DevKit

DevKit 下载下来的是一个自解压文件，我们将其解压到 `D:\DevKit`，当然也可以解压到其他目录，但有两点需要注意：

+ 解压目录中没有有中文和空格；
+ 必须先安装 Ruby，而且 Ruby 需要是 RubyInstallser 安装。

解压 DevKit 后，在命令行输入以下命令来进行安装：

```sh
d: #注意 Windows 的命令提示符中进入盘符要直接输入盘符
cd DevKit #进入文件夹用 cd 命令，教程后面将直接用 cd 来表示
ruby dk.rb init
ruby dk.rb install
```

### 安装 Python

安装 Python,也是一路 Next 就可以，博客的代码高亮用到了 Python 的 Pygments 模块，在 Python 中安装第三方库需要使用 `easy_install`，下载 [https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py](https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py)，下好后打开命令提示符，输入 `cd C:\Python27` 进入 Python 安装目录，然后再输入下面命令来安装 `easy_install`：

```sh
python PATH/ez_setup.py install
```

这里的 `PATH` 是你刚刚下载的 `ez_setup.py` 的保存位置。

安装好之后在 `C:\Python27\Scripts` 目录下可以看到 `easy_install.exe` 等文件，表示安装成功。

右击我的电脑，进入属性－高级系统设置－高级－环境变量，在用户变量下可以看到之前安装 Ruby 时它自动添加了一个名为 Path 的环境变量，双击它打开编辑窗口，在变量值的最后添加一个英文分号，在添加 `C:\Python27\Scripts`，完成后点几个确定关闭窗口，重新打开命令提示符输入 `echo %PATH%` 查看输出结果中有没有 `C:\Python27\Scripts`，有则表示设置成功。

在命令提示符中依次下面命令就可以安装 Pygments 了：

```sh
cd C:\Python27\Scripts
easy_install pigments
```

## 3. 安装依赖程序（OS X）

由于 OS X 是自带 Git 和 Python 的，所以只需要安装 Ruby。

### 安装 Ruby

首先在终端运行下面命令，来安装 RVM：

```sh
curl -L https://get.rvm.io | bash -s stable —ruby
```

接着顺次运行下面命令，来安装 Ruby 1.9.3：

```sh
rvm install 1.9.3
rvm use 1.9.3
rvm rubygems latest
```

完成后运行 `ruby —version`，不出意外的话这里就可以看到 `ruby 1.9.3` 安装好了。

## 4. 安装 Octopress

首先如果是 Windows 的话，在开始菜单找到 Git Bash 运行，输入 `cd d:` 来进入 D 盘（当然也可以换成其它路径），OS X 的话在终端同样可以用 `cd` 命令来进入指定目录，但默认的目录就可以了。

在终端／Git Bash 中运行下面命令：

```sh
git clone git://github.com/imathis/octopress.git octopress
```

接着在终端／命令提示符中使用 `cd` 命令进入刚才创建的 `octopress` 目录。使用下面命令安装相关依赖：

```sh
gem install bundler
bundle install
```

这两条命令可能需要不少时间，请耐心等待。在 OS X 上第二条命令执行时如果提示错误，可将第一条命令前面加 `sudo` 和空格，会提示输入密码从而获取超级用户权限。Windows 上并没有发现提示错误。

最后是安装默认 Octopress 主题：

```sh
rake install
```

这时候安装就完成了，如果你迫不及待的想看一下成果，就运行下面命令：

```sh
rake preview
```

然后在浏览器中输入 `localhost:4000` 来预览。

## 5. 配置 Octopress

整个框架的主要配置信息在 `octopress` 主目录的 `_config.yml` 文件中，这个文件中有三大部分，分别是 Main Configs、Jekyll & Plugins 和 3rd Party Settings。`url` 先不管，我们之后再填，先把 `title`、`subtitle` 和 `author` 冒号后面的内容改称你想要的，然后我们看到 3rd Party Settings，可以填写一些网站的账号，Twitter、Google Plus、Facebook 之类的如果你没有就可以删掉。关于这个文件里面更多的内容请看 [官方的帮助文档](http://octopress.org/docs/configuring/)。

然后就是主题，我们之前安装了默认的主题，但是如果你觉得太丑，是可以更换主题或者自己制作的，[这里](https://github.com/imathis/octopress/wiki/3rd-Party-Octopress-Themes) 有一些别人制作好的主题。安装主题的基本步骤如下：

```sh
cd octopress
git clone GIT_URL .themes/THEME_NAME
rake install['THEME_NAME']
rake generate
```

如果用 Windows 的话，这里的 `git` 命令是需要在 Git Bash 中运行的，后面的所有 `git` 命令也都要在 Git Bash 中才能运行，而其他命令在命令提示符运行，别忘了都要先 `cd` 到 `octopress` 目录。

安装好主题后，像之前说的，运行 `rake preview` 就可以在浏览器预览，如果你想自己调整主题，那就自己摸索吧。

有一个建议就是删掉 `/source/_includes/custom/head.html` 中的添加 Google 字体的代码，这样可以加快国内的访问速度。

Octopress 在 Windows 上存在中文编码问题，可以通过下面步骤解决：

- 在环境变量中添加下面的键值对：
```sh
LANG=zh_CN.UTF-8
LC_ALL=zh_CN.UTF-8
```
- 含有中文的文件需要保存为 UTF-8 无 BOM 格式编码。
- 在 Ruby 的安装路径找到文件 `convertible.rb`（`C:\Ruby193\lib\ruby\gems\1.9.1\gems\jekyll-0.12.0\lib\jekyll\convertible.rb`），将 `self.content = File.read(File.join(base, name))` 替换为：
```ruby
self.content = File.read(File.join(base, name), :encoding => ‘utf-8')
```

## 6. 添加新文章

现在博客基本上配置好了，但是还空空如也，正等着你去展示文采，所以下面来讲怎么添加新文章。

还是在终端／命令提示符，先用 `cd` 进入到 `octopress` 主目录，然后执行下面命令：

```sh
rake new_post[‘title’]
```

这里的 `title` 并不一定需要是文章的标题，它其实是生成的文件名的一部分，也是 URL 的一部分，尽量不要用中文。

命令执行后生成的文件在 `octopress/source/_post/` 目录中可以找到，这个文件的格式是 `markdown`，可以用文本编辑器打开，当然最好是找一款专门编辑 Markdown 文件的编辑器，Windows 推荐 MarkdownPad，OS X推荐 Mou。Markdown 是一种轻量级的标记语言，很容易学，甚至可以在需要时再去查询它的语法，可以在 [http://squidv.com/octopress-markdown/](http://squidv.com/octopress-markdown/) 查询。

这个文件的最上面几行是默认生成的，Octopress 框架通过它们来获取文章的标题、分类等属性，这里的 `title` 就是文章真正的标题，你可以按自己需要修改这几项属性。如果你想暂时不公开发表这篇文章，那么可以在这里添加一条属性 `published: false`，等你想公开发表的时候把 `false` 改称 `true` 就可以了。

文章写好后保存，然后执行：

```sh
rake generate
```

执行这个命令不需要关闭之前运行着 `rake preview` 命令的窗口，直接新建窗口运行该命令即可，生成完毕后，刚才的 `rake preview` 命令会自动更新内容，同样在浏览器中可以预览。

## 7. 发布到 GitHub

说了这么多，我们的博客别人看不到，那等于白忙，所以我们要把博客部署到 GitHub，至于 GitHub 是什么可以自己去维基百科了解。

在这里你需要在 [官网](https://github.com/) 注册一个 GitHub 账号，然后到个人页面在 Repositories 页面点「New」按钮新建一个仓库，仓库名称命名为 `username.github.io`，`username` 就是你的用户名，`README.md` 创不创建无所谓。我们的博客的源码将会放到这个仓库的 `source` 分支，而博客内容放在 `master` 分支，这个懂不懂没关系。

在 `_config.yml` 文件中的 `url` 后面填上 `http://username.github.io`，`username` 就是你的 GitHub 账户名。

在终端／Git Bash 执行下面命令：

```sh
rake setup_github_pages
```

按提示输入刚才创建的仓库地址。

完成后执行：

```sh
rake deploy
```

这个命令将会把博客内容 `commit` 并 `push` 到仓库的 `master` 分支，就像我们前面说的，博客内容在 `master` 分支。

如果这一步提示 `Permission denied(publickey)` 这类错误，请参考 GitHub 的官方帮助文档 [Generating SSH Keys](https://help.github.com/articles/generating-ssh-keys)，按其步骤生成 `SHH Key`，之后再从 `rake setup_github_pages` 命令开始重试。

现在已经可以通过 `username.github.io` 访问你的博客了（可能有较长时间的延迟，请一定要耐心等待）。

我们还需要把源码给放到仓库的 `source` 分支，依次执行下面命令：

```sh
git add .
git commit -am 'your commit message'
git push origin source
```

引号里面不限制内容，相当于对这次做的更改进行的备注。
教程到这其实基本结束了，如果你想学习更多内容，那么请看我的另一篇文章 [Octopress 搭建博客总结以及可选功能]()。
