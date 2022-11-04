#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author: https://github.com/Evil0ctal/
# @Time: 2021/11/06
# @Update: 2022/11/04
# @Version: 3.0.0
# @Function:
# 创建一个接受提交参数的Flask应用程序。
# 将scraper.py返回的内容以JSON格式返回。
# 默认运行端口2333, 请自行在config.ini中修改。

import time
import json

import orjson
import uvicorn
import configparser

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from scraper import Scraper

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
# 运行端口
port = int(config["Web_API"]["Port"])
# 域名
domain = config["Web_API"]["Domain"]

# 创建FastAPI实例
title = "Douyin TikTok Download API(api.douyin.wtf)"
version = '3.0.0'
update_time = "2022/10/31"
description = """
#### Description/说明
<details>
<summary>点击展开/Click to expand</summary>
> [中文/Chinese]
- 爬取Douyin以及TikTok的数据并返回，更多功能正在开发中。
- 如果需要更多接口，请查看[https://api-v2.douyin.wtf/docs](https://api-v2.douyin.wtf/docs)。
- 本项目开源在[GitHub：Douyin_TikTok_Download_API](https://github.com/Evil0ctal/Douyin_TikTok_Download_API)。
- 全部端点数据均来自抖音以及TikTok的官方接口，如遇到问题或BUG或建议请在[issues](https://github.com/Evil0ctal/Douyin_TikTok_Download_API/issues)中反馈。
- 本项目仅供学习交流使用，严禁用于违法用途，如有侵权请联系作者。
> [英文/English]
- Crawl the data of Douyin and TikTok and return it. More features are under development.
- If you need more interfaces, please visit [https://api-v2.douyin.wtf/docs](https://api-v2.douyin.wtf/docs).
- This project is open source on [GitHub: Douyin_TikTok_Download_API](https://github.com/Evil0ctal/Douyin_TikTok_Download_API).
- All endpoint data comes from the official interface of Douyin and TikTok. If you have any questions or BUGs or suggestions, please feedback in [issues](
- This project is for learning and communication only. It is strictly forbidden to be used for illegal purposes. If there is any infringement, please contact the author.
</details>
#### Contact author/联系作者
<details>
<summary>点击展开/Click to expand</summary>
- WeChat: Evil0ctal
- Email: [Evil0ctal1985@gmail.com](mailto:Evil0ctal1985@gmail.com)
- Github: [https://github.com/Evil0ctal](https://github.com/Evil0ctal)
</details>
"""
tags_metadata = [
    {
        "name": "Root",
        "description": "Root path info.",
    },
    {
        "name": "API",
        "description": "Hybrid interface, automatically determine the input link and return the simplified data/混合接口，自动判断输入链接返回精简后的数据。",
    },
    {
        "name": "Douyin",
        "description": "All Douyin API Endpoints/所有抖音接口节点",
    },
    {
        "name": "TikTok",
        "description": "All TikTok API Endpoints/所有TikTok接口节点",
    },
    {
        "name": "Download",
        "description": "Enter the share link and return the download file response./输入分享链接后返回下载文件响应",
    },
    {
        "name": "iOS_Shortcut",
        "description": "Get iOS shortcut info/获取iOS快捷指令信息",
    },
]

# 创建Scraper对象
api = Scraper()

# 创建FastAPI实例
app = FastAPI(
    title=title,
    description=description,
    version=version,
    openapi_tags=tags_metadata
)

""" ________________________⬇️端点响应模型(Endpoints Response Model)⬇________________________"""


# API Root节点
class APIRoot(BaseModel):
    API_status: str
    Version: str = version
    Update_time: str = update_time
    API_V1_Document: str
    API_V2_Document: str
    GitHub: str


# API获取视频基础模型
class iOS_Shortcut(BaseModel):
    version: str = None
    update: str = None
    link: str = None
    link_en: str = None
    note: str = None
    note_en: str = None


# API获取视频基础模型
class API_Video_Response(BaseModel):
    status: str = None
    platform: str = None
    endpoint: str = None
    message: str = None
    total_time: float = None
    aweme_list: list = None


