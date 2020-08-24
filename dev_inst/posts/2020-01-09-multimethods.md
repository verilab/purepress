---
title: 关于 Multimethods
categories: [Dev]
tags: [编程语言, 多态, 多分派, Multimethods, C++]
created: 2020-01-09 11:24:00
---

最近学到了一个编程语言中叫作 **multimethods** 的概念，在这里做个笔记。

## 为什么

要解释这个概念，首先提出两个程序设计中会遇到的问题。

### 1. Expression Problem

#### 案例

考虑 C++ 中这样一种情况：

```cpp
struct Event {
    virtual ~Event() {}
};

struct MessageEvent : Event {
    virtual ~MessageEvent() {}

    std::string message;
    int user_id;
};

struct NoticeEvent : Event {
    virtual ~NoticeEvent() {}

    std::string notice;
};
```

如果此时需要给这些 `Event` 类添加一个序列化对象为 JSON 的成员函数，从面向对象的角度自然会想到给 `Event` 加一个虚函数，然后在子类中实现：

```cpp
struct Event {
    virtual ~Event() {}
    virtual std::string to_json() const = 0;
};

struct MessageEvent : Event {
    virtual ~MessageEvent() {}

    std::string message;
    int user_id;

    std::string to_json() const override {
        return "json for message event";
    }
};
```

这种方法的问题在于，这些 `Event` 类很可能是第三方库中的，而它们对应的实现文件可能已经编译成了链接库，要修改类定义是很困难的。

要在不改变类定义的情况下给类添加新功能，这就是 **expression problem**。

#### 横切关注点（Cross-cutting Concern）

Expression problem 是横切关注点问题的一部分，以上面为例，`to_json` 是一种非常普遍的操作，不仅是 `Event` 类，其它各种类都可能需要此操作。类似的还有 `to_string`、`time_it` 等，它们都是一种与很多模块都相关的横切面。

### 2. 多分派（Multiple Dispatch）

在 OOP 中，最常用的操作是通过形如 `obj.operate()` 的方式调用对象的方法（C++ 中的成员函数）。C++ 会隐式地给 `operate` 函数增加一个 `this` 参数，指示调用的方法所属的对象。这种操作使用一个参数来确定要调用的函数，因此称为**单分派（single dispatch）**。

如果要使用两个或多个参数来确定要调用的函数，也就是**多分派**，该怎么办呢？一种方案是函数重载（override），例如：

```cpp
struct Shape {
    virtual ~Shape() {}
    // ...
};

struct Circle : Shape {
    virtual ~Circle() {}
    // ...
};

struct Rect : Shape {
    virtual ~Rect() {}
    // ...
};

bool intersect(const Circle &a, const Circle &b);
bool intersect(const Rect &a, const Rect &b);
bool intersect(const Circle &a, const Rect &b);
```

但问题是，重载函数的选择是在编译期进行的，但实际编程中，常常会把各类型的对象都通过 `Shape &` 来引用，此时必须在运行期动态确定要调用的函数，函数重载就不可行了。

## Open Multimethods

Open multimethods 可同时解决上面的两个问题，这里之所以是 open，是因为 method（方法）通常指类内定义的函数，这里 open 意思是方法定义在类外。

以 [YOMM2](https://github.com/jll63/yomm2) 库提供的矩阵类为例可以比较容易理解 open multimethods 的思路：

```cpp
// 不可修改的库代码部分：

// 矩阵基类
struct Matrix {
    virtual ~Matrix() {}
    // ...
};

// 稠密矩阵
struct DenseMatrix : Matrix { /* ... */ };
// 对角矩阵
struct DiagonalMatrix : Matrix { /* ... */ };

// 可修改的应用程序代码部分：

#include <yorel/yomm2/cute.hpp>

using yorel::yomm2::virtual_;

register_class(Matrix);
register_class(DenseMatrix, Matrix);
register_class(DiagonalMatrix, Matrix);

declare_method(string, to_json, (virtual_<const Matrix &>));

define_method(string, to_json, (const DenseMatrix &m)) {
    return "json for dense matrix...";
}

define_method(string, to_json, (const DiagonalMatrix &m)) {
    return "json for diagonal matrix...";
}

int main() {
    yorel::yomm2::update_methods();

    shared_ptr<const Matrix> a = make_shared<DenseMatrix>();
    shared_ptr<const Matrix> b = make_shared<DiagonalMatrix>();

    cout << to_json(*a) << "\n"; // json for dense matrix
    cout << to_json(*b) << "\n"; // json for diagonal matrix

    return 0;
}
```

可以看到，open multimethods 的定义和函数重载相似，但 `a` 和 `b` 都是 `Matrix` 的指针，当调用 `to_json` 时，程序能够正确地在运行期根据 `a`、`b` 的实际类型来选择函数。同时，不需要将 `to_json` 写到 `Matrix` 类的内部，减少了侵入和重新编译的成本。

除此之外，YOMM2 还用一个矩阵乘法的例子演示了多分派的实现：

```cpp
declare_method(
    shared_ptr<const Matrix>,
    times,
    (virtual_<shared_ptr<const Matrix>>, virtual_<shared_ptr<const Matrix>>));

// 任意 Matrix * Matrix -> DenseMatrix
define_method(
    shared_ptr<const Matrix>,
    times,
    (shared_ptr<const Matrix> a, shared_ptr<const Matrix> b)) {
    return make_shared<DenseMatrix>();
}

// DiagonalMatrix * DiagonalMatrix -> DiagonalMatrix
define_method(
    shared_ptr<const Matrix>,
    times,
    (shared_ptr<const DiagonalMatrix> a, shared_ptr<const DiagonalMatrix> b)) {
    return make_shared<DiagonalMatrix>();
}
```

程序将在运行时通过 `a`、`b` 的 `typeid` 来选择最 specific 的函数来调用。

## 参考资料

- [jll63/yomm2](https://github.com/jll63/yomm2)
- [Cross-cutting concern - Wikipedia](https://en.wikipedia.org/wiki/Cross-cutting_concern)
- [Expression problem - Wikipedia](https://en.wikipedia.org/wiki/Expression_problem)
- [Expression Problem - WikiWikiWeb](http://wiki.c2.com/?ExpressionProblem)
- [Multiple dispatch - Wikipedia](https://en.wikipedia.org/wiki/Multiple_dispatch)
- [Open Multi-Methods for C++](http://www.stroustrup.com/multimethods.pdf)
- [typeid 运算符 - cppreference.com](https://zh.cppreference.com/w/cpp/language/typeid)
- [Five-minute Multimethods in Python](https://www.artima.com/weblogs/viewpost.jsp?thread=101605)
