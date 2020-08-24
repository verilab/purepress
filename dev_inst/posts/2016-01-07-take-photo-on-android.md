---
title: Android 调用系统相机拍摄照片
categories: Dev
tags: [Java, Android]
---

## 1. 获取缩略图

使用 Intent 可以很方便地调用系统相机，通过 `startActivityForResult` 方法启动，代码如下：

```java
Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
startActivityForResult(intent, REQUEST_CODE); // REQUEST_CODE 为预先定义的 int 常量
```

重载 Activity 的 `onActivityResult` 方法，可以获取返回的结果中的 Bitmap 并显示，代码如下：

```java
@Override
protected void onActivityResult(int requestCode, int resultCode, Intent data) {
    super.onActivityResult(requestCode, resultCode, data);

    if (resultCode == RESULT_OK && requestCode == REQUEST_CODE) {
        Bundle bundle = data.getExtras();
        Bitmap bitmap = (Bitmap) bundle.get("data");
        mImageView.setImageBitmap(bitmap); // mImageView 为预先定义的 ImageView
    }
}
```

出于性能方面的考虑，`onActivityResult` 中得到 `data` 里的 Bitmap 并不是完整照片，而是压缩过的很不清晰的缩略图。

<!-- more -->

## 2. 存储完整图片

只能获取缩略图显然大多数情况下不符合我们的预期，有个办法就是先把拍摄的照片存储下来，然后再按路径读取它并显示，需要修改一下调用系统相机的代码：

```java
mFilePath = getExternalFilesDir(null).getPath() + "/temp.png"; // mFilePath 为预先声明的成员变量
Uri picUri = Uri.fromFile(new File(mFilePath));
Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
intent.putExtra(MediaStore.EXTRA_OUTPUT, picUri);
startActivityForResult(intent, REQUEST_CODE);
```

第 4 行代码指定了图片存储的地址，这里的 `filePath` 是 SD 卡根目录下 `Android/data/<PackageName>/files/temp.png`。

此时拍摄完照片后，完整图片会被存储到指定位置，同样可以在 `onActivityResult` 方法中读取，代码如下：

```java
@Override
protected void onActivityResult(int requestCode, int resultCode, Intent data) {
    super.onActivityResult(requestCode, resultCode, data);

    if (resultCode == RESULT_OK && requestCode == REQUEST_CODE) {
        try (FileInputStream fis = new FileInputStream(mFilePath)) {
            Bitmap bitmap = BitmapFactory.decodeStream(fis);
            mImageView.setImageBitmap(bitmap1);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

由于这里图片存储的路径是在应用自己的外部 data 目录中，较新版本的 Android 中无需 `READ_EXTERNAL_STORAGE` 权限，详见 [Android存储访问及目录](http://www.cnblogs.com/mengdd/p/3742623.html)。

有一个比较坑的点就是，如果你试图在 `intent.putExtra(MediaStore.EXTRA_OUTPUT, picUri)` 这里把存储路径指定到应用的内部 data 目录 `/data/data/<PackageName>` 中，调用系统相机拍了照之后点确定会卡在那没反应，稍微想一下就会发现，这里调用的系统相机显然是不能直接访问我们应用的内部 data 目录的，所以需要把存储路径指定在外部存储中。（见 [Camera not working/saving when using Cache Uri as MediaStore.EXTRA_OUTPUT](http://stackoverflow.com/questions/18711525/camera-not-working-saving-when-using-cache-uri-as-mediastore-extra-output)）