# 混合解析API基础模型:
class API_Hybrid_Response(BaseModel):
    status: str = None
    message: str = None
    endpoint: str = None
    url: str = None
    type: str = None
    platform: str = None
    aweme_id: str = None
    total_time: float = None
    official_api_url: dict = None
    desc: str = None
    create_time: int = None
    author: dict = None
    music: dict = None
    statistics: dict = None
    cover_data: dict = None
    hashtags: list = None
    video_data: dict = None
    image_data: dict = None


# 混合解析API精简版基础模型:
class API_Hybrid_Minimal_Response(BaseModel):
    status: str = None
    message: str = None
    platform: str = None
    type: str = None
    wm_video_url: str = None
    wm_video_url_HQ: str = None
    nwm_video_url: str = None
    nwm_video_url_HQ: str = None
    no_watermark_image_list: list or None = None
    watermark_image_list: list or None = None


""" ________________________⬇️端点日志记录(Endpoint logs)⬇________________________"""


# 记录API请求日志
async def api_logs(start_time, input_data, endpoint, error_data: dict = None):
    time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    total_time = float(format(time.time() - start_time, '.4f'))
    file_name = "API_logs.json"
    # 写入日志内容
    with open(file_name, "a", encoding="utf-8") as f:
        data = {
            "time": time_now,
            "endpoint": f'/{endpoint}/',
            "total_time": total_time,
            "input_data": input_data,
            "error_data": error_data if error_data else "No error"
        }
        f.write(json.dumps(data, ensure_ascii=False) + ",\n")
    return 1


""" ________________________⬇️Root端点(Root endpoint)⬇________________________"""


# Root端点
@app.get("/", response_model=APIRoot, tags=["Root"])
async def root():
    """
    Root path info.
    """
    data = {
        "API_status": "Running",
        "Version": version,
        "Update_time": update_time,
        "API_V1_Document": "https://api.douyin.wtf/docs",
        "API_V2_Document": "https://api-v2.douyin.wtf/docs",
        "GitHub": "https://github.com/Evil0ctal/Douyin_TikTok_Download_API",
    }
    return ORJSONResponse(data)


""" ________________________⬇️混合解析端点(Hybrid parsing endpoints)⬇________________________"""


# 混合解析端点,自动判断输入链接返回精简后的数据
# Hybrid parsing endpoint, automatically determine the input link and return the simplified data.
@app.get("/api", tags=["API"], response_model=API_Hybrid_Response)
async def hybrid_parsing(url: str):
    """
        ## 用途/Usage
        - 获取[抖音|TikTok]单个视频数据，参数是视频链接或分享口令。
        - Get [Douyin|TikTok] single video data, the parameter is the video link or share code.
        ## 参数/Parameter
        #### url(必填/Required)):
        - 视频链接。| 分享口令
        - The video link.| Share code
        - 例子/Example:
        `https://www.douyin.com/video/7153585499477757192`
        `https://v.douyin.com/MkmSwy7/`
        `https://vm.tiktok.com/TTPdkQvKjP/`
        `https://www.tiktok.com/@tvamii/video/7045537727743380782`
        ## 返回值/Return
        - 用户当个视频数据的列表，列表内包含JSON数据。
        - List of user single video data, list contains JSON data.
    """
    print("正在进行混合解析...")
    # 开始时间
    start_time = time.time()
    # 获取数据
    data = api.hybrid_parsing(url)
    # 更新数据
    result = {
        'url': url,
        "endpoint": "/api/",
        "total_time": float(format(time.time() - start_time, '.4f')),
    }
    # 合并数据
    result.update(data)
    # 记录API调用
    await api_logs(start_time=start_time,
                   input_data={'url': url},
                   endpoint='api')
    return ORJSONResponse(result)


