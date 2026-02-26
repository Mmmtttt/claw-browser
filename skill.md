# OpenClaw Browser Python Client Skill

## 概述

本 Skill 提供了通过 Python 脚本控制 OpenClaw Browser 工具的完整能力。AI Agent 可以使用此 Skill 将浏览器自动化操作固化为可执行的 Python 脚本，实现基本的浏览器控制、标签页管理和配置管理。

## 核心能力

### 1. 浏览器控制
- 启动/停止浏览器
- 获取浏览器状态
- 浏览器配置管理

### 2. 标签页管理
- 打开/关闭标签页
- 页面导航
- 获取标签页列表

### 3. JavaScript 执行（重点）

**⚠️ 重要提示：JavaScript 语法限制**

OpenClaw 的 `browser evaluate` 命令对 JavaScript 语法有严格限制，**不支持以下语法**：
- ❌ `const`、`let`、`var` 变量声明
- ❌ `return` 语句
- ❌ 分号 `;` 结尾的多语句
- ❌ 复杂的函数定义
- ❌ ES6+ 语法（箭头函数、解构等）

**✅ 支持的语法**：
- ✅ 单个表达式
- ✅ 可选链操作符 `?.`
- ✅ DOM 查询和操作
- ✅ 属性访问和方法调用

#### JavaScript 使用示例

**获取页面标题**：
```python
result = await client.browser_evaluate("document.title")
title = result.get("result", "")
```

**获取元素数量**：
```python
result = await client.browser_evaluate("document.querySelectorAll('a').length")
count = result.get("result", 0)
```

**获取元素内容**：
```python
result = await client.browser_evaluate("document.querySelector('h1').textContent")
text = result.get("result", "")
```

**使用可选链操作符（推荐）**：
```python
result = await client.browser_evaluate("document.querySelector('h1')?.textContent")
text = result.get("result", "")
```

**获取 URL**：
```python
result = await client.browser_evaluate("window.location.href")
url = result.get("result", "")
```

**获取页面文本**：
```python
result = await client.browser_evaluate("document.body.innerText")
text = result.get("result", "")
```

**查询并修剪文本**：
```python
result = await client.browser_evaluate("document.querySelector('h1')?.textContent.trim()")
text = result.get("result", "")
```

**获取元素属性**：
```python
result = await client.browser_evaluate("document.querySelector('h1')?.tagName")
tag_name = result.get("result", "")
```

**获取页面元数据**：
```python
result = await client.browser_evaluate("document.querySelector('meta[name=\"description\"]')?.content")
description = result.get("result", "")
```

**检查元素是否存在**：
```python
result = await client.browser_evaluate("document.querySelector('h1') !== null")
exists = result.get("result", False)
```

**修改页面样式**：
```python
await client.browser_evaluate("document.body.style.backgroundColor = '#f0f0f0'")
```

**获取段落数量**：
```python
result = await client.browser_evaluate("document.querySelectorAll('p').length")
p_count = result.get("result", 0)
```

**获取页面语言**：
```python
result = await client.browser_evaluate("document.documentElement.lang")
lang = result.get("result", "")
```

**获取页面字符集**：
```python
result = await client.browser_evaluate("document.characterSet")
charset = result.get("result", "")
```

#### 常见错误示例

**❌ 错误：使用变量声明**
```python
# 错误：会报 "Unexpected token 'const'"
result = await client.browser_evaluate("const links = document.querySelectorAll('a'); return links.length;")
```

**✅ 正确：直接使用表达式**
```python
result = await client.browser_evaluate("document.querySelectorAll('a').length")
```

**❌ 错误：使用 return 语句**
```python
# 错误：会报 "Unexpected token 'return'"
result = await client.browser_evaluate("return document.title;")
```

**✅ 正确：直接返回表达式**
```python
result = await client.browser_evaluate("document.title")
```

**❌ 错误：使用分号连接多个语句**
```python
# 错误：会报 "Unexpected token ';'"
result = await client.browser_evaluate("document.body.style.backgroundColor = '#f0f0f0'; 'done'")
```

**✅ 正确：只执行一个操作**
```python
result = await client.browser_evaluate("document.body.style.backgroundColor = '#f0f0f0'")
```

