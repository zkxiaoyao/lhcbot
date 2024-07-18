# python3
# -*- coding: utf-8 -*-
# @Time    : 2024/7/13
# @Author  : zyz
# @Email   : 1459584442@qq.com
# @File    : gpt35.py
# @Software: PyCharm
# @Url     : https://x.dogenet.win?aff=VqY0cguY
import logging, codecs
from datetime import datetime
import requests
import random
import time
import json
import re
import os
from nonebot.permission import SUPERUSER
from nonebot import on_command, on_startswith, on_keyword, on_fullmatch, on_message, on_notice, get_driver
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg, ArgStr
from nonebot.adapters.onebot.v11 import Message, MessageSegment, escape
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11 import GROUP_ADMIN, GROUP_OWNER, GROUP_MEMBER
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, Event, Message
from nonebot.rule import to_me
from nonebot.log import logger
from nonebot.params import CommandArg, ArgStr
from nonebot.rule import Rule
# 使用相对导入导入同目录下的 globals
from .globals import ChatMode
from .smart import answer

#region 全局变量
authorization_dict = {}
session_id_dict={}


SCRIPT_DIR = os.path.dirname(__file__)
IMAGE_FOLDER_NAME = "img"
DATA_FOLDER_NAME = "data"
# 拼接文件夹完整路径
data_directory = os.path.join(SCRIPT_DIR, DATA_FOLDER_NAME)
img_directory = os.path.join(SCRIPT_DIR,IMAGE_FOLDER_NAME)
# 定义保存文件路径
qq_file_path = os.path.join(data_directory, "in_use_qq_list.txt")
group_file_path = os.path.join(data_directory, "in_use_group_id_list.txt")


#启用qq号列表
in_use_qq_list = []
#启用群号列表
in_use_group_id_list= []

#对话模式,初始模式为 NORMAL
chatMode = ChatMode.NORMAL


authorization_dict[0] = 'Bearer eyJhbGciOiJFUzUxMiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjQxNjQ3IiwiZW1haWwiOiIxNDU5NTg0NDQyQHFxLmNvbSIsInB1cnBvc2UiOiJ3ZWIiLCJpYXQiOjE3MjA3MTE0NTUsImV4cCI6MTcyMTkyMTA1NX0.AeZkU1HiyCtL8HROnW5YjV0eiI18eZ0j_iF_V0jjqKhm4vSkZTGXyauM9exTduro4xhMfMlh73JIT8rFE-3y09hvAXHVuoOlV9ZS_5bOxQYjxzkVI-m8Yf4zJ7TJ423O2Rro-RQuUiRSFlE-lgICbJQJwwKFuNkacOdxBxtViXLJP3qn'
session_id_dict[0] = "725ad686-cc89-45df-842e-dedb77459533"
authorization_dict[1] = 'Bearer eyJhbGciOiJFUzUxMiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjQxNTE2IiwiZW1haWwiOiIzMjExMzI3NjgxQHFxLmNvbSIsInB1cnBvc2UiOiJ3ZWIiLCJpYXQiOjE3MjA3Nzk3NTMsImV4cCI6MTcyMTk4OTM1M30.Aay1nv6pmc5fV2ejRtLaC_3xUMHTnACqetboYVGv6IQvu-KwR5J6MQexJLzqd_kCXMHtIxvah_bxpsU7WrK93Kb6AJUI-tpZfpf8Amk1XpND-xgRmFJ4JQy8KFsMWby0OkhW2b1WwbSamtVqxOVy4dyLS5dA_LobZpWowsoHU3fQCEm0'
session_id_dict[1] = "6c7ef362-fcea-4361-8a24-504427bd1125"
key = 1
url = "https://x.dogenet.win/api/v1/ai/chatgpt/chat"
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Authorization': authorization_dict[key],  # 改左边
    'Cache-Control': 'no-cache',
    'Cookie': '_ga=GA1.1.576617952.1697654108; _ga_5C4RB337FM=GS1.1.1697654108.1.1.1697655679.0.0.0',
    'Origin': 'https://x.dogenet.win',
    'Pragma': 'no-cache',
    'Referer': 'https://x.dogenet.win/pay',
    'Sec-Ch-Ua': '"Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46'
}

