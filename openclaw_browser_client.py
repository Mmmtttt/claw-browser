import asyncio
import json
import base64
import subprocess
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class BrowserSnapshot:
    """浏览器快照数据"""
    content: str
    refs: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class BrowserTab:
    """浏览器标签页信息"""
    id: str
    url: str
    title: str


class OpenClawBrowserClient:
    """OpenClaw Browser 工具的 Python 客户端"""

    def __init__(self, profile: Optional[str] = None):
        self.profile = profile

    async def connect(self):
        """连接 - 占位符方法"""
        return self

    async def _run_command(self, command: str, timeout: int = 30) -> str:
        """运行命令"""
        try:
            # 使用 shell=True 来确保在正确的环境中运行
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
            # 确保 stdout 不为空
            if result.stdout is None:
                return ""
            return result.stdout
        except subprocess.CalledProcessError as e:
            # 尝试从 stderr 获取错误信息
            error_msg = e.stderr if e.stderr else str(e)
            raise Exception(f"命令执行失败: {error_msg}\n命令: {command}")
        except subprocess.TimeoutExpired:
            raise Exception(f"命令执行超时（{timeout}秒）: {command}")

    async def browser_status(self, profile: Optional[str] = None) -> Dict[str, Any]:
        """获取浏览器状态"""
        cmd = f"openclaw browser status --json"
        if profile or self.profile:
            p = profile or self.profile
            cmd += f" --profile {p}"
        output = await self._run_command(cmd)
        return json.loads(output)

    async def browser_start(self, profile: Optional[str] = None) -> Dict[str, Any]:
        """启动浏览器"""
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

    async def browser_stop(self, profile: Optional[str] = None) -> Dict[str, Any]:
        """停止浏览器"""
        cmd = f"openclaw browser stop --json"
        if profile or self.profile:
            p = profile or self.profile
            cmd += f" --profile {p}"
        output = await self._run_command(cmd)
        return json.loads(output)

    async def browser_tabs(self, profile: Optional[str] = None) -> List[BrowserTab]:
        """获取所有标签页"""
        cmd = f"openclaw browser tabs --json"
        if profile or self.profile:
            p = profile or self.profile
            cmd += f" --profile {p}"
        output = await self._run_command(cmd)
        result = json.loads(output)
        
        tabs = []
        if "tabs" in result:
            for tab in result["tabs"]:
                # 尝试多种可能的 ID 字段名称
                tab_id = tab.get("id") or tab.get("targetId") or tab.get("tabId") or str(tab.get("index", ""))
                tabs.append(BrowserTab(
                    id=tab_id,
                    url=tab.get("url", ""),
                    title=tab.get("title", "")
                ))
        return tabs

    async def browser_open(self, url: str, profile: Optional[str] = None) -> Dict[str, Any]:
        """打开 URL"""
        cmd = f"openclaw browser open {url} --json"
        if profile or self.profile:
            p = profile or self.profile
            cmd += f" --profile {p}"
        output = await self._run_command(cmd)
        return json.loads(output)

    async def browser_focus(self, tab_id: str, profile: Optional[str] = None) -> Dict[str, Any]:
        """聚焦到指定标签页"""
        cmd = f"openclaw browser focus {tab_id} --json"
        if profile or self.profile:
            p = profile or self.profile
            cmd += f" --profile {p}"
        output = await self._run_command(cmd)
        return json.loads(output)

    async def browser_close(self, tab_id: Optional[str] = None, profile: Optional[str] = None) -> Dict[str, Any]:
        """关闭标签页"""
        if tab_id:
            cmd = f"openclaw browser close {tab_id} --json"
        else:
            cmd = "openclaw browser close --json"
        if profile or self.profile:
            p = profile or self.profile
            cmd += f" --profile {p}"
        output = await self._run_command(cmd)
        return json.loads(output)

    async def browser_navigate(self, url: str, profile: Optional[str] = None) -> Dict[str, Any]:
        """导航到指定 URL"""
        cmd = f"openclaw browser navigate {url} --json"
        if profile or self.profile:
            p = profile or self.profile
            cmd += f" --profile {p}"
        
        print(f"[DEBUG] browser_navigate: {cmd}")
        output = await self._run_command(cmd)
        result = json.loads(output)
        print(f"[DEBUG] browser_navigate result: {result}")
        return result

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
        # 始终使用 chrome profile
        if not profile and not self.profile:
            cmd += " --profile chrome"
        elif profile or self.profile:
            p = profile or self.profile
            cmd += f" --profile {p}"
        
        print(f"[DEBUG] browser_snapshot: {cmd}")
        output = await self._run_command(cmd)
        result = json.loads(output)
        print(f"[DEBUG] browser_snapshot result keys: {list(result.keys())}")
        
        return BrowserSnapshot(
            content=result.get("snapshot", ""),
            refs=result.get("refs", {}),
            metadata=result.get("metadata", {})
        )

    async def browser_screenshot(self, profile: Optional[str] = None) -> Dict[str, Any]:
        """获取截图"""
        cmd = "openclaw browser screenshot --json"
        # 始终使用 chrome profile
        if not profile and not self.profile:
            cmd += " --profile chrome"
        elif profile or self.profile:
            p = profile or self.profile
            cmd += f" --profile {p}"
        
        print(f"[DEBUG] browser_screenshot: {cmd}")
        output = await self._run_command(cmd)
        result = json.loads(output)
        print(f"[DEBUG] browser_screenshot result keys: {list(result.keys())}")
        return result

    async def browser_act(self, ref: int, action: str, value: Optional[str] = None,
                          profile: Optional[str] = None, wait_ms: Optional[int] = None) -> Dict[str, Any]:
        """执行 UI 操作
        
        Args:
            ref: 元素引用（从 snapshot 获取）
            action: 操作类型：click, type, press, hover, drag, select, fill, resize, wait, evaluate
            value: 操作值（如输入的文本、按键等）
            profile: 浏览器配置名称
            wait_ms: 等待毫秒数
        """
        # 构建命令
        if action == "click":
            cmd = f"openclaw browser click {ref} --json"
        elif action == "type" and value:
            cmd = f"openclaw browser type {ref} \"{value}\" --json"
        elif action == "press" and value:
            cmd = f"openclaw browser press {value} --json"
        elif action == "hover":
            cmd = f"openclaw browser hover {ref} --json"
        elif action == "drag" and value:
            # drag 需要两个 ref，格式: drag <from_ref> <to_ref>
            cmd = f"openclaw browser drag {ref} {value} --json"
        elif action == "select" and value:
            # select 需要 ref 和选项
            cmd = f"openclaw browser select {ref} {value} --json"
        elif action == "fill" and value:
            cmd = f"openclaw browser fill --fields '{value}' --json"
        elif action == "resize" and value:
            # resize 需要宽度和高度
            cmd = f"openclaw browser resize {value} --json"
        elif action == "wait" and value:
            # wait 需要时间（毫秒）
            cmd = f"openclaw browser wait --time {value} --json"
        else:
            raise ValueError(f"不支持的操作类型: {action}")
        
        # 始终使用 chrome profile
        if not profile and not self.profile:
            cmd += " --profile chrome"
        elif profile or self.profile:
            p = profile or self.profile
            cmd += f" --profile {p}"
        
        if wait_ms:
            cmd += f" --wait {wait_ms}"
        
        print(f"[DEBUG] browser_act: {cmd}")
        output = await self._run_command(cmd)
        result = json.loads(output)
        print(f"[DEBUG] browser_act result keys: {list(result.keys())}")
        return result

    async def browser_evaluate(self, javascript: str, profile: Optional[str] = None) -> Dict[str, Any]:
        """执行 JavaScript"""
        # 使用 openclaw browser evaluate 命令
        # 格式: openclaw browser evaluate --fn 'javascript' --json
        cmd = f"openclaw browser evaluate --fn \"{javascript}\" --json"
        # 始终使用 chrome profile
        if not profile and not self.profile:
            cmd += " --profile chrome"
        elif profile or self.profile:
            p = profile or self.profile
            cmd += f" --profile {p}"
        
        print(f"[DEBUG] browser_evaluate: {cmd[:100]}...")
        output = await self._run_command(cmd)
        result = json.loads(output)
        print(f"[DEBUG] browser_evaluate result keys: {list(result.keys())}")
        
        return result

    async def browser_console(self, profile: Optional[str] = None) -> Dict[str, Any]:
        """获取控制台日志"""
        cmd = "openclaw browser console --json"
        if profile or self.profile:
            p = profile or self.profile
            cmd += f" --profile {p}"
        output = await self._run_command(cmd)
        return json.loads(output)

    async def browser_pdf(self, profile: Optional[str] = None) -> Dict[str, Any]:
        """导出为 PDF"""
        cmd = "openclaw browser pdf --json"
        if profile or self.profile:
            p = profile or self.profile
            cmd += f" --profile {p}"
        output = await self._run_command(cmd)
        return json.loads(output)

    async def browser_upload(self, file_path: str, ref: Optional[int] = None, 
                             input_ref: Optional[str] = None, element: Optional[str] = None,
                             profile: Optional[str] = None) -> Dict[str, Any]:
        """上传文件
        
        Args:
            file_path: 文件路径
            ref: 元素引用（可选，用于自动点击）
            input_ref: aria 引用（可选）
            element: CSS 选择器（可选）
            profile: 浏览器配置名称
        """
        cmd = f"openclaw browser upload '{file_path}' --json"
        if ref:
            cmd += f" --ref {ref}"
        if input_ref:
            cmd += f" --input-ref {input_ref}"
        if element:
            cmd += f" --element '{element}'"
        if profile or self.profile:
            p = profile or self.profile
            cmd += f" --profile {p}"
        output = await self._run_command(cmd)
        return json.loads(output)

    async def browser_dialog(self, action: str, profile: Optional[str] = None) -> Dict[str, Any]:
        """处理对话框
        
        Args:
            action: accept, dismiss
        """
        cmd = f"openclaw browser dialog {action} --json"
        if profile or self.profile:
            p = profile or self.profile
            cmd += f" --profile {p}"
        output = await self._run_command(cmd)
        return json.loads(output)

    async def browser_profiles(self) -> Dict[str, Any]:
        """列出所有浏览器配置"""
        cmd = "openclaw browser profiles --json"
        output = await self._run_command(cmd)
        return json.loads(output)

    async def browser_create_profile(self, name: str, cdp_url: Optional[str] = None) -> Dict[str, Any]:
        """创建新的浏览器配置"""
        if cdp_url:
            cmd = f"openclaw browser create-profile --name {name} --cdp-url {cdp_url} --json"
        else:
            cmd = f"openclaw browser create-profile --name {name} --json"
        output = await self._run_command(cmd)
        return json.loads(output)

    async def browser_delete_profile(self, name: str) -> Dict[str, Any]:
        """删除浏览器配置"""
        cmd = f"openclaw browser delete-profile --name {name} --json"
        output = await self._run_command(cmd)
        return json.loads(output)

    async def browser_reset_profile(self, name: str) -> Dict[str, Any]:
        """重置浏览器配置"""
        cmd = f"openclaw browser reset-profile --name {name} --json"
        output = await self._run_command(cmd)
        return json.loads(output)

    async def close(self):
        """关闭 - 占位符方法"""
        pass

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()


