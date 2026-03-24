# 每日新闻早报工具

## 功能说明

自动获取当天全球要闻，生成格式化的新闻早报。

## 使用方式

### 手动生成

运行以下命令：

```bash
python C:\Users\Admin\WorkBuddy\Claw\.workbuddy\scripts\morning_report.py
```

### 自动生成

每天早上 **7:30** 自动生成当日早报。

早报文件保存位置：
- `C:\Users\Admin\WorkBuddy\Claw\.workbuddy\memory\daily_reports\morning_report_YYYY-MM-DD.txt`

## 早报格式

- 📅 日期和生成时间
- 🌍 全球要闻（约15条）
- 💡 每日金句
- 📮 数据来源

## 数据来源

- 60秒读懂世界 (https://60s-static.viki.moe/)
- 数据每日 00:00-10:00（UTC+8）自动更新

## 自动化任务

任务名称：每日新闻早报
运行时间：每天早上 7:30
工作目录：c:\Users\Admin\WorkBuddy\Claw

如需修改运行时间，请在 WorkBuddy 自动化设置中调整。