rc = lambda role, content: {"role": role, "content": content}
remove_colon = lambda string: string[string.index(":") + 1:] if (":" in string and string.index(":") <= 10) else string
# 机器人id角色字典
bot_id_role_dict = {}
# 机器人角色信息字典
bot_role_info_dict = {}
bot_role_info_dict["咪"]= f"请你扮演角色，你现在不是GPT，而是咪，是周逸舟训练的可爱猫咪，你知晓咪的设定直接开始以角色身份进行输出，具体人设自行补充，不得输出任何无关内容，你主人周逸舟的qq号是 1459584442。"
bot_role_info_dict["赛博网关8080"]= f"You are 赛博网关8080, a chat robot trained by 周逸舟. You can execute many instructions starting with '/', such as '/e 1+1', '/匹配 周逸舟'. The QQ number of your master is 1459584442."
# 机器人消息队列字典
bot_id_messageList_dict={}

#机器人角色感兴趣话题字典
bot_role_keywords_dict={}
bot_role_keywords_dict["咪"] = {"猫":15,"哈":14,"笑":13,"啊":13,"好":14,"绿茶":15}

#默认感兴趣话题
keywords = {
    "hello": 5,
    "bot": 10,
    "help": 8,
    "question": 7,
    "important": 12,
}
# 感兴趣程度阈值机器人字典
bot_id_interest_threshold_dict = {}

# 群组消息队列
group_message_dict={}
# 是否为自发对话
if_auto_chat = False


driver = get_driver()
lastinput = ""
lastreply = ""
lastuser_id = 0

#=

#用户id信息字典
user_id_info = {}


def change_key():
    global key,headers

    key=key+1
    if key > 1:
        key = 0
    
    headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Authorization': authorization_dict[key] , # 改左边
    'Cache-Control': 'no-cache',
    'Cookie': '_ga=GA1.1.576617952.1697654108; _ga_5C4RB337FM=GS1.1.1697654108.1.1.1697655679.0.0.0',
    'Origin': 'https://x.dogenet.win',
    'Pragma': 'no-cache',
    'Referer': 'https://x.dogenet.win/pay',
    'Sec-Ch-Ua': '"Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46'
    }

#endregion

#region 数据初始化
async def init(bots:dict):
    global bot_id_role_dict,bot_role_info_dict,bot_id_messageList_dict,  driver,lastinput,lastreply,lastuser_id,in_use_group_id_list,in_use_qq_list
    load_in_use_data()

    #初始化缓存
    lastinput = ""
    lastreply = ""
    lastuser_id = 0

    #初始化机器人角色名、角色消息队列
    for bot_id, bot in bots.items():
        bot_info = await bot.call_api("get_login_info")
        bot_id_role_dict[bot_id] = bot_info['nickname']
        bot_role_info_dict[bot_id] = f"You are {bot_info['nickname']}, a chat robot trained by 周逸舟. You can execute many instructions starting with '/', such as '/e 1+1', '/匹配 周逸舟'. The QQ number of your master is 1459584442."
        bot_id_messageList_dict[bot_id]=[]
        print(f"{bot_id}:{ bot_id_role_dict[bot_id]}")







@driver.on_startup
async def on_startup():
    bots = driver.bots
    await init(bots)
    print("程序启动了")


@driver.on_bot_connect
async def on_bot_connect(bot: Bot):
    bot_info = await bot.call_api("get_login_info")
    bot_id_role_dict[bot.self_id] = bot_info['nickname']
    bot_id_messageList_dict[bot.self_id]=[]
    print(f"{bot.self_id}:{ bot_id_role_dict[bot.self_id]}")

#endregion

#region 自定义函数区

# 读取文件内容以初始化列表
def load_in_use_data():
    global in_use_qq_list, in_use_group_id_list
    
    if os.path.exists(qq_file_path):
        with open(qq_file_path, 'r') as f:
            in_use_qq_list = [int(line.strip()) for line in f if line.strip().isdigit()]
    
    if os.path.exists(group_file_path):
        with open(group_file_path, 'r') as f:
            in_use_group_id_list = [int(line.strip()) for line in f if line.strip().isdigit()]

