# read book

摸鱼必备，一次只显示一行的小说阅读器

左手或右手单手即可翻页

退出时清除所有痕迹

## 环境要求
安装 python3

## 使用方式

将 txt 格式的小说放到 books 目录下，然后执行`python3 reader.py`

![img1](https://github.com/fly-bear/read_book/blob/master/imgs/Lark20200702145228.png)

可以输入数字选择书籍，也可以直接回车选择上一次看过的书，阅读器会记录页码。

![img2](https://github.com/fly-bear/read_book/blob/master/imgs/Lark20200702145323.png)

以段落分行，如果一段长度大于当前 console 的一行，则会被切分为多行，但页码不变

如果一段为空，则会自动跳过

## 按键介绍

`j` 或 `a`: 上一行

`k` 或 `s`: 下一行

`t`: 跳转到某一行

`c`: 保存并返回选择书籍

`e`: 保存并退出

`d`: 删除一行输出