@app.get("/api/minimal", tags=["API"], response_model=API_Hybrid_Minimal_Response)
async def hybrid_parsing_minimal(url: str):
    """
        ## 用途/Usage
        - 获取[抖音|TikTok]单个视频数据(精简版-用于给快捷指令使用)，参数是视频链接或分享口令。
        - Get [Douyin|TikTok] single video data (simplified version - for use with shortcut actions), the parameter is the video link or share code.
        ## 参数/Parameter
        #### url(必填/Required)):
        - 视频链接。| 分享口令
        - The video link.| Share code
        - 例子/Example:
        `https://www.douyin.com/video/7153585499477757192`
        `https://v.douyin.com/MkmSwy7/`
        `https://vm.tiktok.com/TTPdkQvKjP/`
        `https://www.tiktok.com/@tvamii/video/7045537727743380782`
        ## 返回值/Return
        - 用户当个视频数据的列表，列表内包含JSON数据。
        - List of user single video data, list contains JSON data.
    """
    print("正在进行最小化混合解析...")
    # 开始时间
    start_time = time.time()
    data = api.hybrid_parsing_minimal(video_url=url)
    # 记录API调用
    await api_logs(start_time=start_time,
                   input_data={'url': url},
                   endpoint='api/minimal')
    return ORJSONResponse(data)


""" ________________________⬇️抖音视频解析端点(Douyin video parsing endpoint)⬇________________________"""


# 获取抖音单个视频数据/Get Douyin single video data
@app.get("/douyin_video_data/", response_model=API_Video_Response, tags=["Douyin"])
async def get_douyin_video_data(douyin_video_url: str = None, video_id: str = None):
    """
    ## 用途/Usage
    - 获取抖音用户单个视频数据，参数是视频链接|分享口令
    - Get the data of a single video of a Douyin user, the parameter is the video link.
    ## 参数/Parameter
    #### douyin_video_url(选填/Optional):
    - 视频链接。| 分享口令
    - The video link.| Share code
    - 例子/Example:
    `https://www.douyin.com/video/7153585499477757192`
    `https://v.douyin.com/MkmSwy7/`
    #### video_id(选填/Optional):
    - 视频ID，可以从视频链接中获取。
    - The video ID, can be obtained from the video link.
    - 例子/Example:
    `7153585499477757192`
    #### 备注/Note:
    - 参数`douyin_video_url`和`video_id`二选一即可，如果都填写，优先使用`video_id`以获得更快的响应速度。
    - The parameters `douyin_video_url` and `video_id` can be selected, if both are filled in, the `video_id` is used first to get a faster response speed.
    ## 返回值/Return
    - 用户当个视频数据的列表，列表内包含JSON数据。
    - List of user single video data, list contains JSON data.
    """
    if video_id is None or video_id == '':
        # 获取视频ID
        video_id = api.get_douyin_video_id(douyin_video_url)
        if video_id is None:
            result = {
                "status": "failed",
                "platform": "douyin",
                "message": "video_id获取失败/Failed to get video_id",
            }
            return ORJSONResponse(result)
    if video_id is not None and video_id != '':
        # 开始时间
        start_time = time.time()
        print('获取到的video_id数据:{}'.format(video_id))
        if video_id is not None:
            video_id = video_id
            video_data = api.get_douyin_video_data(video_id=video_id)
            # print('获取到的video_data:{}'.format(video_data))
            # 记录API调用
            await api_logs(start_time=start_time,
                           input_data={'douyin_video_url': douyin_video_url, 'video_id': video_id},
                           endpoint='douyin_video_data')
            # 结束时间
            total_time = float(format(time.time() - start_time, '.4f'))
            # 返回数据
            result = {
                "status": "success",
                "platform": "douyin",
                "endpoint": "/douyin_video_data/",
                "message": "获取视频数据成功/Got video data successfully",
                "total_time": total_time,
                "aweme_list": [video_data]
            }
            return ORJSONResponse(result)
        else:
            print('获取抖音video_id失败')
            result = {
                "status": "failed",
                "platform": "douyin",
                "endpoint": "/douyin_video_data/",
                "message": "获取视频ID失败/Failed to get video ID",
                "total_time": 0,
                "aweme_list": []
            }
            return ORJSONResponse(result)