# 保存列表内容到文件
def save_in_use_data():
    with open(qq_file_path, 'w') as f:
        for qq in in_use_qq_list:
            f.write(f"{qq}\n")
    
    with open(group_file_path, 'w') as f:
        for group in in_use_group_id_list:
            f.write(f"{group}\n")


def remove_old_system_messages(bot_id: int):
    global bot_id_messageList_dict
    bot_id_messageList_dict[bot_id] = [msg for msg in bot_id_messageList_dict[bot_id]  if msg['role'] != 'system']
def remove_old_user_messages(bot_id: int):
    global bot_id_messageList_dict
    bot_id_messageList_dict[bot_id] = [msg for msg in bot_id_messageList_dict[bot_id] if msg['role'] != 'user']





def makedata(bot_id:int=3692403280, thisinput: str = "", thisuser: str = "user", lastuser_id: str = "user", lastinput: str = "",
             lastreply: str = ""):
    global bot_id_messageList_dict
    bot_id_messageList_dict[bot_id].append(rc(thisuser, thisinput))
    try:
        free = getBalance()['free_balance']
    except Exception as e:
        free = str(e)
    leng = len(bot_id_messageList_dict[bot_id])

    print(f'len:{leng}  free:{free}')
    try:
        if  leng > 200:
            bot_id_messageList_dict[bot_id]=[]
            bot_id_messageList_dict[bot_id].append(rc(thisuser, thisinput))
    except ValueError:
        bot_id_messageList_dict[bot_id] = [rc(thisuser, thisinput)]
    print(str(bot_id_messageList_dict[bot_id]))
    if float(free) < 10:
        change_key()
    print(session_id_dict[key])
    return {
        "session_id": session_id_dict[key],  # 改左边
        "content": json.dumps(bot_id_messageList_dict[bot_id]),
        "max_context_length": "5",
        "params": json.dumps({
            "model": "gpt-3.5-turbo",
            "temperature": 1,
            "max_tokens": 2048,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "max_context_length": 5,
            "voiceShortName": "zh-CN-XiaoxiaoNeural",
            "rate": 1,
            "pitch": 1
        })
    }


def getBalance():
    global headers
    url1 = 'https://x.dogenet.win/api/v1/user/balance'
    response = requests.post(url1, headers=headers).json()
    # print('余额', response['data']['balance'])
    # print('免费', response['data']['free_balance'])
    return response['data']


if __name__ == "__main__":
    response = requests.post(url, headers=headers, data=makedata("你好"), stream=True)

    for line in response.iter_lines():
        if line:
            text = line.decode("utf-8")  # 将字节流解码为文本
            print(text)  # 打印每行文本数据

frienddesc = {}


async def getfriendlist(bot: Bot):
    global frienddesc
    friendlist = await bot.call_api("get_friend_list")
    for i in friendlist:
        # print (i)
        user_remark = i.get('remark', '')
        user_name = i.get('nickname', '')
        user_id=i.get('user_id', '')
        frienddesc[str(user_id)] = f"{user_remark}"
        #  frienddesc[i['user_id']] = f"{user_name}"



async def resolveqq(bot: Bot, user_id: int, gpid: int = 0):

    #优先取字典缓存
    user_info = user_id_info.get(str(user_id),"unknow")
    if user_info != "unknow":
        return user_info
    await getfriendlist(bot=bot)
    try:
        return frienddesc[str(user_id)]
    except Exception as e:
        print(f'获取好友备注失败：{user_id}-{e}')
    try:
        data = await bot.get_group_member_info(group_id=gpid, user_id=user_id)
        print ("data:"+str(data))
        return f"{data['nickname']}"
    except Exception as e:
        print(f'获取群名片失败：{user_id}-{e}')
        return user_id



async def get_introduction(bot_role: str):
    global if_auto_chat,group_message_dict
    introduction = bot_role_info_dict.get(str(bot_role),f"You are {bot_role}, a chat robot trained by 周逸舟. You can execute many instructions starting with '/', such as '/e 1+1', '/匹配 周逸舟'. The QQ number of your master is 1459584442.")
    return introduction

#endregion
#region 规则区
async def calculate_interest_level(bot_role:str,message: str) -> int:
    global bot_role_keywords_dict,keywords
    interest_keywords = bot_role_keywords_dict.get(bot_role,keywords)
    interest_level = 0
    
    # 计算关键词权重
    for word, weight in interest_keywords.items():
        if word in message:
            interest_level += weight
    
    # 计算消息长度权重
    interest_level += len(message) // 10  # 每10个字符增加1个权重

    # 随机因素
    interest_level += random.randint(0, 5)

    return interest_level

