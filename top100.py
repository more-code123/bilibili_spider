import json
import os
import random
import re
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, wait

import requests
from bs4 import BeautifulSoup


def get_ua():
    user_agent=[
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) QQBrowser/6.9.11079.201',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)',
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
    ]
    return random.choice(user_agent)

def down_video(video_url, audio_url, file_name, flag=5):  # flag重试5次
    print("开始下载**{}**视频文件".format(file_name))
    file_name = file_name.strip()
    file_name = re.sub('[\\/:*?"<>|]','',file_name)
    path = "./video/"+file_name+"/video.mp4"
    try:  # 实现断点续传
        current_size = os.path.getsize(path) + 1
    except FileNotFoundError:
        current_size = 0
    video_header = {
        'accept': '*/*',
        'accept-encoding': 'identity',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'origin': 'https://www.bilibili.com',
        'pragma': 'no-cache',
        'range': 'bytes={}-'.format(current_size),  # 0- 请求整个视频,current_size- 断点续传
        'referer': 'https://www.bilibili.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': get_ua(),
    }
    try:
        res = requests.get(video_url, headers=video_header).content
        with open(path, "ab+")as f:
            f.write(res)
        print("**{}**视频文件下载完成".format(file_name))
        down_audio(audio_url, file_name)
    except:
        if flag != 0:
            return down_video(video_url, audio_url, file_name, flag-1)  # 遇到错误重试
        else:
            print("**{}**视频文件下载失败".format(file_name))
            return

def down_audio(url, file_name,flag=5):
    print("开始下载**{}**音频文件".format(file_name))
    audio_header = {
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
        'user-agent': get_ua(),
    }
    try:
        file_name = file_name.strip()
        file_name = re.sub('[\\/:*?"<>|]','',file_name)
        path = "./video/"+file_name+"/audio.mp3"
        res = requests.get(url, headers=audio_header).content
        with open(path, "ab+")as f:
            f.write(res)
        print("**{}**音频文件下载完成".format(file_name))
    except:
        if flag != 0:
            return down_video(url, file_name, flag-1)  # 遇到错误重试
        else:
            print("**{}**音频文件下载失败".format(file_name))
            return

def get_rank():
    url = "https://www.bilibili.com/v/popular/rank/all"
    res = requests.get(url).text
    soup = BeautifulSoup(res, "html.parser")
    info_list = soup.find_all("div", attrs={"class", "info"})
    video_name, video_url = [], []
    for i in info_list:
        video_name.append(i.a.text)
        video_url.append("https:"+i.a["href"])
    return video_name, video_url

def get_downUrl(name, url, flag=5):
    try:
        header = {}
        header["user-agent"] = get_ua()
        res = requests.get(url, headers=header).text
        soup = BeautifulSoup(res, "html.parser")
        script = soup.find_all("script")
        video_url, audio_url = "", ""
        for i in script:
            if ".m4s" in str(i):
                info_dict = json.loads(re.findall(r"window.__playinfo__=(.*?)</script>", str(i))[0])
                video_url = info_dict["data"]["dash"]["video"][0]["baseUrl"]
                audio_url = info_dict["data"]["dash"]["audio"][0]["baseUrl"]
        with open("./info.txt", "a+", encoding="utf-8")as f:
            f.write(name + "\t" + video_url + "\t" + audio_url + "\n")
    except:
        if flag != 0:
            return get_downUrl(name, url, flag-1)
        else:
            return

def mkdir(file_name):
    file_name = file_name.strip()
    file_name = re.sub('[\\/:*?"<>|]','',file_name)
    if not os.path.exists("./video/"+file_name):
        os.makedirs("./video/"+file_name)
    return True


if __name__ == "__main__":
    names, urls = get_rank()
    with ThreadPoolExecutor(max_workers=100)as t:  # 多线程爬取视频音频下载链接
        all_task = [t.submit(get_downUrl, names[i], urls[i])for i in range(len(names))]
        wait(all_task)

    video_names, video_urls, audio_urls = [], [], []
    for name in video_names:
        mkdir(name)
    with open("./info.txt", "r", encoding="utf-8")as f:
        info = f.readlines()
    for i in info:
        item = i.split("\t")
        video_names.append(item[0].strip())
        video_urls.append(item[1].strip())
        audio_urls.append(item[2].strip())
    
    with ThreadPoolExecutor(max_workers=6)as t:
        task = [t.submit(down_video, video_urls[i],audio_urls[i], video_names[i])for i in range(len(video_names))]
        wait(task)