# !/usr/bin/env python

import requests
from requests.auth import HTTPBasicAuth
import json
from collections import defaultdict
import csv
from datetime import datetime
import os, re
import configparser
import logging  

# 获取当前模块的记录器
logger = logging.getLogger(__name__)

def read_config(config_file='settings.cfg'):
    """读取配置文件"""
    config = configparser.ConfigParser()
    
    # 设置默认值
    config['JIRA'] = {
        'jira_url': 'https://xxx-jira-center/rest/agile/1.0/board',
        'username': 'xxx',
        'password': 'xxxxxxxx',
        'board_id': ''
    }
    
    config['OUTPUT'] = {
        'output_path': './reports',
        'save_detailed_data': 'true',
        'save_csv': 'true',
        'save_json': 'true'
    }
    
    # 读取配置文件
    if os.path.exists(config_file):
        config.read(config_file, encoding='utf-8')
    
    return config

def get_jira_boards(jira_url, username, password):
    """获取JIRA看板列表"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(
            jira_url,
            auth=HTTPBasicAuth(username, password),
            headers=headers,
            verify=True
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"找到 {data['total']} 个看板:")
            logger.info("-" * 80)
            
            boards = []
            for board in data['values']:
                board_info = {
                    'id': board['id'],
                    'name': board['name'],
                    'type': board['type'],
                    'projectKey': board.get('location', {}).get('projectKey', 'N/A'),
                    'projectName': board.get('location', {}).get('projectName', 'N/A'),
                    'self': board.get('self', 'N/A')
                }
                boards.append(board_info)
                
                logger.info(f"ID: {board_info['id']}")
                logger.info(f"名称: {board_info['name']}")
                logger.info(f"类型: {board_info['type']}")
                logger.info(f"项目键: {board_info['projectKey']}")
                logger.info(f"项目名称: {board_info['projectName']}")
                logger.info("-" * 80)
                
            return boards
        else:
            logger.error(f"获取看板列表失败，状态码: {response.status_code}")
            logger.error(f"响应内容: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"获取看板列表时发生错误: {str(e)}")
        return None


def get_all_issues_by_board_id(board_id, jira_url, username, password):
    """根据看板ID获取所有issue（处理分页）"""
    # 如果没有指定board_id，则获取看板列表供用户选择
    if not board_id:
        boards = get_jira_boards(jira_url, username, password)
        if not boards:
            return
        try:
            board_id = input("\n请输入要获取issue的看板ID: ").strip()
        except Exception as e:
            logger.error(f"输入错误: {str(e)}")
            return

    issue_url = f"{jira_url}/{board_id}/issue"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    all_issues = []
    start_at = 0
    max_results = 100  # 每页最大结果数
    
    while True:
        params = {
            "maxResults": max_results,
            "startAt": start_at
        }
        
        try:
            response = requests.get(
                issue_url,
                auth=HTTPBasicAuth(username, password),
                headers=headers,
                params=params,
                verify=True
            )
            
            if response.status_code == 200:
                data = response.json()
                issues = data.get('issues', [])
                all_issues.extend(issues)
                
                # 检查是否还有更多结果
                if start_at + len(issues) >= data.get('total', 0):
                    break
                    
                start_at += len(issues)
                logger.info(f"已获取 {start_at} 个issue...")
            else:
                logger.error(f"获取issue列表失败，状态码: {response.status_code}")
                logger.error(f"响应内容: {response.text}")
                break
                
        except Exception as e:
            logger.error(f"获取issue列表时发生错误: {str(e)}")
            break

    if not all_issues:
        logger.warning("未找到任何issue")
        exit()
    
    logger.info(f"找到 {len(all_issues)} 个issue")
    
    # 提取issue 关键数据
    issue_data_list = []
    for issue in all_issues:
        issue_data = extract_issue_data(issue)
        if issue_data:
            issue_data_list.append(issue_data)
    
    return issue_data_list

def extract_chinese(text):
    """提取字符串中的所有中文字符"""
    # 匹配所有中文字符（包括基本汉字和扩展汉字）
    pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002ebef]+')
    chinese_chars = pattern.findall(text)
    return ''.join(chinese_chars)

def extract_issue_data(issue):
    """从issue中提取所需属性"""
    try:
        # 处理版本信息（可能是数组）
        versions = issue['fields'].get('versions', [])
        version_names = [v.get('name', '') for v in versions] if versions else []
        found_version = ', '.join(version_names) if version_names else '无'
        
        # 处理修复版本信息（可能是数组）
        fix_versions = issue['fields'].get('fixVersions', [])
        fix_version_names = [v.get('name', '') for v in fix_versions] if fix_versions else []
        fix_version = ', '.join(fix_version_names) if fix_version_names else '无'
        
        # 处理严重等级（自定义字段）
        severity_field = issue['fields'].get('customfield_10254')
        severity = severity_field.get('value', '无') if severity_field and isinstance(severity_field, dict) else '无'
        
        # 处理经办人和报告人姓名
        assignee = extract_chinese(issue['fields']['assignee']['displayName'] if issue['fields'].get('assignee') else '未分配')
        reporter = extract_chinese(issue['fields']['reporter']['displayName'] if issue['fields'].get('reporter') else '无')

        # 提取所有需要的字段
        issue_data = {
            'Key': issue['key'],
            'URL': f"https://xxx-jira-home/browse/{issue['key']}", #根据jira url进行修改
            '类型': issue['fields']['issuetype']['name'],
            '状态': issue['fields']['status']['name'],
            '严重等级': severity,
            '创建时间': issue['fields']['created'],
            '更新时间': issue['fields']['updated'],
            '发现版本': found_version,
            '修复版本': fix_version,
            '经办人': assignee,
            '报告人': reporter,
            '标题': issue['fields']['summary']
        }
        
        return issue_data
    except Exception as e:
        logger.error(f"处理issue {issue.get('key', '未知')} 时发生错误: {str(e)}")
        return None

def generate_filename(base_name, project_name, extension, output_path):
    """生成带日期信息的文件名"""
    date_str = datetime.now().strftime("%Y%m%d%H%M")
    filename = f"{base_name}_{project_name}_{date_str}.{extension}"
    return os.path.join(output_path, filename)

def get_issues_info_by_type(issue_data_list, issue_type):

    # 筛选指定类型的issue
    if issue_type == 'All':
        issues = [issue for issue in issue_data_list]
    else:
        issues = [issue for issue in issue_data_list if issue['类型'] == issue_type]
    logger.info(f"其中{issue_type}类型的issue有 {len(issues)} 个")

    # 按状态统计
    issue_status_stats = defaultdict(int)
    for issue_data in issues:
        status = issue_data['状态']
        issue_status_stats[status] += 1

    # 按经办人分组统计
    issue_assignee_stats = defaultdict(lambda: defaultdict(int))
    issue_assignee_totals = defaultdict(int)
    
    for issue_data in issues:
        # 如果bug状态已关闭，则不计入统计
        if issue_data['状态'] != '关闭':
            assignee = issue_data['经办人']
            status = issue_data['状态']
            
            issue_assignee_stats[assignee][status] += 1
            issue_assignee_totals[assignee] += 1
    
    return {'total':len(issues), 'status_total':issue_status_stats, 'assignee_stats':issue_assignee_stats, 'assignee_totals':issue_assignee_totals}

def format_markdown_issue_report(project_name, total, issue_status_stats, issue_assignee_stats, issue_assignee_totals):
    """格式化Bug统计报告为Markdown格式"""
    # 获取当前日期
    current_date = datetime.now().strftime("%Y%m%d%H%M")
    
    # 计算关闭率
    close_rate = round((issue_status_stats.get('关闭', 0) / total) * 100, 2) if total > 0 else 0
    
    # 构建Markdown内容
    markdown_content = f"**【{project_name} JIRA BUG REPORT {current_date}】**\n\n"
    markdown_content += f"BUG总数(**{total}**)："
    markdown_content += f"关闭-{issue_status_stats.get('关闭', 0)}, "
    markdown_content += f"**关闭率-{close_rate}%**\n\n"
    markdown_content += f"**激活-{issue_status_stats.get('激活', 0)}**, "
    markdown_content += f"回归测试-{issue_status_stats.get('回归测试', 0)}, "
    markdown_content += f"已解决-{issue_status_stats.get('已解决', 0)}, "
    markdown_content += f"BUG审核-{issue_status_stats.get('BUG审核', 0)}, "
    markdown_content += f"结果审核-{issue_status_stats.get('结果审核', 0)}\n\n"

    # 按经办人添加详细信息
    for assignee, total in sorted(issue_assignee_totals.items(), key=lambda x: x[1], reverse=True):
        status_counts = issue_assignee_stats[assignee]
        status_list = []
        
        # 按状态数量排序
        for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
            status_list.append(f"{status}-{count}")
        
        markdown_content += f"- {assignee} (总计: {total}): {', '.join(status_list)}\n"
    
    return markdown_content

def jira_issues_fetcher():
    
    # 读取配置文件
    config = read_config()
    jira_config = config['JIRA']
    output_config = config['OUTPUT']
    
    jira_url = jira_config['jira_url']
    username = jira_config['username']
    password = jira_config['password']
    board_id = jira_config['board_id']
    issue_type = jira_config['issue_type']

    project_name = config['PROJECT']['project_name']
    
    # 获取所有issue
    logger.info("正在获取issue列表，请稍候...")
    issue_data_list = get_all_issues_by_board_id(board_id, jira_url, username, password)
    
    logger.info(f"正在统计issue信息，请稍后...")    
    issues_info = get_issues_info_by_type(issue_data_list, issue_type)
    
    # 生成Markdown格式的Bug报告
    markdown_report = format_markdown_issue_report(
        project_name, issues_info['total'], issues_info['status_total'], issues_info['assignee_stats'], issues_info['assignee_totals']
    )

    # 创建输出目录
    output_path = output_config['output_path']
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # 生成带日期的文件名
    issue_stats_filename = generate_filename("jira_issue_report", project_name, "md", output_path)
 
    # 保存Markdown格式的Bug统计报告到文件
    with open(issue_stats_filename, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    logger.info(f"{issue_type}类型issue统计结果已保存到 {issue_stats_filename} (Markdown格式)")
    
    # 根据配置决定是否保存详细数据
    if output_config.getboolean('save_detailed_data'):
        # 保存所有issue数据到CSV文件
        if output_config.getboolean('save_csv') and issue_data_list:
            csv_filename = generate_filename("jira_issues", project_name, "csv", output_path)
            fieldnames = issue_data_list[0].keys()
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for issue_data in issue_data_list:
                    writer.writerow(issue_data)
            
            logger.info(f"所有issue数据已保存到 {csv_filename}")
        
        # 保存所有issue数据到JSON文件
        if output_config.getboolean('save_json'):
            json_filename = generate_filename("jira_issues", project_name, "json", output_path)
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(issue_data_list, f, indent=4, ensure_ascii=False)
            
            logger.info(f"所有issue数据已保存到 {json_filename}")
        
    return markdown_report

if __name__ == "__main__":
    jira_issues_fetcher()