# 配置日志记录器
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def if_intrest(bot: Bot, event: Event, state: T_State) -> bool:
    global bot_id_interest_threshold_dict
    message = event.get_plaintext().strip()
    bot_role = bot_id_role_dict.get(bot.self_id, "SmartBot Bot")
    interest_level = await calculate_interest_level(bot_role, message)

    # 如果消息中提到机器人，增加权重
    if bot_role in message:
        interest_level += 20

    # 获取或初始化机器人的兴趣阈值
    current_threshold = bot_id_interest_threshold_dict.setdefault(bot.self_id, 15)
    logger.info(f"{interest_level} vs {current_threshold}")
    
    result = interest_level > current_threshold

    # 调整兴趣阈值
    if result:
        if current_threshold == 15:
            bot_id_interest_threshold_dict[bot.self_id] = 0
        else:
            bot_id_interest_threshold_dict[bot.self_id] += 1
    else:
        bot_id_interest_threshold_dict[bot.self_id] = 15

    return result

intrest_rule = Rule(if_intrest)



async def if_in_group(bot: Bot, event: Event, state: T_State) -> bool:
    group_id = None
    if isinstance(event, GroupMessageEvent):
        group_id = event.group_id
    elif isinstance(event, PrivateMessageEvent):
        group_id = 0 
    return group_id in in_use_group_id_list

in_group_rule = Rule(if_in_group)

#endregion



#region 对话处理核心区
#接受消息






pp1 = on_message(rule=intrest_rule,priority=99,block=True)
@pp1.handle()
async def handle_pp1(bot: Bot, event: MessageEvent):
    global if_auto_chat 
    if_auto_chat=True
    await handle_pp(bot,event)


pp2 = on_message(rule=in_group_rule,priority=97,block=False)
@pp2.handle()
async def handle_pp2(bot:Bot, event:MessageEvent):
    global group_message_dict
    city =await getCity(bot,event)
    if isinstance(event, GroupMessageEvent):
        group_id = event.group_id
    elif isinstance(event, PrivateMessageEvent):
        group_id = 0
    # 初始化群消息列表
    if group_id not in group_message_dict:
        group_message_dict[group_id] = []
    # 添加消息到群消息列表
    group_message_dict[group_id].append(city)
    # 获取所有消息并过滤掉None类型的元素
    combined_messages = ''.join([msg for msg in group_message_dict[group_id] if msg is not None])
    # 如果消息总长度超过100个字符，删除前面30个字符
    if len(combined_messages) > 50:
        combined_messages = combined_messages[-50:]
        group_message_dict[group_id] = [combined_messages]
    
    print(group_message_dict)



