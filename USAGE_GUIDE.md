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
python demo_open_snapshot.py
```

## 预期输出

```
打开网页并获取 snapshot 示例
============================================================

1. 检查浏览器状态...
   状态: {'enabled': True, 'profile': 'chrome', 'running': True, 'cdpReady': True, ...}

2. 启动浏览器...
   ✓ 浏览器已启动

3. 打开网页...
   ✓ 已打开 https://example.com

4. 等待页面加载...

5. 获取页面 snapshot...
   ✓ 快照获取成功
   页面标题: Example Domain...
   可交互元素数量: 10

6. 保存 snapshot 到文件...
   ✓ snapshot 已保存到 snapshot.json

7. 截图...
   ✓ 截图成功: {"data": "data:image/png;base64,..."}

8. 停止浏览器...
   ✓ 浏览器已停止

============================================================
✓ 操作完成！
✓ 网页已打开，snapshot 已保存
============================================================
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
        await client.browser_start()
        await client.browser_open("https://google.com")
        await asyncio.sleep(5)  # 等待 5 秒
        await client.browser_stop()

asyncio.run(simple_open())
```

### 示例 2: 搜索操作

```python
import asyncio
from openclaw_browser_client import OpenClawBrowserClient

async def search_example():
    async with OpenClawBrowserClient() as client:
        await client.browser_start()
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
        
        await client.browser_stop()

asyncio.run(search_example())
```

## 查看结果

运行脚本后，你可以：

1. **查看 snapshot.json 文件** - 包含页面的详细信息
2. **查看截图** - 浏览器会保存截图数据
3. **检查浏览器** - 看看实际打开的页面

## 后续步骤

- 尝试其他浏览器操作（如 `browser_act` 执行点击、输入等）
- 探索 `BrowserAutomation` 类的高级功能
- 查看 `example_usage.py` 中的更多示例

---

如果遇到任何问题，请确保：
1. OpenClaw Gateway 正在运行
2. Chrome 浏览器已打开并连接了 OpenClaw 扩展
3. 网络连接正常

祝你使用愉快！ 🦞
