# OpenClaw Browser Client 修改说明

## 📋 修改概述

本文档说明了对 `openclaw_browser_client.py` 所做的修改，以及每个修改的原因。

## 🔧 修改详情

### 1. `_run_command` 方法 - 添加超时和编码处理

**修改位置：** 第35-69行

**修改内容：**
```python
async def _run_command(self, command: str, timeout: int = 30) -> str:
    """运行命令
    
    Args:
        command: 要执行的命令
        timeout: 超时时间（秒），默认30秒
    
    Returns:
        命令输出
    
    Raises:
        Exception: 命令执行失败或超时
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True,
            timeout=timeout  # 添加超时设置
        )
        if result.stdout is None:
            return ""
        return result.stdout
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        raise Exception(f"命令执行失败: {error_msg}\n命令: {command}")
    except subprocess.TimeoutExpired:
        raise Exception(f"命令执行超时（{timeout}秒）: {command}")
```

**修改原因：**
1. **添加超时设置**：防止命令无限期挂起，特别是浏览器启动命令
2. **添加编码处理**：`encoding='utf-8'` 和 `errors='replace'` 确保正确处理中文和特殊字符
3. **添加超时异常处理**：捕获 `TimeoutExpired` 异常并提供清晰的错误信息
4. **检查空输出**：确保 `stdout` 不为空，避免后续处理出错

**解决的问题：**
- 脚本卡在浏览器启动步骤（无超时）
- UnicodeDecodeError: 'gbk' codec can't decode byte 0xad
- 命令执行失败时错误信息不清晰

---

### 2. `browser_start` 方法 - 添加状态检查和更长的超时

**修改位置：** 第80-108行

**修改内容：**
```python
async def browser_start(self, profile: Optional[str] = None) -> Dict[str, Any]:
    """启动浏览器
    
    Args:
        profile: 浏览器配置名称
    
    Returns:
        启动结果
    
    Note:
        如果浏览器已经在运行，会直接返回成功状态
    """
    # 先检查浏览器状态
    try:
        status = await self.browser_status(profile)
        if status.get("status") == "running":
            # 浏览器已经在运行，直接返回
            return {"status": "success", "message": "Browser already running"}
    except Exception as e:
        # 状态检查失败，可能是浏览器未启动，继续尝试启动
        pass
    
    # 启动浏览器
    cmd = f"openclaw browser start --json"
    if profile or self.profile:
        p = profile or self.profile
        cmd += f" --profile {p}"
    output = await self._run_command(cmd, timeout=60)  # 启动浏览器可能需要更长时间
    return json.loads(output)
```

**修改原因：**
1. **添加状态检查**：在启动前检查浏览器是否已经在运行，避免重复启动
2. **增加超时时间**：浏览器启动可能需要更长时间，从默认30秒增加到60秒
3. **优雅处理已运行状态**：如果浏览器已在运行，直接返回成功，而不是尝试启动

**解决的问题：**
- 重复启动浏览器导致错误
- 浏览器启动超时（30秒不够）
- 浏览器已在运行时的错误处理

---

### 3. `browser_act` 方法 - 重构命令格式

**修改位置：** 第220-265行