## 使用场景

### 1. 浏览器控制
```python
async with OpenClawBrowserClient() as client:
    # 检查浏览器状态
    status = await client.browser_status()
    print(f"状态: {status}")
    
    # 启动浏览器
    await client.browser_start()
    print("浏览器已启动")
```

### 2. 标签页管理
```python
async with OpenClawBrowserClient() as client:
    # 打开网页
    await client.browser_open("https://example.com")
    
    # 获取标签页列表
    tabs = await client.browser_tabs()
    for tab in tabs:
        print(f"{tab.title} - {tab.url}")
    
    # 导航到新 URL
    await client.browser_navigate("https://www.python.org")
    
    # 关闭标签页
    if tabs and tabs[-1].id:
        await client.browser_close(tabs[-1].id)
```

### 3. 配置管理
```python
async with OpenClawBrowserClient() as client:
    # 列出所有配置
    profiles = await client.browser_profiles()
    print(f"配置列表: {profiles}")
    
    # 创建新配置
    result = await client.browser_create_profile("my-profile")
    print(f"创建结果: {result}")
```

### 4. JavaScript 数据提取
```python
async with OpenClawBrowserClient() as client:
    # 打开网页
    await client.browser_open("https://example.com")
    await asyncio.sleep(2)
    
    # 获取页面标题
    result = await client.browser_evaluate("document.title")
    title = result.get("result", "")
    print(f"标题: {title}")
    
    # 获取所有链接
    result = await client.browser_evaluate("document.querySelectorAll('a').length")
    links_count = result.get("result", 0)
    print(f"链接数量: {links_count}")
```

## 文件结构

```
claw-browser-python-client/
├── skill.md                 # 本文档
├── README.md                # 项目说明
├── USAGE_GUIDE.md          # 详细使用指南
├── openclaw_browser_client.py    # 核心客户端类
├── openclaw_browser_cli.py        # 命令行工具
├── requirements.txt         # 依赖列表
├── examples/               # 示例代码
│   ├── example_usage.py    # 综合示例
│   └── getting_started.py  # 快速开始
└── tests/                  # 测试代码
    └── test_complete.py   # 完整测试套件
```

## 安装依赖

```bash
pip install -r requirements.txt
```

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

## API 参考

### OpenClawBrowserClient

主要方法：
- `browser_status()` - 获取浏览器状态
- `browser_start()` - 启动浏览器
- `browser_stop()` - 停止浏览器
- `browser_open(url)` - 打开新标签页
- `browser_close(tab_id)` - 关闭标签页
- `browser_navigate(url)` - 导航到 URL
- `browser_tabs()` - 获取标签页列表
- `browser_evaluate(javascript)` - 执行 JavaScript ⚠️
- `browser_profiles()` - 获取配置列表
- `browser_create_profile(name)` - 创建配置
- `browser_delete_profile(name)` - 删除配置

## 最佳实践

1. **JavaScript 使用**：始终使用简单的表达式，避免变量声明和 return 语句
2. **错误处理**：使用 try-except 捕获异常
3. **等待时间**：在页面操作后添加适当的等待时间
4. **资源清理**：使用 async with 语句确保资源正确释放

## 注意事项

1. **浏览器扩展**：确保 Chrome 扩展已安装并连接
2. **Gateway 运行**：确保 OpenClaw Gateway 正在运行
3. **标签页连接**：确保扩展已连接到标签页
4. **JavaScript 限制**：严格遵守 JavaScript 语法限制
5. **超时设置**：长时间操作可能需要调整超时时间

## 相关资源

- OpenClaw GitHub: https://github.com/openclaw/openclaw
- OpenClaw 文档: https://docs.openclaw.ai
- Chrome 扩展文档: https://docs.openclaw.ai/tools/chrome-extension

## 版本历史

- v1.0.0 - 初始版本，支持基本的浏览器控制功能
- v1.1.0 - 添加 JavaScript 执行功能
- v1.2.0 - 完善测试套件，通过率 100%
- v1.3.0 - 优化代码结构，删除不必要的封装类

## 许可证

MIT License
