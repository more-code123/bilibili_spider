import json
import os
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, wait

import ffmpeg
import prettytable as pt
import requests
from bs4 import BeautifulSoup
from progressbar import ProgressBar
from tqdm import tqdm


def search(keyword, order=1):
    try:
        if int(order) in [1, 2, 3, 4, 5]:
            orderBy = ["totalrank", "click", "pubdate", "dm", "stow"][int(order)]
    except:
        orderBy = "totalrank"
    search_url = "https://search.bilibili.com/all?keyword={}&order={}".format(keyword, orderBy)
    res = requests.get(search_url).text
    soup = BeautifulSoup(res, "html.parser")
    # title_list = soup.find_all("a", attrs={"class": "title"})
    titles, urls = [], []
    for i in soup.find_all("li", attrs={"class", "video-item"}):
        titles.append(i.a["title"])
        urls.append("https:"+i.a["href"])
    return titles, urls

def formatOutput(titles, urls):
    table = pt.PrettyTable()
    table.field_names = ["序号", "视频名称", "链接"]
    for i in range(len(titles)):
        table.add_row([i+1, titles[i], urls[i].split("?")[0]])
    print(table)

def checkInput(inputStr):
    while True:
        try:
            choiseNum = [int(i) for i in inputStr.split(" ")]
            if set(choiseNum) <= set([i+1 for i in range(20)]):
                return choiseNum
        except ValueError:
            if inputStr == "all":
                return [i+1 for i in range(20)]
        inputStr = input("输入有误,请重新输入下载序号，以空格分开，全部下载请输入\"all\"：")

def mkdir(file_name):
    file_name = file_name.replace(" ", "")
    file_name = re.sub('[\\/:*?"<>|]','',file_name)
    if not os.path.exists("D:/下载/video/"+file_name):
        os.makedirs("D:/下载/video/"+file_name)
    return "D:/下载/video/"+file_name+"/"

def down(title, url):
    file_name = mkdir(title)
    res = requests.get(url).text
    soup = BeautifulSoup(res, "html.parser")
    script = soup.find_all("script")
    video_url, audio_url = "", ""
    for i in script:
        if ".m4s" in str(i):
            info_dict = json.loads(re.findall(r"window.__playinfo__=(.*?)</script>", str(i))[0])
            video_url = info_dict["data"]["dash"]["video"][0]["baseUrl"]
            audio_url = info_dict["data"]["dash"]["audio"][0]["baseUrl"]
    down_task(file_name+"video.mp4", video_url)
    down_task(file_name+"audio.mp3", audio_url)

def down_task(path, url):
    # progressbar = ProgressBar()
    file_name = path.split("/")[3] + path.split("/")[4]
    header = {
        'accept': '*/*',
        'accept-encoding': 'identity',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'origin': 'https://www.bilibili.com',
        'pragma': 'no-cache',
        # 'range': 'bytes=0-',
        'referer': 'https://www.bilibili.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
    }
    header["range"] = "bytes=0-100"
    max_size = int(requests.get(url,headers=header).headers["Content-Range"].split("/")[1])
    one_size = max_size // 100
    old_size = 0
    new_size = one_size
    # print("正在下载：{}，大小：{}MB".format(file_name, max_size/1048576))
    bar = tqdm(range(100))
    current = 0
    with open(path, "wb+")as f:
        for _ in bar:
            bar.set_description("{}，大小{}MB".format(file_name, max_size/1048576))
            header["range"] = "bytes={}-{}".format(old_size, new_size)
            res = requests.get(url, headers=header).content
            f.write(res)
            # if (i+1) % 10 == 0:
            #     print("{}已下载{}%".format(path.split("/")[3:], i+1))
            # print()
            old_size = new_size + 1
            if current <= 99:
                new_size = old_size + one_size
            else:
                new_size = max_size
            current += 1
    print("{}下载完成".format(file_name))

def merge(path):
    print("正在合成{}".format(path))
    video_path = path + "/video.mp4"
    audio_path = path + "/audio.mp3"
    cmd = "ffmpeg -i {} -i {} -c:v copy -c:a aac -strict experimental {}".format(video_path, audio_path, path+".mp4")
    subprocess.call(cmd, shell=True)
    

if __name__ == "__main__":
    baseDir = "D:/下载/video/"
    keyword = input("请输入关键字：")
    orderBy = input("排序方式：\n\t1.综合排序\n\t2.最多点击\n\t3.最新发布\n\t4.最多弹幕\n\t5.最多收藏\n请选择排序方式（默认为1）：")
    titles, urls = search(keyword)
    formatOutput(titles, urls)
    select = checkInput(input("请输入下载序号，以空格分开，全部下载请输入\"all\"："))
    with ThreadPoolExecutor(max_workers=5)as t:
        task = [t.submit(down, titles[i-1], urls[i-1])for i in select]
        wait(task)
    for dir in os.listdir(baseDir):
        if os.path.isdir(baseDir+dir):
            merge(baseDir+dir)
            shutil.rmtree(baseDir+dir, True)