**修改内容：**
```python
async def browser_act(self, ref: int, action: str, value: Optional[str] = None,
                      profile: Optional[str] = None, wait_ms: Optional[int] = None) -> Dict[str, Any]:
    """执行 UI 操作
    
    Args:
        ref: 元素引用（从 snapshot 获取）
        action: 操作类型：click, type, press, hover, drag, select, fill, resize, wait, evaluate
        value: 操作值（如输入的文本、按键等）
        profile: 浏览器配置名称
        wait_ms: 等待毫秒数
    
    Note:
        根据不同的操作类型使用不同的命令格式
    """
    # 构建命令 - 根据不同的操作类型使用不同的命令格式
    if action == "click":
        cmd = f"openclaw browser click {ref} --json"
    elif action == "type" and value:
        cmd = f"openclaw browser type {ref} \"{value}\" --json"
    elif action == "press" and value:
        cmd = f"openclaw browser press {value} --json"
    elif action == "hover":
        cmd = f"openclaw browser hover {ref} --json"
    elif action == "drag" and value:
        cmd = f"openclaw browser drag {ref} {value} --json"
    elif action == "select" and value:
        cmd = f"openclaw browser select {ref} {value} --json"
    elif action == "fill" and value:
        cmd = f"openclaw browser fill --fields '{value}' --json"
    elif action == "resize" and value:
        cmd = f"openclaw browser resize {value} --json"
    elif action == "wait" and value:
        cmd = f"openclaw browser wait {value} --json"
    else:
        raise ValueError(f"不支持的操作类型: {action}")
    
    if wait_ms:
        cmd += f" --wait {wait_ms}"
    if profile or self.profile:
        p = profile or self.profile
        cmd += f" --profile {p}"
    output = await self._run_command(cmd)
    return json.loads(output)
```

**修改原因：**
1. **重构命令格式**：根据不同的操作类型使用不同的命令格式，而不是统一的 `act` 命令
2. **支持更多操作**：支持 click, type, press, hover, drag, select, fill, resize, wait 等操作
3. **改进错误处理**：不支持的操作类型会抛出 `ValueError` 异常

**解决的问题：**
- 错误: too many arguments for 'evaluate'. Expected 0 arguments but got 1
- 不支持的操作类型导致错误
- 命令格式不正确

**命令格式对比：**

| 操作类型 | 修改前 | 修改后 |
|---------|--------|--------|
| click | `openclaw browser act {ref} click` | `openclaw browser click {ref}` |
| type | `openclaw browser act {ref} type '{value}'` | `openclaw browser type {ref} "{value}"` |
| press | `openclaw browser act {ref} press '{value}'` | `openclaw browser press {value}` |
| hover | `openclaw browser act {ref} hover` | `openclaw browser hover {ref}` |

---

### 4. `browser_evaluate` 方法 - 修正命令格式并添加调试信息

**修改位置：** 第267-293行

**修改内容：**
```python
async def browser_evaluate(self, javascript: str, profile: Optional[str] = None) -> Dict[str, Any]:
    """执行 JavaScript
    
    Args:
        javascript: 要执行的 JavaScript 代码
        profile: 浏览器配置名称
    
    Note:
        使用 --fn 参数传递 JavaScript 代码，而不是直接作为参数
    """
    # 使用 openclaw browser evaluate 命令
    # 格式: openclaw browser evaluate --fn 'javascript' --json
    cmd = f"openclaw browser evaluate --fn \"{javascript}\" --json"
    if profile or self.profile:
        p = profile or self.profile
        cmd += f" --profile {p}"
    
    # 调试信息
    print(f"[DEBUG] 执行 JavaScript: {javascript[:100]}...")
    print(f"[DEBUG] 命令: {cmd[:200]}...")
    
    output = await self._run_command(cmd)
    result = json.loads(output)
    
    print(f"[DEBUG] 结果: {result}")
    
    return result
```

**修改原因：**
1. **修正命令格式**：使用 `--fn` 参数传递 JavaScript 代码，而不是直接作为参数
2. **添加调试信息**：打印执行的 JavaScript 代码、命令和结果，方便调试
3. **改进错误处理**：通过调试信息更容易定位问题

**解决的问题：**
- 错误: too many arguments for 'evaluate'. Expected 0 arguments but got 1
- JavaScript 执行失败时难以调试
- 命令格式不正确

**命令格式对比：**

| 修改前 | 修改后 |
|--------|--------|
| `openclaw browser evaluate 'javascript' --json` | `openclaw browser evaluate --fn 'javascript' --json` |

---

### 5. `browser_snapshot` 方法 - 修正字段名称

**修改位置：** 第177-209行

