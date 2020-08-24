---
title: 使用 Nginx 反向代理 Google 和 Wikipedia
categories: Ops
tags: [Nginx, Google, Wikipedia, 反向代理]
created: 2018-10-23 10:04:00
---

对于程序员来说，能够通过一些途径上 Google、Wikipedia 等网站是非常必要的，但对于一些初学者来说，上这些网站还是有一些阻碍，因此尝试通过反代来让他们在内网中轻松访问这些网站。

<!-- more -->

## 准备

只需要有一台在墙外的 VPS，如果还有一个域名则更好。

## 安装／重新编译 Nginx

反代 Google 和 Wikipedia 需要 Nginx 安装有 [ngx_http_substitutions_filter_module] 模块，因此如果之前安装的 Nginx 在编译时没有添加这个模块，是需要重新编译的。

[ngx_http_substitutions_filter_module]: https://github.com/yaoweibin/ngx_http_substitutions_filter_module

如果没有安装 Nginx，先使用发行版自带的包管理器安装一个 Nginx。

然后通过：

```bash
nginx -V
```

查看 Nginx 版本，例如 `nginx version: nginx/1.10.3`，然后下载相应版本的 Nginx 源码：

```bash
wget http://nginx.org/download/nginx-1.10.3.tar.gz
tar zxf nginx-1.10.3.tar.gz
```

然后下载 ngx_http_substitutions_filter_module 模块：

```bash
git clone https://github.com/yaoweibin/ngx_http_substitutions_filter_module
```

接着安装编译所必需的包（这里以 Ubuntu 为例）：

```bash
apt-get update
apt-get install -y libpcre3 libpcre3-dev zlib1g zlib1g-dev openssl libssl-dev libxml2 libxml2-dev libxslt1-dev libgd-dev libgeoip-dev gcc g++ make automake
```

然后进入 Nginx 源码目录，利用 `nginx -V` 输出的 `configure arguments`，在最后加上 `--add-module=../ngx_http_substitutions_filter_module` 来运行 `./configure` 并编译，例如（具体参数需要换成你系统中的）：

```bash
cd nginx-1.10.3
./configure --with-cc-opt='-g -O2 -fPIE -fstack-protector-strong -Wformat -Werror=format-security -Wdate-time -D_FORTIFY_SOURCE=2' --with-ld-opt='-Wl,-Bsymbolic-functions -fPIE -pie -Wl,-z,relro -Wl,-z,now' --prefix=/usr/share/nginx --conf-path=/etc/nginx/nginx.conf --http-log-path=/var/log/nginx/access.log --error-log-path=/var/log/nginx/error.log --lock-path=/var/lock/nginx.lock --pid-path=/run/nginx.pid --http-client-body-temp-path=/var/lib/nginx/body --http-fastcgi-temp-path=/var/lib/nginx/fastcgi --http-proxy-temp-path=/var/lib/nginx/proxy --http-scgi-temp-path=/var/lib/nginx/scgi --http-uwsgi-temp-path=/var/lib/nginx/uwsgi --with-debug --with-pcre-jit --with-ipv6 --with-http_ssl_module --with-http_stub_status_module --with-http_realip_module --with-http_auth_request_module --with-http_addition_module --with-http_dav_module --with-http_geoip_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_image_filter_module --with-http_v2_module --with-http_sub_module --with-http_xslt_module --with-stream --with-stream_ssl_module --with-mail --with-mail_ssl_module --with-threads --add-module=../ngx_http_substitutions_filter_module
make
make install
```

然后将编译出来的二进制覆盖系统中已安装的：

```bash
cp -rf objs/nginx /usr/sbin/nginx
```

再重启 Nginx：

```bash
systemctl stop nginx
systemctl start nginx
```

## 使用 ZeroTier 组建虚拟网络

