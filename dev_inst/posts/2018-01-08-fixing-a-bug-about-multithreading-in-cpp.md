---
title: 记一次关于 C++ 多线程写文件操作的错误修复
categories: [Dev]
tags: [C++, Multithreading]
created: 2018-01-08 16:17:00
---

前段时间酷 Q HTTP API 插件有用户报错说，连续请求两次 API 发送同一张图（通过 URL），会发生第二张图发不出去的问题。想了一下，问题很显然，因为插件在处理第一个请求的时候，开始下载图片，以 URL 的 md5 作为文件名，然后第二个请求到的时候（多线程处理），图还没有下完，但是同名文件已经存在了，插件以为是缓存，于是试图直接发送下到一半的文件，自然是发不出去了。

最简单的修复方法是让插件先把图片下载到一个临时文件，下载完成后再改名。但是这样的话，两个请求都会造成文件下载，但实际上这是不必要的，因为它们实际发的是同一张图。那么自然要想到让第二个请求发现已经有请求在发送同一张图的时候，等待其完成，然后直接发送已缓存的图。

一开始想到用一个 `std::map<std::string, std::mutex>` 来按文件名保存互斥锁，每个线程首先算出文件名，然后尝试获取文件名对应的锁。这个方法看起来虽然好像可以，但实际上仔细一想发现了问题，`std::map` 本身就不是线程安全的数据结构，两个线程很可能在创建和删除锁的时候发生冲突，而如果再给 map 加个锁，逻辑就开始有些混乱了，有发生死锁的风险。

于是去 Stack Overflow 搜了一圈，发现了 [`std::condition_variable`](http://en.cppreference.com/w/cpp/thread/condition_variable) 这么个东西，通过 [`wait`](http://en.cppreference.com/w/cpp/thread/condition_variable/wait) 和 [`notify_one`](http://en.cppreference.com/w/cpp/thread/condition_variable/notify_one)、[`notify_all`](http://en.cppreference.com/w/cpp/thread/condition_variable/notify_all) 方法来实现让线程等待和唤醒等待中的线程，基本上满足了我的需求。

最终修复代码如下：

```cpp
static unordered_set<string> files_in_process;
static mutex files_in_process_mutex;
static condition_variable cv;

if (!filename.empty() && make_file != nullptr) {
    unique_lock<mutex> lk(files_in_process_mutex);
    // wait until there is no other thread processing the same file
    cv.wait(lk, [=] {
        return files_in_process.find(filename) == files_in_process.cend();
    });
    files_in_process.insert(filename);
    lk.unlock();

    // we are now sure that only our current thread is processing the file
    if (make_file()) {
        // succeeded
        segment.data["file"] = filename;
    }

    // ok, we can let other threads play
    lk.lock();
    files_in_process.erase(filename);
    lk.unlock();
    cv.notify_all();
}
```

使用一个 `std::unordered_set<std::string>` 保存了当前正在处理的请求对应的文件名，同时对应有一个互斥锁。

第一部分首先获取互斥锁，然后调用 `std::condition_variable` 的 `wait` 方法，这个方法会首先判断传入的谓词（第二个参数）是否满足（在拥有锁的情况下调用），如果不满足，释放锁，然后等待（阻塞当前线程）。在第一个 API 调用时，显然并没有其它线程正在处理同名文件，所以它会往下执行，把当前文件名放到集合，然后释放锁（这是很重要的，在实际下载文件开始之前需要释放锁，否则下载别的文件的线程也得等这个线程执行完才能执行）。

第二部分就是下载文件操作了，这里之所以不用拥有锁，是因为我们在第一部分已经确定没有其它线程正在操作这个文件，而一旦文件名插入到集合中（拥有锁的时候插入的），别的下载同名文件的线程就会在 `wait` 方法里阻塞了。因此第二部分我们可以确定每个文件只有一个线程在下载。

第三部分就是下载完成后从文件名集合中删除当前文件名了，在拥有锁的情况下删除，然后立即释放锁，接着调用 `notify_all`，还记得其它需要发送同名文件的线程都在 `wait` 中等待吗，调用 `notify_all` 之后它们会被唤醒，然后依次获取锁、判断谓词是否满足，当第二个发送同一图片的线程执行到第二部分的时候，它会发现图片已经缓存了，于是直接发送缓存了的图片。

至此完美解决了一开始的问题。