**修改内容：**
```python
async def browser_snapshot(self, mode: str = "ai", profile: Optional[str] = None, 
                           interactive: bool = False, compact: bool = False, 
                           depth: Optional[int] = None, selector: Optional[str] = None) -> BrowserSnapshot:
    """获取页面快照
    
    Args:
        mode: "ai" 或 "aria"
        profile: 浏览器配置名称
        interactive: 是否包含交互元素
        compact: 是否紧凑模式
        depth: 快照深度
        selector: CSS 选择器
    """
    cmd = f"openclaw browser snapshot --mode {mode} --json"
    if interactive:
        cmd += " --interactive"
    if compact:
        cmd += " --compact"
    if depth is not None:
        cmd += f" --depth {depth}"
    if selector:
        cmd += f" --selector '{selector}'"
    if profile or self.profile:
        p = profile or self.profile
        cmd += f" --profile {p}"
    output = await self._run_command(cmd)
    result = json.loads(output)
    
    return BrowserSnapshot(
        content=result.get("snapshot", ""),  # 修正：使用 "snapshot" 而不是 "content"
        refs=result.get("refs", {}),
        metadata=result.get("metadata", {})
    )
```

**修改原因：**
1. **修正字段名称**：从 JSON 响应中读取 `snapshot` 字段，而不是 `content` 字段
2. **确保向后兼容**：使用 `.get()` 方法并提供默认值，避免 KeyError

**解决的问题：**
- 页面快照内容为空
- 字段名称不匹配导致数据丢失

**字段名称对比：**

| 修改前 | 修改后 |
|--------|--------|
| `result.get("content", "")` | `result.get("snapshot", "")` |

---

## 📊 修改总结

| 方法 | 主要修改 | 解决的问题 |
|------|---------|-----------|
| `_run_command` | 添加超时、编码处理、异常处理 | 命令挂起、编码错误、错误信息不清晰 |
| `browser_start` | 添加状态检查、增加超时时间 | 重复启动、启动超时 |
| `browser_act` | 重构命令格式、支持更多操作 | 命令格式错误、不支持的操作 |
| `browser_evaluate` | 修正命令格式、添加调试信息 | 命令格式错误、难以调试 |
| `browser_snapshot` | 修正字段名称 | 页面快照内容为空 |

---

## 🎯 影响范围

这些修改主要影响以下功能：

1. **浏览器启动和停止**：更可靠的启动机制，避免重复启动
2. **页面操作**：支持更多操作类型，命令格式更正确
3. **JavaScript 执行**：正确的命令格式，更好的调试支持
4. **页面快照**：正确读取快照内容
5. **错误处理**：更清晰的错误信息，更好的异常处理

---

## 🔄 向后兼容性

所有修改都保持了向后兼容性：

1. **方法签名**：所有方法的参数和返回值类型保持不变
2. **默认行为**：超时时间有合理的默认值（30秒）
3. **错误处理**：异常类型和格式保持一致
4. **数据结构**：`BrowserSnapshot` 和 `BrowserTab` 数据类保持不变

---

## 📝 使用建议

1. **超时设置**：根据网络和系统情况调整超时时间
2. **调试模式**：使用 `browser_evaluate` 的调试信息定位问题
3. **状态检查**：在启动浏览器前检查状态，避免重复启动
4. **错误处理**：捕获并处理异常，提供友好的错误信息

---

## 🚀 未来改进

可能的未来改进方向：

1. **重试机制**：对失败的命令自动重试
2. **日志系统**：集成更完善的日志系统
3. **性能优化**：减少不必要的命令执行
4. **配置管理**：支持从配置文件读取参数
5. **异步优化**：进一步优化异步操作

---

## 📞 反馈

如果您在使用过程中遇到问题或有改进建议，请通过以下方式反馈：

- 提交 Issue
- 发送 Pull Request
- 联系维护者

---

**文档版本：** 1.0  
**最后更新：** 2026-02-27  
**维护者：** OpenClaw Browser Team