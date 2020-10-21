# bilibili_spider

## search.py

>功能

* 输入关键字，获取关键字对应的前20个B站搜索结果，根据需要下载结果中的内容

>采用***python3.7***编写

* python3.7 官网[下载链接](https://www.python.org/ftp/python/3.7.9/python-3.7.9-amd64.exe)

>使用了以下第三方模块
******
* ***ffmpeg***：B站以.m4s格式将视频、音频分开传输，爬取到本地的视频、音频文件可以使用***ffmpeg***模块合并，安装：pip install ffmpeg，pip install ffmpy，另外需要去官网下载[ffmpeg](https://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2)，并配置环境变量

* ***prettytable***：生成一个相当工整的命令行表格，安装：pip install prettytable

* ***requests***：python的一个http请求模块，search.py所有网络请求基于该模块，安装：pip install requests

* ***BeautifulSoup***：快速从HTML文件中提取数据，安装：pip install bs4，导入时使用from bs4 import Beautifulsoup
******


>配置

* 本爬虫默认下载位置为***D:/下载/video/***，可根据需要进行修改，要修改main方法中的baseDir，以及mkdir方法中各个路径

* main方法使用了线程池ThreadPoolExecutor可根据实际情况修改max_workers(线程数量)大小

## top100.py
>功能

* 下载B站top100的所有视频，不包括p2以及p2之后的视频


>采用***python3.7***编写

* python3.7 官网[下载链接](https://www.python.org/ftp/python/3.7.9/python-3.7.9-amd64.exe)

>使用了以下第三方模块
******
* ***requests***：python的一个http请求模块，search.py所有网络请求基于该模块，安装：pip install requests

* ***BeautifulSoup***：快速从HTML文件中提取数据，安装：pip install bs4，导入时使用from bs4 import Beautifulsoup
******

>配置

* 不同于上一个爬虫，该爬虫采用的时相对路径，下载的视频以及生成的文件均在该爬虫所在目录下