---
title: 利用 JSONP 实现跨站请求的方法及原理
categories: Dev
tags: [JSONP, JavaScript, Frontend, Backend, 跨站请求]
---

因为之前想解决博客前后端对接时候跨站请求的问题，于是看到可以用 JSONP 来实现，研究了一番之后做一下笔记。

## 实现方法

要实现跨站请求是需要同时牵扯到前后两端的代码的。

### 后端

首先需要修改后端，这边以 Flask 为例：

```py
from functools import wraps
from flask import Flask, request, current_app, jsonify

app = Flask(__name__)


def support_jsonp(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + f(*args, **kwargs).data.decode('utf-8') + ')'
            return current_app.response_class(content, mimetype='application/json')
        else:
            return f(*args, **kwargs)

    return decorated_function


@app.route('/test')
@support_jsonp
def test():
    return jsonify({'abc': 1, 'def': 2})
```

这边 `support_jsonp` 装饰器会判断是否是 JSONP 请求，如果是，则返回相应的「特殊」数据（具体在下面原理的地方详细讲），否则就按正常的请求处理。

### 前端

后端改完之后，前端就可以来请求了，这边先以 jQuery 的 `ajax` 函数为例：

```js
$.ajax({
    url: 'http://api.example.com/test',
    dataType: 'jsonp',
    type: 'get',
    success: function(data) {
        console.log(JSON.parse(data));
    },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
        console.log('failed');
    }
});
```

这样就可以成功请求到跨站的 JSON 了。

<!-- more -->

## 原理

其实原理非常简单，就是利用了 `script` 标签可以获取其它站点的 JavaScript 代码并执行这一特点。

前面的示例中，前端发起请求后，观察后端的日志就会发现，请求时候的地址 `/test` 被修改成了形如 `/test?callback=jsonp1470561184396` 的地址，也就是加上了一个 `callback` 参数，这时候去看之前修改的后端代码的 `support_jsonp` 装饰器就会发现，后端这里实际上先检查请求参数里有没有 `callback` 这个参数，如果有的话，就会通过 `content = str(callback) + '(' + f(*args, **kwargs).data.decode('utf-8') + ')'` 这一句来把 `callback` 和 `f(*args, **kwargs)` 返回的 JSON 数据拼接起来形成形如 `jsonp1470561184396({"abc": 1, "def": 2})` 这样的「数据」，然后把这个「数据」返回给浏览器。这里的「数据」之所以加引号，是因为其实这里拼接出来的 `content` 已经不再是单纯的 JSON 数据，而是一个 JavaScript 函数调用，而这里面形如 `jsonp1470561184396` 的东西就是 `ajax` 自动给回调函数编的号。另外，这里被修改后的 `/test?callback=jsonp1470561184396` 这个链接实际上被放在了一个 `script` 标签的 `src` 属性里，于是：`script` 标签从 `http://api.example.com/test?callback=jsonp1470561184396` 获取到 JavaScript 代码 `jsonp1470561184396({"abc": 1, "def": 2})` 然后执行，成功调用回调函数。

理解了这个之后就可以比较随心所欲的使用了，无论代码怎么写只要最终后端拼接出了相应的函数调用代码就行，你甚至可以在 HTML 里面这么写：

```html
<script src="http://api.example.com/test?callback=console.log"></script>
```

## 参考资料

- [JSONP decorator](http://flask.pocoo.org/snippets/79/)
- [尝试使用jsonp 解决ajax 跨域解决](https://segmentfault.com/q/1010000000424040)
