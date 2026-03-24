# -*- coding: utf-8 -*-
"""
生成抖音热点HTML并准备GitHub上传
"""
import json
import requests
from datetime import datetime
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
            return hot_list[:limit]
        else:
            print(f"❌ API返回错误: {data.get('msg')}")
            return None
    except Exception as e:
        print(f"❌ 获取抖音热点失败: {e}")
        return None

def generate_html(hot_list):
    """生成HTML文件"""
    if not hot_list:
        return None

    today_date = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 生成热点数据JS
    hot_data_json = json.dumps(hot_list, ensure_ascii=False, indent=2)

    # HTML模板
    html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>抖音热点榜 - {today_date}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 14px;
        }}
        .hot-list {{
            padding: 20px;
        }}
        .hot-item {{
            display: flex;
            align-items: center;
            padding: 15px;
            margin-bottom: 12px;
            background: #f8f9fa;
            border-radius: 12px;
            text-decoration: none;
            color: #333;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        .hot-item:hover {{
            background: #e9ecef;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .rank {{
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 18px;
            margin-right: 15px;
            flex-shrink: 0;
        }}
        .rank.top3 {{
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        }}
        .content {{
            flex: 1;
        }}
        .title {{
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 5px;
        }}
        .meta {{
            display: flex;
            align-items: center;
            gap: 15px;
            font-size: 13px;
            color: #666;
        }}
        .hot-value {{
            color: #ff6b6b;
            font-weight: 500;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            font-size: 13px;
        }}
        @media (max-width: 600px) {{
            .container {{
                border-radius: 0;
                margin: -20px;
            }}
            .header h1 {{
                font-size: 22px;
            }}
            .hot-item {{
                padding: 12px;
            }}
            .rank {{
                width: 35px;
                height: 35px;
                font-size: 16px;
            }}
            .title {{
                font-size: 14px;
            }}
            .meta {{
                font-size: 12px;
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 抖音热点榜</h1>
            <p>{today_date}</p>
        </div>
        <div class="hot-list" id="hotList"></div>
        <div class="footer">
            <p>点击热点即可跳转到抖音搜索页面</p>
            <p>数据来源：抖音热搜榜 | 更新频率：约2小时/次</p>
            <p>更新时间：{datetime.now().strftime('%H:%M:%S')}</p>
        </div>
    </div>

    <script>
        const hotData = {hot_data_json};

        function formatHotValue(value) {{
            if (value >= 10000000) {{
                return (value / 10000000).toFixed(1) + '千万';
            }} else if (value >= 10000) {{
                return (value / 10000).toFixed(1) + '万';
            }}
            return value.toString();
        }}

        function encodeText(text) {{
            return encodeURIComponent(text);
        }}

        function renderHotList() {{
            const container = document.getElementById('hotList');
            const list = hotData.map(item => {{
                const rankClass = item.rank <= 3 ? 'rank top3' : 'rank';
                const hotValueStr = formatHotValue(item.hotValue);
                const douyinUrl = `https://www.douyin.com/search/${{encodeText(item.word)}}`;

                return `
                    <a href="${{douyinUrl}}" class="hot-item">
                        <div class="${{rankClass}}">${{item.rank}}</div>
                        <div class="content">
                            <div class="title">${{item.word}}</div>
                            <div class="meta">
                                <span class="hot-value">🔥 ${{hotValueStr}}</span>
                                <span>排名 #${{item.rank}}</span>
                            </div>
                        </div>
                    </a>
                `;
            }}).join('');

            container.innerHTML = list;
        }}

        document.addEventListener('DOMContentLoaded', renderHotList);
    </script>
</body>
</html>'''

    return html_template, timestamp

def save_html(html_content, timestamp):
    """保存HTML文件"""
    filename = f'douyin_hot_{timestamp}.html'
    filepath = f'C:\\Users\\Admin\\WorkBuddy\\Claw\\{filename}'

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ HTML已生成: {filepath}")
    return filepath

def main():
    """主函数"""
    print("🔥 正在生成抖音热点HTML...")

    # 获取热点数据
    hot_list = get_douyin_hot(limit=15)

    if not hot_list:
        print("❌ 获取数据失败")
        return

    # 生成HTML
    html_content, timestamp = generate_html(hot_list)

    if html_content:
        # 保存文件
        save_html(html_content, timestamp)
        print("✅ 生成完成！")
        print("💡 提示：将此文件上传到 GitHub 仓库，即可生成可访问的网页链接")
    else:
        print("❌ HTML生成失败")

if __name__ == '__main__':
    main()
