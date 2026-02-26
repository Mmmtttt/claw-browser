# OpenClaw Browser 工具使用指南

## 步骤 1: 确保 OpenClaw Gateway 正在运行

首先，确保 OpenClaw Gateway 已经启动：

```bash
# 启动 Gateway
openclaw gateway --port 18789 --verbose
```

## 步骤 2: 安装并连接 Chrome 扩展

1. **打开 Chrome 浏览器**
2. **安装 OpenClaw Chrome 扩展**（如果还没有安装）
3. **点击浏览器右上角的 OpenClaw 扩展图标**
4. **在弹出的界面中选择要连接的标签页**
5. **点击 "Connect" 按钮**

## 步骤 3: 运行示例脚本

现在运行我们的示例脚本：

```bash
# 快速开始示例
python examples/getting_started.py

# 综合示例
python examples/example_usage.py
```

## 预期输出

### 快速开始示例

```
OpenClaw Browser 入门示例
==================================================

1. 启动浏览器...
   ✓ 浏览器已启动

2. 打开网页...
   ✓ 已打开 https://example.com

3. 获取标签页列表...
   ✓ 标签页数量: 1
     1. Example Domain - https://example.com/

4. 导航到新 URL...
   ✓ 已导航到 https://www.python.org

5. 再次获取标签页列表...
   ✓ 标签页数量: 1
     1. Welcome to Python.org - https://www.python.org/

==================================================
✓ 示例运行完成！
==================================================
```

### 综合示例

```
OpenClaw Browser 工具 Python 客户端示例
============================================================

示例 1: 基本使用
============================================================

1. 检查浏览器状态...
   状态: {'enabled': True, 'profile': 'chrome', 'running': True, ...}

2. 启动浏览器...
   浏览器已启动

3. 打开网页...
   已打开 https://example.com

4. 获取标签页列表...
   标签页数量: 1
     1. Example Domain - https://example.com/
```

## 故障排除

### 常见问题

1. **Chrome 扩展未连接**
   - 确保 Chrome 浏览器已打开
   - 点击 OpenClaw 扩展图标
   - 选择一个标签页并连接

2. **Gateway 未运行**
   - 运行 `openclaw gateway --port 18789`
   - 检查端口 18789 是否被占用

3. **权限问题**
   - 确保 Chrome 扩展有正确的权限
   - 检查 OpenClaw 配置文件

## 其他示例

### 示例 1: 简单打开网页

```python
import asyncio
from openclaw_browser_client import OpenClawBrowserClient

async def simple_open():
    async with OpenClawBrowserClient() as client:
        # 启动浏览器
        await client.browser_start()
        
        # 打开网页
        await client.browser_open("https://example.com")
        
        # 等待页面加载
        await asyncio.sleep(2)
        
        # 获取标签页列表
        tabs = await client.browser_tabs()
        for tab in tabs:
            print(f"{tab.title} - {tab.url}")

asyncio.run(simple_open())
```

### 示例 2: 标签页管理

```python
import asyncio
from openclaw_browser_client import OpenClawBrowserClient

async def tab_management():
    async with OpenClawBrowserClient() as client:
        # 打开多个标签页
        await client.browser_open("https://example.com")
        await client.browser_open("https://www.python.org")
        await client.browser_open("https://github.com")
        
        # 列出所有标签页
        tabs = await client.browser_tabs()
        for i, tab in enumerate(tabs, 1):
            print(f"{i}. {tab.title} - {tab.url}")
        
        # 导航到新 URL
        if tabs:
            await client.browser_navigate("https://httpbin.org")
            await asyncio.sleep(2)
        
        # 关闭最后一个标签页
        tabs = await client.browser_tabs()
        if tabs and tabs[-1].id:
            await client.browser_close(tabs[-1].id)

asyncio.run(tab_management())
```

### 示例 3: 配置管理

```python
import asyncio
from openclaw_browser_client import OpenClawBrowserClient

async def profile_management():
    async with OpenClawBrowserClient() as client:
        # 列出所有配置
        profiles = await client.browser_profiles()
        print(f"配置列表: {profiles}")
        
        # 创建新配置
        try:
            result = await client.browser_create_profile("my-profile")
            print(f"创建结果: {result}")
        except Exception as e:
            print(f"创建配置失败（可能已存在）: {e}")

asyncio.run(profile_management())
```

## 查看结果

运行脚本后，你可以：

1. **检查浏览器** - 看看实际打开的页面
2. **查看标签页列表** - 了解当前打开的所有标签页
3. **检查配置列表** - 了解可用的浏览器配置

## 后续步骤

- 查看 `example_usage.py` 了解更多示例
- 查看 `getting_started.py` 了解快速开始
- 使用 `openclaw_browser_cli.py` 进行命令行操作
- 阅读 `README.md` 了解完整文档
- 阅读 `skill.md` 了解 JavaScript 执行功能

---

如果遇到任何问题，请确保：
1. OpenClaw Gateway 正在运行
2. Chrome 浏览器已打开并连接了 OpenClaw 扩展
3. 网络连接正常

祝你使用愉快！ 🦞
