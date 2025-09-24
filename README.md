# JiraDingtalkBot

## 简介
JiraDingtalkBot 是一个自动化工具，用于从JIRA看板获取Issue统计信息，并通过钉钉机器人发送统计报告。支持按类型筛选 Issue、按状态和经办人统计，并生成格式化的 Markdown 报告。

## 功能特性
- 🔍 自动获取 JIRA 看板 Issue 数据
- 📊 按状态和经办人进行统计分析
- 📝 生成 Markdown 格式的统计报告
- 🤖 通过钉钉机器人发送群消息
- ⚙️ 配置文件化管理各项参数
- 📁 支持多种输出格式（CSV、JSON、Markdown）


## 环境要求
- Python 3.6+
- 访问 JIRA 服务器的权限
- 钉钉群机器人配置

## 安装步骤
### 1. 手动安装依赖
```bash
# 安装依赖库
pip install -r requirements.txt
```

### 2. 文件准备
jira-board-bot/
├── jira_issues_fetcher.py  # 获取jira issues 数据
├── dingtalk_bot.py         # 钉钉机器人模块
├── settings.cfg            # 配置管理文件
├── run.py                  # 启动脚本
└── requirements.txt        # 需手动安装的依赖模块

### 3. 配置修改
编辑 settings.cfg 文件，根据自身环境修改配置：
#### JIRA 配置段
- jira_url: JIRA REST API 地址
- username/password: JIRA 登录凭据
- board_id: 要统计的看板 ID（留空可查看所有看板列表）
- issue_type: Issue 类型筛选（All/Bug）

#### 机器人配置段
- access_token: 钉钉机器人 Webhook 的 access_token
- secret: 机器人安全设置的加签密钥
- is_at_all: 是否@所有人

#### 输出配置段
- output_path: 报告文件保存路径
- save_detailed_data: 是否保存详细数据
- save_csv/save_json: 输出格式选择

#### 日志配置段
- log_level: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
- log_output_mode: 输出方式（CONSOLE_ONLY/FILE）
- log_path: 日志文件路径

#### 输出文件
程序运行后会生成以下文件：
- jira_issue_report_项目名_时间戳.md - Markdown 格式统计报告
- jira_issues_项目名_时间戳.csv - CSV 格式详细数据（可选）
- jira_issues_项目名_时间戳.json - JSON 格式详细数据（可选）


## 使用方法
### 运行
在根目录下运行指令：
```bash
python run.py
```

## 钉钉消息格式
发送的消息包含以下信息：
- BUG 总数和关闭率
- 各状态 BUG 数量统计
- 按经办人的详细统计

## 故障排除
### 常见问题
1. JIRA 连接失败
   - 检查网络连接和 JIRA 服务器地址
   - 验证用户名和密码是否正确
   - 确认有访问指定看板的权限
2. 钉钉消息发送失败
   - 检查 access_token 和 secret 是否正确
   - 确认机器人已添加到目标群组
   - 验证网络连接是否正常
3. 配置文件错误
   - 确保 settings.cfg 文件格式正确
   - 检查路径配置是否存在中文或特殊字符
4. 日志查看
   - 程序运行日志保存在 ./log/app.log，遇到问题时可以查看日志文件获取详细错误信息。

## 安全提示
- 不要将包含敏感信息的配置文件提交到版本控制系统
- 定期更新 JIRA 密码和钉钉机器人密钥
- 确保日志文件不会泄露敏感信息

## 许可证
本项目采用 **GNU General Public License v3.0**。
Copyright (C) 2025
这是一个自由软件：您可以自由地重新分发和修改它，遵循 GNU 通用公共许可证的条款。
**重要提示**: 由于本项目使用 GPL 许可证，任何基于本项目的修改或衍生作品也必须以 GPLv3 发布。
完整许可证文本请参阅 [LICENSE](LICENSE) 文件。
