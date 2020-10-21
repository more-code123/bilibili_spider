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


def search(keyword):
    search_url = "https://search.bilibili.com/all?keyword={}".format(keyword)
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
        table.add_row([i+1, titles[i], urls[i]])
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
    header = {
        'accept': '*/*',
        'accept-encoding': 'identity',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'origin': 'https://www.bilibili.com',
        'pragma': 'no-cache',
        'range': 'bytes=0-',
        'referer': 'https://www.bilibili.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
    }
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
    # print(file_name.split("/")[3], url, audio_url)
    print("正在下载：{}.mp4".format(file_name.split("/")[3]))
    video_res = requests.get(video_url, headers=header).content
    with open(file_name+"video.mp4", "wb+")as f:
        f.write(video_res)
    print("正在下载：{}.mp3".format(file_name.split("/")[3]))
    audio_res = requests.get(audio_url, headers=header).content
    with open(file_name+"audio.mp3", "wb+")as f:
        f.write(audio_res)

def merge(path):
    print("正在合成{}".format(path))
    video_path = path + "/video.mp4"
    audio_path = path + "/audio.mp3"
    cmd = "ffmpeg -i {} -i {} -c:v copy -c:a aac -strict experimental {}".format(video_path, audio_path, path+".mp4")
    subprocess.call(cmd, shell=True)
    

if __name__ == "__main__":
    baseDir = "D:/下载/video/"
    keyword = input("请输入关键字：")
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
