# -*- coding: utf-8 -*-
"""
抖音热点整合工具
自动获取抖音热搜榜并生成格式化的热点摘要
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

def get_douyin_hot(limit=15):
    """获取抖音热搜榜数据"""
    api_url = 'https://v2.xxapi.cn/api/douyinhot'

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('code') == 200:
            hot_list = data.get('data', [])
            return hot_list[:limit]  # 返回前N条
        else:
            print(f"❌ API返回错误: {data.get('msg')}")
            return None
    except Exception as e:
        print(f"❌ 获取抖音热点失败: {e}")
        return None

def generate_hot_report(hot_list):
    """生成格式化的热点报告"""
    if not hot_list:
        return None

    today_date = datetime.now().strftime('%Y-%m-%d')

    # 生成热点报告
    report = f"""
{'='*60}
🔥 抖音热点榜
{'='*60}
📅 日期: {today_date}
⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*60}
🎬 今日热搜 TOP {len(hot_list)}
{'='*60}
"""

    # 添加热点条目
    for i, item in enumerate(hot_list, 1):
        word = item.get('word', '')
        hot_value = item.get('hot_value', 0)
        position = item.get('position', i)

        # 格式化热度值
        if hot_value >= 10000000:
            hot_str = f"{hot_value/10000000:.1f}千万"
        elif hot_value >= 10000:
            hot_str = f"{hot_value/10000:.1f}万"
        else:
            hot_str = str(hot_value)

        report += f"\n{i}. {word}\n"
        report += f"   🔥 热度: {hot_str} | 排名: #{position}\n"

    report += f"""
{'='*60}
📱 如何查看视频？
{'='*60}

方式1：打开抖音APP，直接搜索以上关键词
方式2：复制关键词粘贴到抖音搜索框

📮 数据来源: 抖音热搜榜
🌐 更新频率: 约2小时/次
{'='*60}
"""

    return report

def save_report(report, save_dir=None):
    """保存热点报到文件"""
    if save_dir is None:
        save_dir = os.path.join(os.path.dirname(__file__), '..', 'memory', 'daily_reports')

    # 创建目录
    os.makedirs(save_dir, exist_ok=True)

    # 生成文件名
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f'douyin_hot_{today}.txt'
    filepath = os.path.join(save_dir, filename)

    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ 抖音热点已保存至: {filepath}")
    return filepath

def main():
    """主函数"""
    print("🔥 正在获取抖音热搜榜...")

    # 获取热点数据
    hot_list = get_douyin_hot(limit=15)

    if not hot_list:
        print("❌ 获取抖音热点数据失败，请稍后重试")
        return

    # 生成热点报告
    report = generate_hot_report(hot_list)

    if report:
        # 输出到控制台
        print(report)

        # 保存到文件
        save_report(report)
        print("✅ 抖音热点生成完成！")
    else:
        print("❌ 抖音热点生成失败")

if __name__ == '__main__':
    main()