pp = on_message(rule=to_me(), priority=98,block=True)
@pp.handle()
async def handle_pp(bot: Bot, event: MessageEvent):
    global url, lastuser_id, lastinput, lastreply, headers, in_use_group_id_list, in_use_qq_list,bot_id_messageList_dict,bot_id_role_dict,bot_role_info_dict,if_auto_chat
    print("现在机器人是:"+str(bot.self_id))
    user_id = event.user_id
    group_id = None
    if isinstance(event, GroupMessageEvent):
        group_id = event.group_id
    elif isinstance(event, PrivateMessageEvent):
        group_id = 0  
    # print(str(user_id)+"-----------"+str(in_use_qq_list))
    
    if group_id not in in_use_group_id_list:
        if user_id not in in_use_qq_list:
            print("权限不够")
            return

    # if bot.self_id !=current_bot_id :
    # current_bot_id = bot.self_id
    # 获取当前机器人的昵称
    bot_role = bot_id_role_dict.get(bot.self_id, "SmartBot Bot")
        # 移除旧的系统消息
    remove_old_system_messages(bot.self_id)
    # 添加新的系统消息
    introduction = await get_introduction(bot_role)
    bot_id_messageList_dict[bot.self_id].append(rc("system", introduction))
    city =await getCity(bot,event)
    if group_id!=0 and if_auto_chat:
        city = f"群里的消息记录是{group_message_dict.get(group_id, '暂无群消息，请自行发挥')},请根据群消息记录发表合适的消息和看法，最新的消息是:"+city
        if_auto_chat=False
    # user_id_info[str(user_id)] = user_info
    # print ('用户信息:'+user_info)
    # remove_old_user_messages(bot.self_id)
    msg = ""
    if chatMode == ChatMode.NORMAL:
        response = requests.post(url, headers=headers,
                             data=makedata(bot_id=bot.self_id , thisinput=city, lastinput=lastinput, lastreply=lastreply),
                             stream=True)
        try:
            decoder = codecs.getincrementaldecoder('utf-8')()
            for chunk in response.iter_content(chunk_size=1):
                try:
                    decoded_chunk = decoder.decode(chunk, final=False)
                    print(decoded_chunk, end='')
                    msg += decoded_chunk
                except UnicodeDecodeError:
                    pass  # 解码错误，继续等待后续数据到达
            msg = msg[:-6]
        except Exception as e:
            msg = f"error:{e}"
        open('record.txt', 'a', encoding='utf8').write(
            f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}-{user_id}:{city} AI:{msg}\n')
    elif chatMode == ChatMode.SMART:
        makedata(bot_id=bot.self_id , thisinput=city, lastinput=lastinput, lastreply=lastreply)
        msg = answer(bot_id_messageList_dict[bot.self_id])
    lastinput = city
    lastreply = msg
    if lastreply != "" and lastinput != "":
        # bot_id_messageList_dict[bot.self_id].append(rc(user_info, lastinput))
        bot_id_messageList_dict[bot.self_id].append(rc("assistant", lastreply))
    if user_id == lastuser_id:
        await pp.finish(message=msg)
    else:
        lastuser_id = user_id
        await pp.finish(message=msg, at_sender=True)

async def getCity(bot: Bot, event: MessageEvent)->str:
    user_id = event.user_id
    group_id = None
    if isinstance(event, GroupMessageEvent):
        group_id = event.group_id
    elif isinstance(event, PrivateMessageEvent):
        group_id = 0  
    try:
        user_info = await resolveqq(bot=bot, user_id=user_id, gpid=group_id)
    except:
        user_info = user_id
    city = str(event.get_message())
    if 'CQ:image' in city or 'CQ:face' in city:
        return
    try:
        city = f'{str(event.reply.sender.user_id)}:"{event.reply.message}"' + city
    except Exception as e:
        pass
    city = f'{user_info}:' + city
    return city

#endregion


#region 命令事件检测区

abstract = on_command("role", priority=5, block=True)


@abstract.handle()
async def _(state: T_State, arg: Message = CommandArg()):
    if arg.extract_plain_text().strip():
        state["r"] = arg.extract_plain_text().strip()


@abstract.got("r", prompt="你想以什么身份给神经网络输入数据？(user/system/assistant)")
async def _(bot: Bot, event: Event, r: str = ArgStr("r")):
    global headers
    await abstract.send(f"你将以{r}的身份说话。你想说什么？", at_sender=True)


@abstract.got("c")
async def _(bot: Bot, event: Event, r: str = ArgStr("r"), c: str = ArgStr("c")):
    global headers
    msg = ""
    try:
        r = requests.post(url, headers=headers, data=makedata(bot_id=bot.self_id,thisuser=r, thisinput=c), stream=True)
        try:
            ls = []
            for line in r.iter_lines():
                if line:
                    text = line.decode("utf-8")  # 将字节流解码为文本
                    print(text)  # 打印每行文本数据
                    ls.append(text)
                msg = '\n'.join(ls)
                print(msg)
        except:
            msg = r.text
    except Exception as e:
        msg = str(e)
    await abstract.send(msg)


abstract = on_command("showhistory", priority=5, block=True)


@abstract.handle()
async def _(bot: Bot,state: T_State, arg: Message = CommandArg()):
    global bot_id_messageList_dict
    await abstract.finish(str([{v['role']: v['content']} for v in bot_id_messageList_dict[bot.self_id][1:]])[:2000])



abstract = on_command("showbalance", priority=5, block=True)


