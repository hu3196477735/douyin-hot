from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # 启动浏览器
    browser = p.chromium.launch()
    
    # 创建手机尺寸视口
    context = browser.new_context(
        viewport={'width': 375, 'height': 812},  # iPhone X 尺寸
        device_scale_factor=2
    )
    
    page = context.new_page()
    
    # 打开本地网站
    page.goto('file:///c:/Users/Admin/WorkBuddy/Claw/index.html')
    
    # 等待页面加载
    page.wait_for_timeout(2000)
    
    # 截图
    page.screenshot(path='mobile_test.png', full_page=True)
    
    browser.close()
    
print("手机尺寸截图已保存: mobile_test.png")
