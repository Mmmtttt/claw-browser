# OpenClaw Browser Python Client

通过 Python 脚本控制 OpenClaw Browser 工具的完整能力。

## 快速开始

```python
import asyncio
from openclaw_browser_client import OpenClawBrowserClient

async def main():
    async with OpenClawBrowserClient() as client:
        # 启动浏览器
        await client.browser_start()
        
        # 打开网页
        await client.browser_open("https://example.com")
        
        # 等待页面加载
        await asyncio.sleep(2)
        
        # 获取标签页列表
        tabs = await client.browser_tabs()
        for i, tab in enumerate(tabs, 1):
            print(f"{i}. {tab.title} - {tab.url}")

asyncio.run(main())
```

## 安装

```bash
pip install -r requirements.txt
```

## 核心功能

- 🌐 浏览器控制（启动、停止、状态查询）
- 📑 标签页管理（打开、关闭、导航）
- ⚙️ 配置管理（列出、创建配置）

## 重要提示

### ⚠️ JavaScript 语法限制

OpenClaw 的 `browser_evaluate` 命令对 JavaScript 语法有严格限制：

**❌ 不支持**：
- `const`、`let`、`var` 变量声明
- `return` 语句
- 分号 `;` 结尾的多语句
- ES6+ 语法

**✅ 支持**：
- 单个表达式
- 可选链操作符 `?.`
- DOM 查询和操作

**示例**：
```python
# ❌ 错误
await client.browser_evaluate("const title = document.title; return title;")

# ✅ 正确
await client.browser_evaluate("document.title")
```

更多 JavaScript 用法请参考 [skill.md](skill.md)。

## 文档

- [skill.md](skill.md) - 完整 SKILL 文档，包含详细的 API 参考和使用示例
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - 详细使用指南
- [examples/](examples/) - 示例代码
- [tests/](tests/) - 测试套件

## 文件结构

```
claw-browser-python-client/
├── skill.md                      # SKILL 文档
├── README.md                     # 本文件
├── USAGE_GUIDE.md               # 使用指南
├── openclaw_browser_client.py   # 核心客户端
├── openclaw_browser_cli.py       # 命令行工具
├── requirements.txt              # 依赖列表
├── examples/                    # 示例代码
│   ├── example_usage.py
│   └── getting_started.py
└── tests/                       # 测试代码
    └── test_complete.py
```

## 使用场景

### 标签页管理
```python
async with OpenClawBrowserClient() as client:
    # 打开多个标签页
    await client.browser_open("https://example.com")
    await client.browser_open("https://www.python.org")
    
    # 列出所有标签页
    tabs = await client.browser_tabs()
    for tab in tabs:
        print(f"{tab.title} - {tab.url}")
    
    # 导航到新 URL
    await client.browser_navigate("https://github.com")
    
    # 关闭标签页
    if tabs and tabs[-1].id:
        await client.browser_close(tabs[-1].id)
```

### 配置管理
```python
async with OpenClawBrowserClient() as client:
    # 列出所有配置
    profiles = await client.browser_profiles()
    print(f"配置列表: {profiles}")
    
    # 创建新配置
    result = await client.browser_create_profile("my-profile")
    print(f"创建结果: {result}")
```

## 注意事项

1. 确保 Chrome 扩展已安装并连接
2. 确保 OpenClaw Gateway 正在运行
3. 确保扩展已连接到标签页
4. 严格遵守 JavaScript 语法限制
5. 长时间操作可能需要调整超时时间

## 相关资源

- OpenClaw GitHub: https://github.com/openclaw/openclaw
- OpenClaw 文档: https://docs.openclaw.ai
- Chrome 扩展文档: https://docs.openclaw.ai/tools/chrome-extension

## 许可证

MIT License
