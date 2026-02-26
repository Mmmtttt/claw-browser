# OpenClaw Browser 工具 Python 客户端

这是一个完整的 Python 客户端实现，用于手动调用 OpenClaw 的 browser 工具。

## 文件说明

- `openclaw_browser_client.py` - 核心客户端类和高级自动化封装
- `example_usage.py` - 7 个详细的使用示例
- `getting_started.py` - 入门示例
- `openclaw_browser_cli.py` - 命令行工具
- `requirements.txt` - Python 依赖
- `README.md` - 项目文档
- `USAGE_GUIDE.md` - 详细使用指南
- `.gitignore` - Git 忽略文件

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 确保 OpenClaw Gateway 正在运行

```bash
# 启动 Gateway
openclaw gateway --port 18789 --verbose
```

### 2. 安装并连接 Chrome 扩展

1. 打开 Chrome 浏览器
2. 安装 OpenClaw Chrome 扩展
3. 点击浏览器右上角的 OpenClaw 扩展图标
4. 选择一个标签页并连接

### 3. 运行示例

```python
# 入门示例
python getting_started.py

# 详细示例
python example_usage.py
```

## 代码示例

### 示例 1: 基本使用

```python
import asyncio
from openclaw_browser_client import OpenClawBrowserClient

async def basic_usage():
    """基本使用示例"""
    async with OpenClawBrowserClient() as client:
        # 检查浏览器状态
        status = await client.browser_status()
        print(f"浏览器状态: {status}")
        
        # 打开网页
        await client.browser_open("https://example.com")
        print("已打开 https://example.com")
        
        # 获取快照
        snapshot = await client.browser_snapshot(mode="ai")
        print(f"页面内容: {snapshot.content[:200]}...")

asyncio.run(basic_usage())
```

### 示例 2: 搜索操作

```python
import asyncio
from openclaw_browser_client import OpenClawBrowserClient

async def search_example():
    """搜索操作示例"""
    async with OpenClawBrowserClient() as client:
        # 打开 Google
        await client.browser_open("https://google.com")
        await asyncio.sleep(2)
        
        # 获取快照
        snapshot = await client.browser_snapshot(mode="ai")
        
        # 查找搜索框
        search_ref = None
        for ref, element in snapshot.refs.items():
            if "search" in str(element).lower():
                search_ref = ref
                break
        
        if search_ref:
            # 输入搜索内容
            await client.browser_act(search_ref, "click")
            await asyncio.sleep(0.5)
            await client.browser_act(search_ref, "type", value="OpenClaw AI")
            await asyncio.sleep(1)
            await client.browser_act(search_ref, "press", value="Enter")
            await asyncio.sleep(3)
        
        print("搜索完成")

asyncio.run(search_example())
```

### 示例 3: 标签页管理

```python
import asyncio
from openclaw_browser_client import OpenClawBrowserClient

async def tab_management():
    """标签页管理示例"""
    async with OpenClawBrowserClient() as client:
        # 列出所有标签页
        tabs = await client.browser_tabs()
        print(f"当前标签页数量: {len(tabs)}")
        
        # 打开新网页
        await client.browser_open("https://example.com")
        await asyncio.sleep(1)
        
        # 再次列出标签页
        tabs_after = await client.browser_tabs()
        print(f"打开后标签页数量: {len(tabs_after)}")
        
        # 关闭最后一个标签页
        if tabs_after:
            last_tab = tabs_after[-1]
            await client.browser_close(last_tab.id)
            print(f"已关闭标签页: {last_tab.title}")

asyncio.run(tab_management())
```

### 示例 4: 执行 JavaScript

```python
import asyncio
from openclaw_browser_client import OpenClawBrowserClient

async def execute_javascript():
    """执行 JavaScript 示例"""
    async with OpenClawBrowserClient() as client:
        # 打开网页
        await client.browser_open("https://example.com")
        await asyncio.sleep(2)
        
        # 执行 JavaScript
        title = await client.browser_evaluate("document.title")
        print(f"页面标题: {title}")
        
        # 执行复杂的 JavaScript
        result = await client.browser_evaluate("\n""
            const links = document.querySelectorAll('a');
            return Array.from(links).map(link => ({
                text: link.textContent,
                href: link.href
            }));
        """)
        print(f"找到 {len(result)} 个链接")
        for link in result[:3]:
            print(f"- {link['text']}: {link['href']}")

asyncio.run(execute_javascript())
```