""" ________________________⬇️TikTok视频解析端点(TikTok video parsing endpoint)⬇________________________"""


# 获取TikTok单个视频数据/Get TikTok single video data
@app.get("/tiktok_video_data/", response_class=ORJSONResponse, response_model=API_Video_Response, tags=["TikTok"])
async def get_tiktok_video_data(tiktok_video_url: str = None, video_id: str = None):
    """
        ## 用途/Usage
        - 获取单个视频数据，参数是视频链接| 分享口令。
        - Get single video data, the parameter is the video link.
        ## 参数/Parameter
        #### tiktok_video_url(选填/Optional):
        - 视频链接。| 分享口令
        - The video link.| Share code
        - 例子/Example:
        `https://www.tiktok.com/@evil0ctal/video/7156033831819037994`
        `https://vm.tiktok.com/TTPdkQvKjP/`
        #### video_id(选填/Optional):
        - 视频ID，可以从视频链接中获取。
        - The video ID, can be obtained from the video link.
        - 例子/Example:
        `7156033831819037994`
        #### 备注/Note:
        - 参数`tiktok_video_url`和`video_id`二选一即可，如果都填写，优先使用`video_id`以获得更快的响应速度。
        - The parameters `tiktok_video_url` and `video_id` can be selected, if both are filled in, the `video_id` is used first to get a faster response speed.
        ## 返回值/Return
        - 用户当个视频数据的列表，列表内包含JSON数据。
        - List of user single video data, list contains JSON data.
        """
    # 开始时间
    start_time = time.time()
    if video_id is None or video_id == "":
        video_id = api.get_tiktok_video_id(tiktok_video_url)
        if video_id is None:
            return ORJSONResponse({"status": "fail", "platform": "tiktok", "endpoint": "/tiktok_video_data/",
                                   "message": "获取视频ID失败/Get video ID failed"})
    if video_id is not None and video_id != '':
        print('开始解析单个TikTok视频数据')
        video_data = api.get_tiktok_video_data(video_id)
        # 记录API调用
        await api_logs(start_time=start_time,
                       input_data={'tiktok_video_url': tiktok_video_url, 'video_id': video_id},
                       endpoint='tiktok_video_data')
        # 结束时间
        total_time = float(format(time.time() - start_time, '.4f'))
        # 返回数据
        result = {
            "status": "success",
            "platform": "tiktok",
            "endpoint": "/tiktok_video_data/",
            "message": "获取视频数据成功/Got video data successfully",
            "total_time": total_time,
            "aweme_list": [video_data]
        }
        return ORJSONResponse(result)
    else:
        print('视频链接错误/Video link error')
        result = {
            "status": "failed",
            "platform": "tiktok",
            "endpoint": "/tiktok_video_data/",
            "message": "视频链接错误/Video link error",
            "total_time": 0,
            "aweme_list": []
        }
        return ORJSONResponse(result)


""" ________________________⬇️iOS快捷指令更新端点(iOS Shortcut update endpoint)⬇________________________"""


@app.get("/ios", response_model=iOS_Shortcut, tags=["iOS_Shortcut"])
async def Get_Shortcut():
    data = {
        'version': config["Web_API"]["iOS_Shortcut_Version"],
        'update': config["Web_API"]['iOS_Shortcut_Update_Time'],
        'link': config["Web_API"]['iOS_Shortcut_Link'],
        'link_en': config["Web_API"]['iOS_Shortcut_Link_EN'],
        'note': config["Web_API"]['iOS_Shortcut_Update_Note'],
        'note_en': config["Web_API"]['iOS_Shortcut_Update_Note_EN'],
    }
    return ORJSONResponse(data)


""" ________________________⬇️下载文件端点(Download file endpoint)⬇________________________"""


@app.get("/download", tags=["Download"])
async def download_file(url: str):
    pass


if __name__ == '__main__':
    uvicorn.run("web_api:app", port=port, reload=True, access_log=False)
