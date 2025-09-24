# !/usr/bin/env python

import argparse
import logging
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests

import logging  

# 获取当前模块的记录器
logger = logging.getLogger(__name__)


def define_options():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--access_token', dest='access_token', required=True,
        help='机器人webhook的access_token from https://open.dingtalk.com/document/orgapp/obtain-the-webhook-address-of-a-custom-robot '
    )
    parser.add_argument(
        '--secret', dest='secret', required=True,
        help='secret from https://open.dingtalk.com/document/orgapp/customize-robot-security-settings#title-7fs-kgs-36x'
    )
    parser.add_argument(
        '--userid', dest='userid',
        help='待 @ 的钉钉用户ID，多个用逗号分隔 from https://open.dingtalk.com/document/orgapp/basic-concepts-beta#title-o8w-yj2-t8x '
    )
    parser.add_argument(
        '--at_mobiles', dest='at_mobiles',
        help='待 @ 的手机号，多个用逗号分隔'
    )
    parser.add_argument(
        '--is_at_all', dest='is_at_all', action='store_true',
        help='是否@所有人，指定则为True，不指定为False'
    )
    parser.add_argument(
        '-msg', dest='msg', default='钉钉，让进步发生',
        help='要发送的消息内容'
    )
    return parser.parse_args()


def send_robot_group_message(access_token, secret, msg, at_user_ids=None, at_mobiles=None, is_at_all=False):
    """
    发送钉钉自定义机器人群消息
    :param access_token: 机器人webhook的access_token
    :param secret: 机器人安全设置的加签secret
    :param msg: 消息内容
    :param at_user_ids: @的用户ID列表
    :param at_mobiles: @的手机号列表
    :param is_at_all: 是否@所有人
    :return: 钉钉API响应
    """
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f'{timestamp}\n{secret}'
    hmac_code = hmac.new(secret.encode('utf-8'), string_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

    url = f'https://oapi.dingtalk.com/robot/send?access_token={access_token}&timestamp={timestamp}&sign={sign}'
    body = {
        "at": {
            "isAtAll": str(is_at_all).lower(),
            "atUserIds": at_user_ids or [],
            "atMobiles": at_mobiles or []
        },
        "markdown": {
            "title": "JIRA REPORT",
            "text": msg
        },
        "msgtype": "markdown"
    }
    headers = {'Content-Type': 'application/json'}
    try:
        logger.info("发送机器人群发消息请求到群组")
        logger.debug("发送机器人群发消息请求到: %s", url)
        resp = requests.post(url, json=body, headers=headers, timeout=30)
        
        logger.info("响应状态码: %s, 内容: %s", resp.status_code, resp.text)
        resp.raise_for_status()
        
        return resp.json()
        
    except requests.exceptions.Timeout:
        logger.error("请求超时: %s", url)
        return None
        
    except requests.exceptions.ConnectionError:
        logger.error("连接失败: %s", url)
        return None
        
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else "未知"
        logger.error("HTTP错误 (状态码 %s): %s", status_code, str(e))
        return None
        
    except Exception as e:
        logger.exception("请求异常: %s", str(e))
        return None


def main():
    options = define_options()
    # 处理 @用户ID
    at_user_ids = []
    if options.userid:
        at_user_ids = [u.strip() for u in options.userid.split(',') if u.strip()]
    # 处理 @手机号
    at_mobiles = []
    if options.at_mobiles:
        at_mobiles = [m.strip() for m in options.at_mobiles.split(',') if m.strip()]
    logger.debug('send_robot_group_message')
    
    send_robot_group_message(
        options.access_token,
        options.secret,
        options.msg,
        at_user_ids=at_user_ids,
        at_mobiles=at_mobiles,
        is_at_all=options.is_at_all
    )
    

if __name__ == '__main__':
    main()
