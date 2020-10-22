import requests
import json
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor, wait
import prettytable as pt
from tqdm import tqdm
import os
import subprocess
import shutil

def parseUrl(url):
    res = requests.get(url).text
    soup = BeautifulSoup(res, "html.parser")
    item = soup.find_all("a", attrs={"class": "title"})
    movie_name, movie_url = [], []
    for i in item:
        movie_name.append(i.text)
        movie_url.append("https:"+i["href"])
    return movie_name, movie_url

def formatOutput(titles, urls):
    table = pt.PrettyTable()
    table.field_names = ["序号", "电影名称", "链接"]
    for i in range(len(titles)):
        table.add_row([i+1, titles[i], urls[i].split("?")[0]])
    print(table)

def checkInput(inputStr):
    while True:
        try:
            choiseNum = [int(i) for i in inputStr.split(" ")]
            if set(choiseNum) <= set([i+1 for i in range(100)]):
                return choiseNum
        except ValueError:
            if inputStr == "all":
                return [i+1 for i in range(100)]
        inputStr = input("输入有误,请重新输入下载序号，以空格分开，全部下载请输入\"all\"：")

def getEp(name, url):
    ep_res = requests.get(url).text
    soup = BeautifulSoup(ep_res, "html.parser")
    item = soup.find_all("script")[-2]
    epid = json.loads(re.findall(r"\"newestEp\":(.*?),\"payMent\"", str(item))[0])["id"]
    header = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'cookie': '',  # 登录B站获取自己的cookie
        'origin': 'https://www.bilibili.com',
        'pragma': 'no-cache',
        'referer': 'https://www.bilibili.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36 Edg/86.0.622.48',
    }
    url = "https://api.bilibili.com/pgc/player/web/playurl?qn=80&type=&otype=json&fourk=1&ep_id={}&fnver=0&fnval=80&session=10f9a2a4b3cb7b8a7754edd92d09fb04".format(epid)
    res = requests.get(url, headers=header).text
    video_url = json.loads(res)["result"]["dash"]["video"][0]["base_url"]
    audio_url = json.loads(res)["result"]["dash"]["audio"][0]["base_url"]
    path = mkdir(name)
    down_task(path+"video.mp4", video_url)
    down_task(path+"audio.mp3", audio_url)

def mkdir(file_name):
    file_name = file_name.replace(" ", "")
    file_name = re.sub('[\\/:*?"<>|]','',file_name)
    if not os.path.exists("D:/下载/video/"+file_name):
        os.makedirs("D:/下载/video/"+file_name)
    return "D:/下载/video/"+file_name+"/"

def down_task(path, url):
    file_name = path.split("/")[3] + path.split("/")[4]
    header = {
        'accept': '*/*',
        'accept-encoding': 'identity',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'origin': 'https://www.bilibili.com',
        'pragma': 'no-cache',
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
    bar = tqdm(range(100))
    current = 0
    with open(path, "wb+")as f:
        for _ in bar:
            bar.set_description("{}，大小{}MB".format(file_name, max_size/1048576))
            header["range"] = "bytes={}-{}".format(old_size, new_size)
            res = requests.get(url, headers=header).content
            f.write(res)
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
    url = "https://www.bilibili.com/v/popular/rank/movie"
    movie_name, movie_url = [], []
    movie_name, movie_url = parseUrl(url)
    formatOutput(movie_name, movie_url)
    select = checkInput(input("请输入下载序号，以空格分开，全部下载请输入\"all\"："))
    with ThreadPoolExecutor(max_workers=100)as t:
        task = [t.submit(getEp, movie_name[i-1], movie_url[i-1])for i in select]
        wait(task)
    # getEp("举起手来2：追击阿多丸号", "https://www.bilibili.com/bangumi/play/ss12454?theme=movie")  # 测试
    for dir in os.listdir(baseDir):
        if os.path.isdir(baseDir+dir):
            merge(baseDir+dir)
            shutil.rmtree(baseDir+dir, True)