class BrowserAutomation:
    """浏览器自动化高级封装"""

    def __init__(self, client: OpenClawBrowserClient):
        self.client = client

    async def open_and_snapshot(self, url: str) -> BrowserSnapshot:
        """打开网页并获取快照"""
        await self.client.browser_open(url)
        await asyncio.sleep(2)
        return await self.client.browser_snapshot(mode="ai")

    async def find_and_click(self, search_text: str, max_attempts: int = 3) -> bool:
        """查找包含文本的元素并点击"""
        for attempt in range(max_attempts):
            snapshot = await self.client.browser_snapshot(mode="ai")
            
            for ref, element in snapshot.refs.items():
                if isinstance(ref, int) and search_text.lower() in str(element).lower():
                    await self.client.browser_act(ref, "click")
                    await asyncio.sleep(1)
                    return True
            
            await asyncio.sleep(1)
        
        return False

    async def type_text(self, ref: int, text: str, clear_first: bool = True) -> None:
        """在元素中输入文本"""
        if clear_first:
            await self.client.browser_act(ref, "click")
            await asyncio.sleep(0.5)
            await self.client.browser_act(ref, "press", value="Control+A")
            await asyncio.sleep(0.2)
        
        await self.client.browser_act(ref, "type", value=text)

    async def wait_for_element(self, search_text: str, timeout: int = 10) -> bool:
        """等待元素出现"""
        for _ in range(timeout):
            snapshot = await self.client.browser_snapshot(mode="ai")
            
            for ref, element in snapshot.refs.items():
                if isinstance(ref, int) and search_text.lower() in str(element).lower():
                    return True
            
            await asyncio.sleep(1)
        
        return False

    async def take_screenshot_and_save(self, filename: str) -> None:
        """截图并保存到文件"""
        result = await self.client.browser_screenshot()
        
        if "data" in result:
            image_data = result["data"]
            if image_data.startswith("data:image"):
                image_data = image_data.split(",")[1]
            
            image_bytes = base64.b64decode(image_data)
            with open(filename, "wb") as f:
                f.write(image_bytes)