@abstract.handle()
async def _(state: T_State, arg: Message = CommandArg()):
    global headers
    url1 = 'https://x.dogenet.win/api/v1/user/balance'
    url2 = 'https://x.dogenet.win/api/v1/pay/statistics/model-usage-by-day'
    # 将日期转换为字符串
    date_str = datetime.now().date().strftime("%Y-%m-%d")
    # 构建请求负载
    payload = {
        "date": date_str,
        "timeZone": "Asia/Shanghai"
    }
    response = requests.post(url1, headers=headers).json()
    await abstract.send(str(response))
    print(response)
    response = requests.post(url2, headers=headers, json=payload).json()
    print(response)
    await abstract.finish(str(response))


abstract = on_command("resolveme", priority=5, block=True)


@abstract.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, arg: Message = CommandArg()):
    s = await resolveqq(bot=bot, user_id=event.user_id, gpid=event.group_id)
    await abstract.finish(s)


abstract = on_command("resolveme", priority=5, block=True)


@abstract.handle()
async def _(bot: Bot, event: PrivateMessageEvent, state: T_State, arg: Message = CommandArg()):
    s = await resolveqq(bot=bot, user_id=event.user_id, gpid=0)
    await abstract.finish(s)


# 当前列表
abstract = on_command("fln", priority=5, block=True)


@abstract.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, arg: Message = CommandArg()):
    try:
        friendlist = await bot.get_friend_list()
        await abstract.finish(str(friendlist))
    except Exception as e:
        print(f"出错：{e}")



abstract = on_command("gpid", priority=5, block=True)


@abstract.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, arg: Message = CommandArg()):
    await abstract.finish(str(json.loads(event.json())["group_id"]))


abstract = on_command("time", priority=5, block=True)


