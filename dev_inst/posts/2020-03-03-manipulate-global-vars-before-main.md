---
title: 在 main 函数运行之前修改全局变量
categories: [Dev]
tags: [C++, 奇技淫巧]
created: 2020-03-03 20:48:00
---

## 动机

写 C++ 时往往有这样一种需求，即在 main 函数运行之前就对全局变量进行修改，比如向全局的容器对象中填充内容。考虑下面这个需求：作为一个第三方库，我希望向用户提供一种事件机制，在发生某些事件时，触发用户编写的某些代码，但我不希望用户自己编写 main 函数并在里面设置事件回调，而是提供一个更强制的接口。在这个需求下，设计接口如下：

```cpp
// 用户代码 app.cpp

#include <somelib.hpp>

ON_EVENT(handler1) {
    // 事件处理程序 1
}

ON_EVENT(handler2) {
    // 事件处理程序 2
}
```

此时，用户的两个处理程序，就需要在静态区初始化时被注册到我所提供的第三方库的某个全局容器对象中。

## 有问题的实现

最开始通过下面的代码来实现上述机制：

```cpp
// somelib.hpp

extern std::vector<std::function<void()>> event_callbacks;

#define ON_EVENT_A(Name)                                \
    static void __handler_##Name();                     \
    static bool __dummy_val_##Name = [] {               \
        event_callbacks.emplace_back(__handler_##Name); \
        return true;                                    \
    }();                                                \
    static void __handler_##Name()
```

```cpp
// somelib.cpp

std::vector<std::function<void()>> event_callbacks;
```

这种实现乍看起来没有什么问题，并且在很多情况下真的可以正常工作。然而，这种表面上的正常是建立在 `app.cpp` 中的全局变量 `__dummy_val_##Name` 迟于 `somelib.cpp` 中的 `event_callbacks` 初始化的情况下的，也就是说，一旦 `__dummy_val_##Name` 在 `event_callbacks` 之前初始化，那么调用 `event_callbacks.emplace_back` 的那个 lambda 表达式将会访问一个无意义的 `event_callbacks`。

那么这种错误情况到底有没有可能出现呢，花费好几个小时调试程序的事实已经告诉我**有可能**。后来查阅资料发现，在同一个翻译单元，全局变量的初始化顺序是按定义顺序来的，但在不同的翻译单元之间，初始化顺序是未定义的。上面的实现中，两个变量正是处于不同的翻译单元。

## 正确的实现

同一篇资料里也提出了解决这个问题的方法，那就是利用函数内静态变量在第一次使用时初始化的特性。只需要一点点修改即可得到正确的实现：

```cpp
// somelib.hpp

inline auto &event_callbacks() {
    static std::vector<std::function<void()>> _event_callbacks;
    return _event_callbacks;
}

#define ON_EVENT_A(Name)                                  \
    static void __handler_##Name();                       \
    static bool __dummy_val_##Name = [] {                 \
        event_callbacks().emplace_back(__handler_##Name); \
        return true;                                      \
    }();                                                  \
    static void __handler_##Name()
```

同时不再需要 `somelib.cpp` 了。

这里 `event_callbacks()` 函数调用保证了当它返回引用时，`_event_callbacks` 静态变量必然已经被初始化，因此 `emplace_back` 必然有效。

## 为什么可以是 inline

这是另一个话题了。上面的 `event_callbacks` 被标记为 inline 函数，这意味着它将在可能的情况下被原地展开。那么这会不会导致不同的用户 cpp 文件中拿到的 `_event_callbacks` 引用不一样呢？答案是不会，因为 inline 有一个特性就是，编译器会自动将多次导入的 inline 函数合并为一个，因此其中的静态变量也只有一个。

## 参考资料

- [C++静态变量的初始化](https://www.jianshu.com/p/dd34cee5242c)
- [static variables in an inlined function](https://stackoverflow.com/questions/185624/static-variables-in-an-inlined-function)
- [More C++ Idioms/Construct On First Use](https://en.wikibooks.org/wiki/More_C++_Idioms/Construct_On_First_Use)