### 示例 5: 保存快照和截图

```python
import asyncio
import json
import base64
from openclaw_browser_client import OpenClawBrowserClient

async def save_snapshot_and_screenshot():
    """保存快照和截图示例"""
    async with OpenClawBrowserClient() as client:
        # 打开网页
        await client.browser_open("https://example.com")
        await asyncio.sleep(2)
        
        # 获取快照并保存
        snapshot = await client.browser_snapshot(mode="ai")
        with open("snapshot.json", "w", encoding="utf-8") as f:
            json.dump({
                "content": snapshot.content,
                "refs": snapshot.refs
            }, f, ensure_ascii=False, indent=2)
        print("✓ 快照已保存到 snapshot.json")
        
        # 截图并保存
        screenshot = await client.browser_screenshot()
        if "data" in screenshot:
            image_data = screenshot["data"].split(",")[1]
            image_bytes = base64.b64decode(image_data)
            with open("screenshot.png", "wb") as f:
                f.write(image_bytes)
            print("✓ 截图已保存到 screenshot.png")

asyncio.run(save_snapshot_and_screenshot())
```

## 主要功能

### OpenClawBrowserClient 类

提供所有 browser 工具的底层 API：

- `browser_status()` - 获取浏览器状态
- `browser_start()` - 启动浏览器
- `browser_stop()` - 停止浏览器
- `browser_tabs()` - 获取所有标签页
- `browser_open(url)` - 打开 URL
- `browser_focus(tab_id)` - 聚焦标签页
- `browser_close(tab_id)` - 关闭标签页
- `browser_navigate(url)` - 导航到 URL
- `browser_snapshot(mode="ai")` - 获取页面快照
- `browser_screenshot()` - 截图
- `browser_act(ref, action, value)` - 执行 UI 操作
- `browser_evaluate(javascript)` - 执行 JavaScript
- `browser_console()` - 获取控制台日志
- `browser_pdf()` - 导出 PDF
- `browser_upload(file_path)` - 上传文件
- `browser_dialog(action)` - 处理对话框
- `browser_profiles()` - 列出所有配置
- `browser_create_profile(name)` - 创建配置
- `browser_delete_profile(name)` - 删除配置
- `browser_reset_profile(name)` - 重置配置

### BrowserAutomation 类

提供高级自动化功能：

- `open_and_snapshot(url)` - 打开网页并获取快照
- `find_and_click(search_text)` - 查找元素并点击
- `type_text(ref, text)` - 在元素中输入文本
- `wait_for_element(search_text)` - 等待元素出现
- `take_screenshot_and_save(filename)` - 截图并保存到文件

## 命令行工具

```bash
# 检查浏览器状态
python openclaw_browser_cli.py status

# 打开网页
python openclaw_browser_cli.py open https://example.com

# 获取快照
python openclaw_browser_cli.py snapshot --mode ai

# 执行 JavaScript
python openclaw_browser_cli.py evaluate "document.title"

# 查看帮助
python openclaw_browser_cli.py --help
```

## UI 操作类型

`browser_act()` 支持的操作类型：

- `click` - 点击元素
- `type` - 输入文本
- `press` - 按键（如 Enter, Escape）
- `hover` - 悬停
- `drag` - 拖拽
- `select` - 选择
- `fill` - 填充表单
- `resize` - 调整大小
- `wait` - 等待
- `evaluate` - 执行 JavaScript

## 快照模式

- `ai` - AI 模式（默认，需要 Playwright）
- `aria` - 可访问性树模式

## 错误处理

```python
try:
    async with OpenClawBrowserClient() as client:
        await client.browser_start()
        await client.browser_open("https://example.com")
except Exception as e:
    print(f"错误: {e}")
```

## 注意事项

1. 确保 OpenClaw Gateway 正在运行（默认端口: 18789）
2. 确保 Chrome 浏览器已打开并连接了 OpenClaw 扩展
3. 网络连接正常
4. Browser 工具需要在 `~/.openclaw/openclaw.json` 中启用：
   ```json
   {
     "browser": {
       "enabled": true
     }
   }
   ```

## 故障排除

- **Chrome 扩展未连接**：点击 OpenClaw 扩展图标并选择一个标签页连接
- **Gateway 未运行**：运行 `openclaw gateway --port 18789`
- **权限问题**：确保 Chrome 扩展有正确的权限

## 许可证

MIT License
