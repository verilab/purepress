---
title: 用 Let's Encrypt 免费签发 SSL 证书
updated: 2016-06-04
categories: Ops
tags: [SSL, Let's Encrypt]
---

昨天尝试给博客加上了 SSL，用的 [Let's Encrypt](https://letsencrypt.org/)，这玩意可以免费签发有效期 90 天的 SSL 证书，使用也挺简单的，这里总结一下。

## 安装 Let's Encrypt

```sh
git clone https://github.com/certbot/certbot
cd certbot
./certbot-auto
```

第一次执行 `./certbot-auto` 会安装各种依赖环境，会比较慢。

如果你用的是 Apache，那么直接 `./certbot-auto --apache` 就会全自动配置，中间会提示你选择需要开启 SSL 的站点之类的。如果你用的是其它服务器软件或者需要手动获取证书，看下面。

## 获取 SSL 证书

这里只讨论 [Manual 模式](https://letsencrypt.readthedocs.org/en/latest/using.html#manual)。

首先要把需要签证书的域名解析到当前服务器的 IP，这里以 `ssl.r-c.im` 演示，然后运行 `./certbot-auto certonly --manual -d ssl.r-c.im`，这里 `ssl.r-c.im` 换成要签的域名，也可以同时签多个域名，只需要加多个 `-d` 选项，如 `./certbot-auto certonly --manual -d ssl.r-c.im -d ssl2.r-c.im`。

<!-- more -->

耐心等待，这里可能需要等较长时间，直到出现下图这样：

![image](https://o33x5shzt.qnssl.com/16-2-26/88763450.jpg)

选「Yes」，然后会出现类似于下面这样的内容：

```
Make sure your web server displays the following content at
http://ssl.r-c.im/.well-known/acme-challenge/7huixD-nddpR3c0T6aKt_MXqrpox4brEU4yA2rLNOIY before continuing:

7huixD-nddpR3c0T6aKt_MXqrpox4brEU4yA2rLNOIY.j0H7Twj9gLcy7RfbIMiW1qBaOJNa88UfRKlp0D96CaI

If you don't have HTTP server configured, you can run the following
command on the target server (as root):

mkdir -p /tmp/letsencrypt/public_html/.well-known/acme-challenge
cd /tmp/letsencrypt/public_html
printf "%s" 7huixD-nddpR3c0T6aKt_MXqrpox4brEU4yA2rLNOIY.j0H7Twj9gLcy7RfbIMiW1qBaOJNa88UfRKlp0D96CaI > .well-known/acme-challenge/7huixD-nddpR3c0T6aKt_MXqrpox4brEU4yA2rLNOIY
# run only once per server:
$(command -v python2 || command -v python2.7 || command -v python2.6) -c \
"import BaseHTTPServer, SimpleHTTPServer; \
s = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \
s.serve_forever()"
Press ENTER to continue
```

这里需要进行进行 ACME Challenge，按它的提示，如果已有 HTTP 服务器就确保 `http://ssl.r-c.im/.well-known/acme-challenge/7huixD-nddpR3c0T6aKt_MXqrpox4brEU4yA2rLNOIY` 这个路径返回的内容是 `7huixD-nddpR3c0T6aKt_MXqrpox4brEU4yA2rLNOIY.j0H7Twj9gLcy7RfbIMiW1qBaOJNa88UfRKlp0D96CaI`，如果没有就用 Python 临时搭一个（直接复制它给的命令运行即可）。

HTTP 服务器配置好之后，按回车继续，等它验证通过即获得了 SSL 证书，默认放在了 `/etc/letsencrypt/live/ssl.r-c.im/` 目录下。如果后面证书到期了只需要重新进行这一步即可。

## 在 Nginx 上配置 SSL

新建配置文件如下：

```
server {
    listen 80;
    server_name ssl.r-c.im;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443;
    server_name ssl.r-c.im;

    ssl                  on;
    ssl_certificate      /etc/letsencrypt/live/ssl.r-c.im/fullchain.pem;
    ssl_certificate_key  /etc/letsencrypt/live/ssl.r-c.im/privkey.pem;

    ssl_session_timeout  5m;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers on;

    ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA';

    location / {
        ...
    }
}
```

这里把 HTTP 的请求重定向到了 HTTPS，当然你也可以不这么做，配置完运行 `nginx -s reload` 即可。
