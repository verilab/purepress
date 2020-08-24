---
title: FusionCache 实现思路和使用方法
categories: [Dev, Detailed]
tags: [Android, FusionCache, Cache]
---

前几天看《Android 开发艺术探索》关于 Bitmap 加载的那章，里面讲解了一个内存和磁盘二级缓存的 ImageLoader 的实现方法，然后就突然想自己写一个内存+磁盘的混合缓存框架，正好平时上课闲得慌，就在课上构思，最终在昨天完成了这个 [FusionCache](https://github.com/richardchien/fusion-cache)。虽然注释写得挺多，但还是怕以后看不懂，所以这里记录一下实现思路。

## 实现思路

首先这个缓存应该基于键值对，使用起来方便嘛，作为一个缓存，本身就是为了增强应用使用体验而用的，并不是什么逻辑上的核心部件，那么就应该用起来越简单越好。

并且缓存应当可以分别设置内存和磁盘缓存的容量上限，也就是说要计算每个对象在内存和磁盘中所占空间。

由于不是所有类的对象都能存到磁盘中，也不是所有对象都能成功计算内存占用，所以需要限制支持存入缓存的对象类型，参考 [ASimpleCache](https://github.com/yangfuhai/ASimpleCache)，支持 `String`、`JSONObject`、`JSONArray`、`byte[]`、`Bitmap`、`Drawable`、`Serializable`。

<!-- more -->

考虑到如果做混合缓存，一定得分别独立实现内存缓存和磁盘缓存，为了降低耦合，这两个类肯定是互相不知道对方的存在的，但是作为缓存，它们的 API 应该相似，包括整体的混合缓存，也应该使用相似的 API，于是写了个 `Cache` 接口来统一之。本来考虑有可能某些接口可以预先给出默认实现而不用依赖于具体的缓存类，于是加了个 `AbstractCache` 类用来给具体类继承，不过现在暂时留空了。`FusionCache`、`MemCache` 和 `DiskCache` 都是继承自 `AbstractCache`。

并且，这个混合缓存遵循实现以下动态机制：

- 插入对象时：
 - 优先放进内存缓存，如果对象放进去时，为了腾出空间而删除了较老的缓存，则把这些删除掉的缓存放进磁盘缓存；
 - 如果对象大小超过了内存缓存的最大容量（无法放进内存缓存），则放进磁盘缓存；
 - 如果对象大小超过了磁盘缓存的最大容量，则不缓存。

- 取出对象时：
 - 如果对象在内存缓存，则直接取出返回；
 - 如果对象在磁盘缓存，则取出后放进内存缓存（原磁盘缓存中的缓存文件不删除），并返回结果；
 - 如果对象不存在，则返回 `null`。

- 删除对象时，内存和磁盘缓存中所有对应于要删除的键的缓存都将被删除。

- 清空缓存时，所有内存和磁盘缓存，以及磁盘缓存目录都会被删除。

这样一个动态机制通过内部适时地调用内存缓存和磁盘缓存来实现，所以下面分别独立实现这两种缓存。

### 内存缓存

Android 系统内置了一个 `LruCache` 类用来实现 LRU 算法的内存缓存，它内部用了一个 `LinkedHashMap` 来存对象的强引用，显然这其实可以直接用来作内存缓存。

但是由于从整体上看，混合缓存需要能够在内存缓存满了的情况下，把较老的那些由 LRU 算法淘汰掉的对象转存到磁盘缓存，内置的 `LruCache` 没法做到这一点，它只会在删除较老缓存对象时调用 `void entryRemoved(boolean, K, V, V)` 来通知其子类，一次一个值。为了实现在内存缓存满了的情况下，`put()` 方法能够返回一个被删除了的对象的列表，考虑继承 `LruCache` 来扩展，并且由于 `entryRemoved()` 必须是删除一个对象调用一次，就是说得在第一次删除之前做一个标记，然后在最后一次删除结束，也就是 put 完毕之后，提供被删除的对象列表，于是新增 `mRecentlyEvictedEntryList` 和 `mMarkRecentlyEvicted` 成员变量，但开关标记和清空列表只能从外部操作，如果在 `MemCache` 类里面做这件事，会导致耦合比较高，于是用一个 `LruCacheWrapper` 类来包装扩展的 `ExtendedLruCache`，`LruCacheWrapper` 对外提供一个可以获取到被删除的对象列表的 `put()` 方法，即 `V put(K, V, List<Entry<K, V>>)`，于是 `MemCache` 只需要直接使用这个包装类即可，不用担心内部是怎么实现的。

之前说到需要计算每个对象的空间占用，由于其实内存缓存和磁盘缓存内部都使用了 `LruCacheWrapper`，而对象在内存和在磁盘上占用的大小是不一样的，所以这个大小计算工作应该拿出来放在内存缓存和磁盘缓存中分别实现，于是 `LruCacheWrapper` 内部声明了一个 `Delegate` 接口用来实现 `sizeOf()`，而 `ExtendedLruCache` 里的 `sizeOf()` 只需要调用这个接口的实现就行。

搞清楚了内部 `LruCacheWrapper` 的实现，接下来实现 `Cache` 接口的方法就很简单了，只需要考虑到特别提供一个 package only 的能够获取被删除的对象列表的 `put()` 方法，其它就是简单的调用 `LruCacheWrapper`。

### 磁盘缓存

这里磁盘缓存没有用 `DiskLruCache`，而是直接操作缓存文件。

为了实现 LRU 算法，其实只要继续复用 `LruCacheWrapper` 就好了，不仅有了 LRU，而且还有了缓存容量控制，只不过这里 `LruCacheWrapper` 里面不存对象强引用，只是存缓存文件的大小即可，方便后续其它操作时候正确计算缓存总大小的变化，而实际的缓存操作，就是按不同对象类型写入到文件、读取文件、删除文件即可，另外需要实现 `LruCacheWrapper` 的 `entryRemoved()` 从而在磁盘缓存满了的时候，把最老的缓存文件删掉。

另外，磁盘缓存由于也采用 LRU，因此为了下次启动时能恢复缓存对象的次序，需要维护一个日志文件，因此通过 `saveJournal()` 和 `restoreJournal()` 来保存和恢复日志文件。

### 混合缓存

其实混合缓存只要弄清楚在内存和磁盘缓存之间转移对象的逻辑，就非常容易实现。

为了方便使用，可以让用户选择开启或不开启混合模式，如果开了，那么就按前面讲的动态机制来执行操作，如果不开启，那么就只能通过 `getMemCache()` 和 `getDiskCache()` 来分别使用内存和磁盘缓存。

具体的 put、get、remove、clear 操作的实现只需要根据动态机制的逻辑来调用相应的内存缓存和磁盘缓存的方法即可。

另外，提供一个将内存中的缓存全部存入磁盘缓存的方法，毕竟在退出应用的时候，我们不希望丢掉内存缓存（比如有 Bitmap 在里面，由于经常使用，还没有存到磁盘缓存的情况）。

## 使用方法

根据上面的实现思路实现了之后，就可以很方便地使用缓存，因为 API 实在太简单了……如下：

```java
FusionCache cache = new FusionCache(
        getApplicationContext(),
        4 * 1024 * 1024, // 缓存容量的单位是字节
        50 * 1024 * 1024,
        true // 开启混合缓存模式，默认为 true
);

cache.put("string", "This is a string.");
cache.put("jsonObject", new JSONObject("{}"));
cache.put("jsonArray", new JSONArray("[]"));
cache.put("bytes", new byte[10]);
cache.put("bitmap", Bitmap.createBitmap(100, 100, Bitmap.Config.ARGB_8888));
cache.put("drawable", getDrawable(R.mipmap.ic_launcher));

String string = cache.getString("string");
JSONObject jsonObject = cache.getJSONObject("jsonObject");
JSONArray jsonArray = cache.getJSONArray("jsonArray");
byte[] bytes = cache.getBytes("bytes");
Bitmap bitmap = cache.getBitmap("bitmap");
Drawable drawable = cache.getDrawable("drawable");

cache.saveMemCacheToDisk(); // 将内存缓存中的内容全部保存到磁盘缓存, 一般在应用退出时调用

cache.remove("bitmap");
cache.clear();
```

得益于都实现了 `Cache` 接口，`MemCache` 和 `DiskCache` 的使用方法也几乎和上面的一样，只是构造方法有所不同。

## 最后

其实这个缓存框架实现起来难度真的不大，不过这次注释、文档都写得很齐全，还是很爽的哈，自我感觉相比以前有了挺大的进步。虽然客观上来说，距离那些菊苣们还是有较大差距，但不管怎么说，只要自己在不断进步，就是最好了。
