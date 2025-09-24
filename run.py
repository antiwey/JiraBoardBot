# !/usr/bin/env python

import os
import configparser
import jira_issues_fetcher
import dingtalk_bot
import logging
from pathlib import Path


def read_config(config_file='settings.cfg'):
    """读取配置文件"""
    config = configparser.ConfigParser()
    
    # 设置默认值
    config['JIRA'] = {
        'jira_url': 'https://jirauat-sekj.seres.cn/rest/agile/1.0/board',
        'username': '970832',
        'password': 'Swei20250703',
        'board_id': ''
    }
    
    config['OUTPUT'] = {
        'output_path': './reports',
        'save_detailed_data': 'true',
        'save_csv': 'true',
        'save_json': 'true'
    }

    config['LOG'] = {
        'log_level': 'error',
        'log_format': '%%(asctime)s %%(name)-8s %%(levelname)-8s %%(message)s [%%(filename)s:%%(lineno)d]',
    }
    
    # 读取配置文件
    if os.path.exists(config_file):
        config.read(config_file, encoding='utf-8')
    
    return config


def setup_logging():
    # 读取配置文件
    config = read_config()
    log_config = config['LOG']

    log_level = getattr(logging, log_config['log_level'].upper(), None)
    log_format = log_config['log_format']
        
    # 创建根记录器
    logger = logging.getLogger()
    logger.setLevel(log_level)

    output_mode = log_config['log_output_mode']

    # 创建控制台处理器, 控制台输出必选
    handler = logging.StreamHandler()       
    # 创建格式化器
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    # 添加处理器到根记录器
    logger.addHandler(handler)

    if output_mode == 'FILE':
        log_file = log_config['log_path']
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            Path(log_dir).mkdir(parents=True, exist_ok=True)

        # 创建控制台处理器
        handler = logging.FileHandler(log_file, encoding='utf-8')
        
        # 创建格式化器
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        # 添加处理器到根记录器
        logger.addHandler(handler)
    else:
        print('WRONG OUTPUT MODE:', output_mode)

        
# 设置日志配置
setup_logging()
logger = logging.getLogger(__name__)

def main():
    logger.debug('START RUNNING...')

    # 读取配置文件
    config = read_config()
    robot_config = config['ROBOT']
    
    access_token = robot_config['access_token']
    secret = robot_config['secret']
    is_at_all = True if robot_config['is_at_all'] == 'True' else False

    msg = jira_issues_fetcher.jira_issues_fetcher()
    logger.debug("JIRA看板Issue统计工具")
    logger.debug("=" * 50)
    logger.debug(msg)
    
    logger.info('正在发送msg至钉钉群...')
    dingtalk_bot.send_robot_group_message(
        access_token,
        secret,
        msg,
        is_at_all = is_at_all
    )
    
    

if __name__ == '__main__':
    main()
