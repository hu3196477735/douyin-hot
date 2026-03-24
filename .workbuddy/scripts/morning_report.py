# -*- coding: utf-8 -*-
"""
每日新闻早报生成工具
自动获取当天新闻并生成格式化的早报
"""
import json
import requests
from datetime import datetime
import os
import sys

# 设置标准输出为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_today_news():
    """获取今日新闻早报数据"""
    today = datetime.now().strftime('%Y-%m-%d')
    api_url = f'https://60s-static.viki.moe/60s/{today}.json'

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"获取新闻失败: {e}")
        return None

def generate_morning_report(data):
    """生成格式化的早报内容"""
    if not data:
        return None

    today_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    news_list = data.get('news', [])
    daily_tip = data.get('tip', '')

    # 生成早报内容
    report = f"""
{'='*60}
📰 每日新闻早报
{'='*60}
📅 日期: {today_date}
⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*60}
🌍 全球要闻（{len(news_list)}条）
{'='*60}
"""

    # 添加新闻条目（编号）
    for i, news in enumerate(news_list, 1):
        report += f"\n{i}. {news}"

    # 添加每日金句
    if daily_tip:
        report += f"""
{'='*60}
💡 每日金句
{'='*60}

{daily_tip}
"""

    report += f"\n{'='*60}\n"
    report += f"📮 数据来源: 60秒读懂世界\n"
    report += f"🌐 官方链接: https://60s-static.viki.moe/\n"
    report += f"{'='*60}\n"

    return report

def save_report(report, save_dir=None):
    """保存早报到文件"""
    if save_dir is None:
        save_dir = os.path.join(os.path.dirname(__file__), '..', 'memory', 'daily_reports')

    # 创建目录
    os.makedirs(save_dir, exist_ok=True)

    # 生成文件名
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f'morning_report_{today}.txt'
    filepath = os.path.join(save_dir, filename)

    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ 早报已保存至: {filepath}")
    return filepath

def main():
    """主函数"""
    print("📰 正在生成今日新闻早报...")

    # 获取新闻数据
    data = get_today_news()

    if not data:
        print("❌ 获取新闻数据失败，请稍后重试")
        return

    # 生成早报
    report = generate_morning_report(data)

    if report:
        # 输出到控制台
        print(report)

        # 保存到文件
        save_report(report)
        print("✅ 早报生成完成！")
    else:
        print("❌ 早报生成失败")

if __name__ == '__main__':
    main()
