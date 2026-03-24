# -*- coding: utf-8 -*-
"""
全网热榜数据生成脚本
生成各平台的热榜数据并保存为JSON文件，供网页使用
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

# 输出目录
OUTPUT_DIR = r'C:\Users\Admin\WorkBuddy\Claw\.workbuddy\hot_data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_douyin_hot():
    """获取抖音热榜"""
    try:
        url = 'https://v2.xxapi.cn/api/douyinhot'
        response = requests.get(url, timeout=10)
        result = response.json()
        
        print(f"抖音API返回: {result}")
        
        if result.get('code') == 200:
            data = result.get('data', {})
            
            # 检查是否是列表格式
            if isinstance(data, list):
                return [
                    {
                        'word': item if isinstance(item, str) else str(item.get('word', '')),
                        'hotValue': 0,
                        'position': i + 1
                    }
                    for i, item in enumerate(data[:30])
                ]
            # 检查是否是对象格式
            elif isinstance(data, dict):
                list_data = data.get('list', [])
                if isinstance(list_data, list):
                    return [
                        {
                            'word': item.get('word', ''),
                            'hotValue': int(item.get('hot_value', 0)),
                            'position': i + 1
                        }
                        for i, item in enumerate(list_data[:30])
                    ]
    except Exception as e:
        print(f"抖音热榜获取失败: {e}")
    return []

def fetch_weibo_hot():
    """获取微博热榜"""
    try:
        url = 'https://v2.xxapi.cn/api/weibohot'
        response = requests.get(url, timeout=10)
        result = response.json()
        
        print(f"微博API返回: {result}")
        
        if result.get('code') == 200 and result.get('data'):
            data = result['data'][:30]
            return [
                {
                    'word': item.get('title', item.get('word', '')),
                    'hotValue': int(str(item.get('hot', '0')).replace('万', '').replace('万热度', '')) * 10000,
                    'position': item.get('index', i + 1)
                }
                for i, item in enumerate(data)
            ]
    except Exception as e:
        print(f"微博热榜获取失败: {e}")
    return []

def fetch_zhihu_hot():
    """获取知乎热榜"""
    try:
        url = 'https://v2.xxapi.cn/api/zhihuhot'
        response = requests.get(url, timeout=10)
        result = response.json()
        
        if result.get('code') == 200 and result.get('data'):
            data = result['data'][:30]
            return [
                {
                    'word': item.get('title', ''),
                    'hotValue': int(str(item.get('hot', '0')).replace('万热度', '').replace('万', '')) * 10000,
                    'position': i + 1
                }
                for i, item in enumerate(data)
            ]
    except Exception as e:
        print(f"知乎热榜获取失败: {e}")
    return []

def fetch_bilibili_hot():
    """获取B站热榜"""
    try:
        url = 'https://v2.xxapi.cn/api/bilibilihot'
        response = requests.get(url, timeout=10)
        result = response.json()
        
        if result.get('code') == 200 and result.get('data'):
            data = result['data'][:30]
            return [
                {
                    'word': word if isinstance(word, str) else str(word),
                    'hotValue': 0,
                    'position': i + 1
                }
                for i, word in enumerate(data)
            ]
    except Exception as e:
        print(f"B站热榜获取失败: {e}")
    return []

def fetch_baidu_hot():
    """获取百度热榜"""
    try:
        url = 'https://v2.xxapi.cn/api/baiduhot'
        response = requests.get(url, timeout=10)
        result = response.json()
        
        if result.get('code') == 200 and result.get('data'):
            data = result['data'][:30]
            return [
                {
                    'word': item.get('title', ''),
                    'hotValue': int(str(item.get('hot', '0')).replace('万', '')) * 10000,
                    'position': item.get('index', i + 1)
                }
                for i, item in enumerate(data)
            ]
    except Exception as e:
        print(f"百度热榜获取失败: {e}")
    return []

def main():
    """主函数"""
    print(f"开始获取全网热榜数据 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取各平台数据
    all_data = {
        'updateTime': datetime.now().isoformat(),
        'platforms': {}
    }
    
    # 抖音
    print("正在获取抖音热榜...")
    all_data['platforms']['抖音'] = fetch_douyin_hot()
    print(f"  成功获取 {len(all_data['platforms']['抖音'])} 条")
    
    # 微博
    print("正在获取微博热榜...")
    all_data['platforms']['微博'] = fetch_weibo_hot()
    print(f"  成功获取 {len(all_data['platforms']['微博'])} 条")
    
    # 知乎
    print("正在获取知乎热榜...")
    all_data['platforms']['知乎'] = fetch_zhihu_hot()
    print(f"  成功获取 {len(all_data['platforms']['知乎'])} 条")
    
    # B站
    print("正在获取B站热榜...")
    all_data['platforms']['B站'] = fetch_bilibili_hot()
    print(f"  成功获取 {len(all_data['platforms']['B站'])} 条")
    
    # 百度
    print("正在获取百度热榜...")
    all_data['platforms']['百度'] = fetch_baidu_hot()
    print(f"  成功获取 {len(all_data['platforms']['百度'])} 条")
    
    # 保存数据
    output_file = os.path.join(OUTPUT_DIR, 'hot_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print("=" * 60)
    print(f"数据已保存到: {output_file}")
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
