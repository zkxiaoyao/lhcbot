import os
import random
import json
import logging
import urllib
import time
import hashlib
import requests
import nonebot
from nonebot.rule import Rule
from nonebot import on_command, on_startswith, on_keyword, on_fullmatch, on_message
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageEvent
from nonebot.adapters.onebot.v11 import GROUP_ADMIN, GROUP_OWNER, GROUP_MEMBER
from nonebot.typing import T_State
from nonebot.log import logger
from nonebot.params import ArgPlainText, CommandArg, ArgStr
from nonebot.adapters.onebot.v11 import Bot, GroupIncreaseNoticeEvent, \
    MessageSegment, Message, GroupMessageEvent, Event, escape

SCRIPT_DIR = os.path.dirname(__file__)
IMAGE_FOLDER_NAME = "img"
DATA_FOLDER_NAME = "data"
# 拼接文件夹完整路径
data_directory = os.path.join(SCRIPT_DIR, DATA_FOLDER_NAME)
img_directory = os.path.join(SCRIPT_DIR,IMAGE_FOLDER_NAME)
# 获取脚本文件所在目录




# 定义发送随机七人帮图片的逻辑
async def send_random_image(bot: Bot, event: Event, state: T_State,src:str):
    img_src_directory = os.path.join(img_directory,src)
    # 获取文件夹中的所有文件
    all_files = os.listdir(img_src_directory)
    # 过滤出图片文件（假设只处理 jpg 和 png 格式的图片）
    image_files = [f for f in all_files if f.endswith(('.jpg', '.png', '.jpeg', '.gif'))]
    
    if not image_files:
        await bot.send(event, "文件夹中没有图片。")
        return
    
    # 随机选择一张图片
    selected_image = random.choice(image_files)
    # 构造图片文件的完整路径
    image_path = os.path.join(img_src_directory, selected_image)
    
    # 将图片文件作为消息发送
    await bot.send(event, MessageSegment.image(f"file:///{image_path}"))

# 定义关键词触发命令
keyword_trigger = on_keyword({"七人帮随机一图"}, priority=5, block=True)

@keyword_trigger.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await send_random_image(bot, event, state)

# 定义命令触发命令
command_trigger = on_command("七人帮", priority=5, block=True)

@command_trigger.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await send_random_image(bot, event, state,"qrb")

# 定义命令触发命令
command_trigger = on_command("猫", priority=5, block=True)

@command_trigger.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await send_random_image(bot, event, state,"cat")

# 定义命令触发命令
command_trigger = on_command("狗", priority=5, block=True)

@command_trigger.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await send_random_image(bot, event, state,"dog")