ZeroTier 用于组建一个虚拟的内网，安装和配置非常简单，见 [ZeroTier](https://www.zerotier.com/download.shtml)。

这一步其实不是必须的，但是在公网发布 Google 的反向代理是极其危险的行为，建议还是仅内部使用。

## 使用 acme.sh 签发 SSL 证书

如果需要通过域名访问反代站点，则需要先准备好 SSL 证书，现在 [Let's Encrypt] 已经提供免费的证书，可通过 [acme.sh] 比较简单地签发。

[Let's Encrypt]: https://letsencrypt.org/
[acme.sh]: https://github.com/Neilpang/acme.sh

具体签发方法见 acme.sh 的 [文档](https://github.com/Neilpang/acme.sh/wiki/说明)。

## 配置反向代理

添加一个 Nginx 站点配置文件，并启用：

```bash
touch /etc/nginx/sites-available/google-wikipedia
ln -s /etc/nginx/sites-available/google-wikipedia /etc/nginx/sites-enabled/
```

然后编辑 `/etc/nginx/sites-available/google-wikipedia`，内容如下：

> 注意：
>
> - `<google.domain>` 和 `<wikipedia.domain>` 等需要改成你自己的域名，不包含 `https://`，如果你没有域名，而是打算直接使用 IP，则需要把下面配置中放在 `443` 端口中的配置移动到 `80` 端口配置中，并且无法使用 HTTPS
>
> - `<ip>` 需要改成你的 VPS 在 ZeroTier 网络中的 IP，如果你不使用 ZeroTier，则需要改成你需要监听的 IP，或直接连同端口前的冒号一起删除

```
upstream www.google.com {
    # 这里的 IP 是写此文时可用的 IP，具体需要使用 nslookup 来查看
    server 172.217.0.4:443 weight=1;
    server 172.217.1.36:443 weight=1;
    server 216.58.193.196:443 weight=1;
    server 216.58.194.196:443 weight=1;
    server 216.58.195.196:443 weight=1;
    server 216.58.216.4:443 weight=1;
    server 216.58.216.36:443 weight=1;
    server 216.58.219.36:443 weight=1;
    server 172.217.6.36:443 weight=1;
}

server {
    listen <ip>:80;
    server_name <google.domain> <wikipedia.domain> <m.wikipedia.domain> <upload.wikipedia.domain>;
    return 301 https://$host$request_uri;
}

server {
    listen <ip>:443 ssl;
    server_name <google.domain>;
    resolver 8.8.8.8;

    ssl on;
    ssl_certificate /root/.acme.sh/<google.domain>/fullchain.cer;
    ssl_certificate_key /root/.acme.sh/<google.domain>/<google.domain>.key;

    # 如果服务跑在公网，则可能需要解除下面的注释，以确保不会被搜索引擎收录，以及下面维基百科的 server 配置也需要添加下面这些
    #if ($http_user_agent ~* "qihoobot|Baiduspider|Googlebot|Googlebot-Mobile|Googlebot-Image|Mediapartners-Google|Adsbot-Google|Feedfetcher-Google|Yahoo! Slurp|Yahoo! Slurp China|YoudaoBot|Sosospider|Sogou spider|Sogou web spider|MSNBot|ia_archiver|Tomato Bot") {
    #    return 403;
    #}

    access_log  off;
    error_log   on;
    error_log  /var/log/nginx/google-proxy-error.log;

    location / {
        proxy_redirect off;
        proxy_cookie_domain google.com <google.domain>;
        proxy_pass https://www.google.com;
        proxy_connect_timeout 60s;
        proxy_read_timeout 5400s;
        proxy_send_timeout 5400s;

        proxy_set_header Host "www.google.com";
        proxy_set_header User-Agent $http_user_agent;
        proxy_set_header Referer https://www.google.com;
        proxy_set_header Accept-Encoding "";
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Accept-Language "zh-CN";
        proxy_set_header Cookie "PREF=ID=047808f19f6de346:U=0f62f33dd8549d11:FF=2:LD=en-US:NW=1:TM=1325338577:LM=1332142444:GM=1:SG=2:S=rE0SyJh2W1IQ-Maw";

        subs_filter https://www.google.com.hk https://<google.domain>;
        subs_filter https://www.google.com https://<google.domain>;
        subs_filter //zh.wikipedia.org //<wikipedia.domain>;

        sub_filter_once off;
    }
}

server {
    listen <ip>:443 ssl;
    server_name <upload.wikipedia.domain>;

    ssl on;
    ssl_certificate /root/.acme.sh/<wikipedia.domain>/fullchain.cer;
    ssl_certificate_key /root/.acme.sh/<wikipedia.domain>/<wikipedia.domain>.key;

    access_log  off;
    error_log   on;
    error_log  /var/log/nginx/wikipedia-proxy-error.log;

    location / {
        proxy_pass https://upload.wikimedia.org;
    }
}

server {
    listen <ip>:443 ssl;
    server_name <wikipedia.domain>;

    ssl on;
    ssl_certificate /root/.acme.sh/<wikipedia.domain>/fullchain.cer;
    ssl_certificate_key /root/.acme.sh/<wikipedia.domain>/<wikipedia.domain>.key;

    access_log  off;
    error_log   on;
    error_log  /var/log/nginx/wikipedia-proxy-error.log;

    location / {
        proxy_cookie_domain zh.wikipedia.org <wikipedia.domain>;
        proxy_pass https://zh.wikipedia.org;
        proxy_redirect https://zh.wikipedia.org/ https://<wikipedia.domain>/;
        proxy_redirect https://zh.m.wikipedia.org/ https://<m.wikipedia.domain>/;
        proxy_connect_timeout 60s;
        proxy_read_timeout 5400s;
        proxy_send_timeout 5400s;

        proxy_set_header Host "zh.wikipedia.org";
        proxy_set_header User-Agent $http_user_agent;
        proxy_set_header Referer https://zh.wikipedia.org;
        proxy_set_header Accept-Encoding "";
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Accept-Language "zh-CN";

        subs_filter_types text/css text/html text/xml text/javascript application/javascript application/json;
        subs_filter //zh.wikipedia.org //<wikipedia.domain>;
        subs_filter upload.wikimedia.org <upload.wikipedia.domain>;
    }
}
```

上面示例中并没有配置 `m.wikipedia.domain`，实际上和 `wikipedia.domain` 是几乎一样的。

配置完成后通过 `nginx -t` 检查是否有错误，如果没错，通过 `systemctl restart nginx` 重启 Nginx 即可生效。

## 参考资料

- [Nginx 反向代理 Google 配置](http://einverne.github.io/post/2017/10/nginx-reverse-proxy-google.html)
- [利用Nginx反向代理谷歌](https://zhgcao.github.io/2016/06/09/nginx-reverse-proxy-google/)
- [维基百科镜像制作全解析](https://io.hancel.org/2017/01/06/make-wiki-mirror.html)
