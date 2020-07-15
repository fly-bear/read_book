# read book

摸鱼必备，一次只显示一行的小说阅读器

左手或右手单手即可翻页

也可使用鼠标滚轮控制

可阅读本地书籍，也可在线阅读起点网小说（需登录），获取段落评论

退出时清除所有痕迹

## 环境要求

安装 python3

## 使用方式

### 1. 本地阅读

将 txt 格式的小说放到 books 目录下，然后执行`python3 reader.py`

![img1](https://github.com/fly-bear/read_book/blob/master/imgs/Lark20200702145228.png)

可以输入数字选择书籍，也可以直接回车选择上一次看过的书，阅读器会记录页码。

![img2](https://github.com/fly-bear/read_book/blob/master/imgs/Lark20200702145323.png)

以段落分行，如果一段长度大于当前 console 的一行，则会被切分为多行，但页码不变

如果一段为空，则会自动跳过

*如果想让内容显示在终端底部，但发现底部有好几行空行，可以上下调整几下终端高度，空行会自动消失*

**如果改变了终端宽度，最好按 c 重新选择书籍或按 e 退出重进，不然行宽可能会计算出错**

#### 按键介绍

`j` 或 `a`: 上一行

`k` 或 `s`: 下一行

`t`: 跳转到某一行

`m`: 切换鼠标控制模式 (**若使用此模式需要先安装 pynput 库**)

`c`: 保存并返回选择书籍

`e`: 保存并退出

`d`: 删除一行输出

#### 鼠标控制

滚轮上下滚动阅读，左键双击返回键盘控制

若向上滚动时带动了页面，可按住 `shift` 再滚动

### 2. 起点在线阅读（试用阶段， 需一定开发知识）
首先网页登录起点，按 f12 打开开发者工具，选择network选项卡，随便操作一下网页（比如进入目录），在请求中头获取_csrfToken 和 cookie，复制，填入request_qidian.py文件的第3行和第5行

![img3](https://github.com/fly-bear/read_book/blob/master/imgs/Lark20200714153917.png)

点进想看的书的主页，在 url 地址中复制书籍数字 id

![img4](https://github.com/fly-bear/read_book/blob/master/imgs/Lark20200714153404.png)

执行`python3 reader.py qidian`，会出现和本地阅读一样的选择书籍，如果阅读新书，直接按回车，输入书名和id，就可以开始阅读了

![img5](https://github.com/fly-bear/read_book/blob/master/imgs/Lark20200714153036.png)

![img6](https://github.com/fly-bear/read_book/blob/master/imgs/Lark20200714153130.png)

#### 按键介绍

键盘基本操作和本地模式相同

`j`和`a`：上一行

`k`和`s`：下一行

`t`：跳转指定行（本章内）

`e`：退出

`d`：删除一行

`l`：跳转上一章

`n`：跳转下一章

`m`：切换鼠标模式

若想要看当前段落的评论，按`r`键进入评论模式

评论最多获取 50 条，同样使用`j`和`k`进行上下翻页，`d`删除一行，阅读完毕自动退出，或者按`e`退出，回到书籍阅读

![img7](https://github.com/fly-bear/read_book/blob/master/imgs/Lark20200714153459.png)

#### 鼠标控制

滚轮上下滚动阅读正文，左键双击返回键盘控制

右键进入本段评论，滚轮阅读评论，左键双击返回正文阅读