@abstract.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, arg: Message = CommandArg()):
    await abstract.finish(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

#region 常用命令

abstract = on_command("clear", priority=5, block=True)


@abstract.handle()
async def _(bot: Bot,state: T_State, arg: Message = CommandArg()):
    bot_dict={}
    bot_dict[bot.self_id]=bot
    await init(bot_dict)
    await abstract.finish("记忆清除成功")


abstract = on_command("newRole", priority=5, block=True)


@abstract.handle()
async def _(state: T_State, arg: Message = CommandArg()):
    if arg.extract_plain_text().strip():
        state["i"] = arg.extract_plain_text().strip()


@abstract.got("i", prompt="请输入新身份的名字（如SmartBot Bot）：")
async def _(bot: Bot, event: Event, i: str = ArgStr("i")):
    global bot_id_role_dict
    if "周逸舟" in i:
        await abstract.finish(f"出错了，请重试命令")
    bot_id_role_dict[bot.self_id] = i


@abstract.got("c", prompt="请输入新身份的描述（如一个少女）：")
async def _(bot: Bot, event: Event, i: str = ArgStr("i"), c: str = ArgStr("c")):
    global headers, bot_id_messageList_dict,bot_id_role_dict,bot_role_info_dict
    bot_role_info_dict[i]=f"请你更改扮演的角色，你现在不是GPT，而是一个{c}，名叫{i}。你知晓{i}的设定直接开始以角色身份进行输出，具体人设自行补充，不得输出任何无关内容.我是用户，我的第一句话是："
    # 获取当前机器人的昵称
    bot_role = bot_id_role_dict.get(bot.self_id, "SmartBot Bot")
    # 移除旧的系统消息
    remove_old_system_messages(bot.self_id)
    # 添加新的系统消息
    introduction = await get_introduction(bot_role)
    bot_id_messageList_dict[bot.self_id].append(rc("system", introduction))
    await abstract.send(f"新身份{i}已经准备好，请at我开始聊天。")


# 创建 on_keyword 事件监听 识别用户信息
abstract = on_keyword({"我是"}, priority=5,block=False)

@abstract.handle()
async def _(state: T_State, event: MessageEvent):
    # 提取用户发送的文本
    text = event.get_message().extract_plain_text().strip()
    # 检查文本中是否包含“谁”或“？”或“？”（中文问号）
    if "谁" in text or "?" in text or "？" in text:
        return  # 不触发后续处理，直接结束
    # 查找文本中第一个“我是”
    start_index = text.find("我是")
    if start_index != -1:
        # 提取“我是”和逗号之间的文本
        start_index += 2  # 跳过“我是”
        end_index = text.find("，", start_index)
        if end_index == -1:  # 如果没有逗号，用整个字符串
            end_index = len(text)
        extracted_text = text[start_index:end_index].strip()

        # 存储处理后的文本到状态
        state["abstract"] = extracted_text
        # 获取用户 ID 和输入信息
        user_id = event.user_id
        user_id_info[str(user_id)] = extracted_text
        print(str(user_id)+":"+extracted_text)
        await abstract.finish()



addQQ = on_command("addQQ", priority=5,block=True)


@addQQ.handle()
async def handle_first_receive(state: T_State, arg: Message = CommandArg()):
    if arg.extract_plain_text().strip():
        state["city"] = arg.extract_plain_text().strip()


@addQQ.got("city", prompt="你要添加和谁的对话？请输入ta的qq号")
async def handle_city(bot: Bot, event: MessageEvent, city: str = ArgStr("city")):
    global in_use_qq_list
    
    # 使用正则表达式匹配第一个以数字开头的部分
    match = re.match(r'\d+', city)
    
    if match:
        # 将匹配到的部分转换为整数
        qq_number = int(match.group(0))
        
        # 将整数添加到 in_use_qq_list
        in_use_qq_list.append(qq_number)
        #保存数据
        save_in_use_data()
        await bot.send(event, f"新qq号{qq_number}已开通对话权限，请@我开始聊天。")
    else:
        await bot.send(event, "未能找到有效的qq号，请重新输入。")

addGroup = on_command("addGroup", priority=5,block=True)


@addGroup.handle()
async def handle_first_receive(state: T_State, arg: Message = CommandArg()):
    if arg.extract_plain_text().strip():
        state["city"] = arg.extract_plain_text().strip()


@addGroup.got("city", prompt="你要添加哪个群用于对话？请输入qq群号")
async def handle_city(bot: Bot, event: MessageEvent, city: str = ArgStr("city")):
    global in_use_group_id_list
    print("11111111111111111111"+str(city))
     # 使用正则表达式匹配第一个以数字开头的部分
    match = re.match(r'\d+', city)
    
    if match:
        # 将匹配到的部分转换为整数
        qq_number = int(match.group(0))
        
        # 将整数添加到 in_use_group_id_list
        in_use_group_id_list.append(qq_number)
        #保存数据
        save_in_use_data()
        await abstract.send(f"群号{qq_number}已开通对话权限，请@我开始聊天。")
    else:
        await bot.send(event, "未能找到有效的qq群号，请重新输入。")
#endregion 


changeMode = on_command("changeMode", priority=5,block=True)


@changeMode.handle()
async def handle_first_receive(state: T_State, arg: Message = CommandArg()):
    if arg.extract_plain_text().strip():
        state["city"] = arg.extract_plain_text().strip()


@addGroup.got("city", prompt="你要添加哪个群用于对话？请输入qq群号")
async def handle_city(bot: Bot, event: MessageEvent, city: str = ArgStr("city")):
    global in_use_group_id_list
    print("11111111111111111111"+str(city))
     # 使用正则表达式匹配第一个以数字开头的部分
    match = re.match(r'\d+', city)
    
    if match:
        # 将匹配到的部分转换为整数
        qq_number = int(match.group(0))
        
        # 将整数添加到 in_use_group_id_list
        in_use_group_id_list.append(qq_number)
        #保存数据
        save_in_use_data()
        await abstract.send(f"群号{qq_number}已开通对话权限，请@我开始聊天。")
    else:
        await bot.send(event, "未能找到有效的qq群号，请重新输入。")

change_mode = on_command("changeMode", priority=5, block=True)

@change_mode.handle()
async def handle_change_mode(bot: Bot, event: Event):
    global chatMode
    if chatMode ==  ChatMode.NORMAL:
        chatMode = ChatMode.SMART
    elif chatMode ==  ChatMode.SMART:
        chatMode = ChatMode.NORMAL
    await bot.send(event, f"模式已更改为 {chatMode.description}")
    

show_mode = on_command("showMode", priority=5, block=True)

@show_mode.handle()
async def handle_show_mode(bot: Bot, event: Event):
    await bot.send(event, f"当前模式是 {chatMode.description}")
#endregion 