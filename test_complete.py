import asyncio
import json
import base64
from datetime import datetime
from pathlib import Path
from openclaw_browser_client import OpenClawBrowserClient, BrowserSnapshot, BrowserAutomation


class OpenClawBrowserClientTest:
    """OpenClaw Browser 客户端完整测试套件"""

    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
        self.client = None
        self.logs_dir = Path(__file__).parent / "logs"
        self.logs_dir.mkdir(exist_ok=True)
    
    def save_snapshot(self, snapshot: BrowserSnapshot, step_name: str):
        """保存快照到JSON文件"""
        if not snapshot:
            print(f"快照为空，无法保存: {step_name}")
            return
        
        # 转换为字典
        snapshot_dict = {
            "content": snapshot.content if hasattr(snapshot, 'content') else None,
            "refs": snapshot.refs if hasattr(snapshot, 'refs') else {},
            "metadata": snapshot.metadata if hasattr(snapshot, 'metadata') else {},
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存到文件
        filename = self.logs_dir / f"snapshot_{step_name}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(snapshot_dict, f, ensure_ascii=False, indent=2)
        
        print(f"快照已保存到: {filename}")
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """记录测试结果"""
        status = "✓ PASS" if passed else "✗ FAIL"
        self.test_results.append({
            "name": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        print(f"{status}: {test_name}")
        if message:
            print(f"  {message}")

    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "=" * 60)
        print("测试摘要")
        print("=" * 60)
        print(f"总计: {self.passed + self.failed}")
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")
        if self.passed + self.failed > 0:
            print(f"通过率: {self.passed / (self.passed + self.failed) * 100:.1f}%")
        print("=" * 60)

    async def setup_browser(self):
        """设置浏览器环境"""
        print("\n【环境设置】启动浏览器并打开测试页面")
        print("-" * 60)
        
        try:
            self.client = OpenClawBrowserClient()
            await self.client.connect()
            
            # 测试连接
            self.log_test("连接到 OpenClaw Gateway", True)
            
            # 检查浏览器状态
            status = await self.client.browser_status()
            self.log_test("获取浏览器状态", True, f"运行中: {status.get('running', False)}")
            
            # 如果浏览器未运行，尝试启动
            if not status.get('running', False):
                print("  浏览器未运行，正在启动...")
                try:
                    await self.client.browser_start()
                    await asyncio.sleep(3)
                    self.log_test("启动浏览器", True)
                except Exception as e:
                    print(f"  启动浏览器失败: {e}")
                    print("  请确保：")
                    print("  1. Chrome 浏览器已打开")
                    print("  2. OpenClaw 扩展已安装")
                    print("  3. 点击扩展图标连接标签页")
                    return False
            else:
                self.log_test("浏览器已在运行", True)
            
            # 获取配置列表
            profiles = await self.client.browser_profiles()
            self.log_test("获取浏览器配置列表", True, f"配置数量: {len(profiles.get('profiles', []))}")
            
            # 打开测试页面
            print("  正在打开测试页面...")
            await self.client.browser_open("https://example.com")
            await asyncio.sleep(2)
            self.log_test("打开测试页面", True, "https://example.com")
            
            return True
            
        except Exception as e:
            self.log_test("环境设置", False, str(e))
            return False

    async def test_tab_management(self):
        """测试 1: 标签页管理"""
        print("\n【测试 1】标签页管理")
        print("-" * 60)
        
        try:
            # 获取标签页列表
            tabs_before = await self.client.browser_tabs()
            self.log_test("获取标签页列表", True, f"标签页数量: {len(tabs_before)}")
            
            # 打开新标签页
            result = await self.client.browser_open("https://httpbin.org")
            self.log_test("打开新标签页", True)
            
            # 等待页面加载
            await asyncio.sleep(2)
            
            # 验证标签页数量增加
            tabs_after = await self.client.browser_tabs()
            self.log_test("验证标签页数量增加", len(tabs_after) > len(tabs_before), 
                        f"之前: {len(tabs_before)}, 之后: {len(tabs_after)}")
            
            # 导航到新 URL - 直接导航，不需要 focus
            await self.client.browser_navigate("https://example.com")
            self.log_test("导航到新 URL", True)
            
            await asyncio.sleep(2)
            
            # 关闭标签页 - 重新获取以确保ID有效
            tabs_final = await self.client.browser_tabs()
            if tabs_final and tabs_final[-1].id:
                await self.client.browser_close(tabs_final[-1].id)
                self.log_test("关闭标签页", True)
            else:
                self.log_test("关闭标签页", False, "没有有效的标签页 ID")
                
        except Exception as e:
            self.log_test("标签页管理", False, str(e))

    async def test_page_snapshot(self):
        """测试 2: 页面快照"""
        print("\n【测试 2】页面快照")
        print("-" * 60)
        
        try:
            # 确保 example.com 页面已打开
            await self.client.browser_navigate("https://example.com")
            await asyncio.sleep(2)
            
            # 验证页面已打开
            tabs = await self.client.browser_tabs()
            if not tabs:
                self.log_test("页面快照", False, "没有可用的标签页")
                return
            
            # 测试 AI 模式快照
            snapshot = await self.client.browser_snapshot(mode="ai")
            self.log_test("获取 AI 模式快照", bool(snapshot.content), 
                        f"内容长度: {len(snapshot.content)}, 元素数量: {len(snapshot.refs)}")
            self.save_snapshot(snapshot, "ai_mode")
            
            # 测试 ARIA 模式快照
            snapshot_aria = await self.client.browser_snapshot(mode="aria")
            self.log_test("获取 ARIA 模式快照", bool(snapshot_aria.content),
                        f"内容长度: {len(snapshot_aria.content)}")
            self.save_snapshot(snapshot_aria, "aria_mode")
            
            # 测试紧凑模式快照
            snapshot_compact = await self.client.browser_snapshot(mode="ai", compact=True)
            self.log_test("获取紧凑模式快照", bool(snapshot_compact.content),
                        f"内容长度: {len(snapshot_compact.content)}")
            self.save_snapshot(snapshot_compact, "compact_mode")
            
            # 测试交互元素快照
            snapshot_interactive = await self.client.browser_snapshot(mode="ai", interactive=True)
            self.log_test("获取交互元素快照", bool(snapshot_interactive.content),
                        f"元素数量: {len(snapshot_interactive.refs)}")
            self.save_snapshot(snapshot_interactive, "interactive_mode")
            
        except Exception as e:
            self.log_test("页面快照", False, str(e))

    async def test_screenshot(self):
        """测试 3: 截图功能"""
        print("\n【测试 3】截图功能")
        print("-" * 60)
        
        try:
            # 确保页面已打开
            await self.client.browser_navigate("https://example.com")
            await asyncio.sleep(2)
            
            # 验证页面已打开
            tabs = await self.client.browser_tabs()
            if not tabs:
                self.log_test("截图功能", False, "没有可用的标签页")
                return
            
            # 测试截图
            screenshot = await self.client.browser_screenshot()
            
            # 检查返回的字段
            if "data" in screenshot:
                self.log_test("获取截图", True, f"数据长度: {len(screenshot.get('data', ''))}")
            elif "path" in screenshot:
                self.log_test("获取截图", True, f"文件路径: {screenshot.get('path', '')}")
            else:
                self.log_test("获取截图", False, f"返回字段: {list(screenshot.keys())}")
            
            # 保存截图到文件
            if "data" in screenshot and screenshot["data"]:
                image_data = screenshot["data"]
                if image_data.startswith("data:image"):
                    image_data = image_data.split(",")[1]
                
                image_bytes = base64.b64decode(image_data)
                screenshot_path = self.logs_dir / "test_screenshot.png"
                with open(screenshot_path, "wb") as f:
                    f.write(image_bytes)
                self.log_test("保存截图到文件", True, f"已保存到 {screenshot_path}")
            elif "path" in screenshot:
                # 截图已经保存到文件，复制到 logs 目录
                import shutil
                source_path = screenshot["path"]
                screenshot_path = self.logs_dir / "test_screenshot.png"
                try:
                    shutil.copy(source_path, screenshot_path)
                    self.log_test("保存截图到文件", True, f"已复制到 {screenshot_path}")
                except Exception as e:
                    self.log_test("保存截图到文件", False, f"复制失败: {e}")
            else:
                self.log_test("保存截图到文件", False, "没有可用的截图数据")
            
        except Exception as e:
            self.log_test("截图功能", False, str(e))

    async def test_ui_actions(self):
        """测试 4: UI 操作"""
        print("\n【测试 4】UI 操作")
        print("-" * 60)
        
        try:
            # 打开表单测试页面
            await self.client.browser_open("https://httpbin.org/forms/post")
            await asyncio.sleep(2)
            
            # 获取快照
            snapshot = await self.client.browser_snapshot(mode="ai")
            self.log_test("获取页面快照用于 UI 操作", True, f"元素数量: {len(snapshot.refs)}")
            
            # 测试点击操作 - 查找第一个字符串类型的引用
            clickable_ref = None
            for ref, element in snapshot.refs.items():
                if isinstance(ref, str) and element.get('role') in ['link', 'button']:
                    clickable_ref = ref
                    break
            
            if clickable_ref is not None:
                try:
                    await self.client.browser_act(clickable_ref, "click")
                    self.log_test("执行点击操作", True, f"元素 ref: {clickable_ref}")
                    await asyncio.sleep(1)  # 等待页面稳定
                except Exception as e:
                    self.log_test("执行点击操作", False, str(e))
            else:
                self.log_test("执行点击操作", False, "没有找到有效的元素引用")
            
            # 测试按键操作
            try:
                await self.client.browser_act(0, "press", value="Tab")
                self.log_test("执行按键操作", True, "按键: Tab")
                await asyncio.sleep(1)  # 等待页面稳定
            except Exception as e:
                self.log_test("执行按键操作", False, str(e))
            
            # 测试等待操作
            try:
                await self.client.browser_act(0, "wait", value="1000")
                self.log_test("执行等待操作", True, "等待 1 秒")
            except Exception as e:
                self.log_test("执行等待操作", False, str(e))
            
        except Exception as e:
            self.log_test("UI 操作", False, str(e))

    async def test_javascript_execution(self):
        """测试 5: JavaScript 执行"""
        print("\n【测试 5】JavaScript 执行")
        print("-" * 60)
        
        try:
            # 确保 example.com 页面已打开
            await self.client.browser_navigate("https://example.com")
            await asyncio.sleep(2)
            
            # 验证页面已打开
            tabs = await self.client.browser_tabs()
            if not tabs:
                self.log_test("JavaScript 执行", False, "没有可用的标签页")
                return
            
            # 测试简单 JavaScript
            result = await self.client.browser_evaluate("document.title")
            title = result.get("result", "")
            self.log_test("执行简单 JavaScript", bool(title), f"结果: {title}")
            
            # 测试复杂 JavaScript
            result = await self.client.browser_evaluate("const links = document.querySelectorAll('a'); return links.length;")
            links_count = result.get("result", 0)
            self.log_test("执行复杂 JavaScript", True, f"链接数量: {links_count}")
            
            # 测试获取页面元素
            result = await self.client.browser_evaluate("const h1 = document.querySelector('h1'); return h1 ? h1.textContent : null;")
            h1_text = result.get("result", "")
            self.log_test("获取页面元素", bool(h1_text), f"H1 内容: {h1_text}")
            
            # 测试修改页面内容
            result = await self.client.browser_evaluate("document.body.style.backgroundColor = '#f0f0f0'; return 'Background color changed';")
            bg_result = result.get("result", "")
            self.log_test("修改页面内容", bool(bg_result), f"结果: {bg_result}")
            
        except Exception as e:
            self.log_test("JavaScript 执行", False, str(e))

    async def test_console_logs(self):
        """测试 6: 控制台日志"""
        print("\n【测试 6】控制台日志")
        print("-" * 60)
        
        try:
            # 检查当前标签页状态
            print("  [DEBUG] 检查当前标签页状态...")
            tabs = await self.client.browser_tabs()
            print(f"  [DEBUG] 当前标签页数量: {len(tabs)}")
            
            # 确保 example.com 页面已打开
            print("  [DEBUG] 导航到 example.com...")
            await self.client.browser_navigate("https://example.com")
            await asyncio.sleep(2)
            
            # 验证页面已打开
            print("  [DEBUG] 验证页面已打开...")
            tabs = await self.client.browser_tabs()
            if not tabs:
                self.log_test("控制台日志", False, "没有可用的标签页")
                return
            
            # 执行一些 JavaScript 产生日志
            print("  [DEBUG] 产生控制台日志...")
            await self.client.browser_evaluate("console.log('Test log from Python client')")
            await self.client.browser_evaluate("console.warn('Test warning from Python client')")
            await self.client.browser_evaluate("console.error('Test error from Python client')")
            
            # 获取控制台日志
            print("  [DEBUG] 获取控制台日志...")
            console = await self.client.browser_console()
            log_count = len(console.get('logs', []))
            self.log_test("获取控制台日志", log_count > 0, f"日志数量: {log_count}")
            
        except Exception as e:
            self.log_test("控制台日志", False, str(e))

    async def test_profile_management(self):
        """测试 7: 配置管理"""
        print("\n【测试 7】配置管理")
        print("-" * 60)
        
        try:
            # 测试列出所有配置
            profiles = await self.client.browser_profiles()
            self.log_test("列出所有配置", True, f"配置数量: {len(profiles.get('profiles', []))}")
            
            # 测试创建新配置
            test_profile_name = "test-profile-python"
            try:
                # 先尝试删除可能存在的配置
                try:
                    await self.client.browser_delete_profile(test_profile_name)
                    await asyncio.sleep(1)
                except:
                    pass
                
                # 创建新配置
                result = await self.client.browser_create_profile(test_profile_name)
                self.log_test("创建新配置", True, f"配置名: {test_profile_name}")
                
                # 验证配置已创建
                profiles_after = await self.client.browser_profiles()
                profile_names = [p.get('name') for p in profiles_after.get('profiles', [])]
                self.log_test("验证配置已创建", test_profile_name in profile_names)
                
                # 测试删除配置
                await self.client.browser_delete_profile(test_profile_name)
                self.log_test("删除配置", True, f"已删除: {test_profile_name}")
                
                # 验证配置已删除
                profiles_final = await self.client.browser_profiles()
                profile_names_final = [p.get('name') for p in profiles_final.get('profiles', [])]
                self.log_test("验证配置已删除", test_profile_name not in profile_names_final)
                
            except Exception as e:
                self.log_test("配置管理", False, str(e))
            
        except Exception as e:
            self.log_test("配置管理", False, str(e))

    async def test_automation_features(self):
        """测试 8: 自动化功能"""
        print("\n【测试 8】自动化功能")
        print("-" * 60)
        
        try:
            # 确保页面已打开
            await self.client.browser_navigate("https://example.com")
            await asyncio.sleep(2)
            
            # 验证页面已打开
            tabs = await self.client.browser_tabs()
            if not tabs:
                self.log_test("自动化功能", False, "没有可用的标签页")
                return
            
            automation = BrowserAutomation(self.client)
            
            # 测试打开并获取快照
            snapshot = await automation.open_and_snapshot("https://example.com")
            self.log_test("自动化打开并获取快照", bool(snapshot.content),
                        f"内容长度: {len(snapshot.content)}")
            
            # 测试查找并点击元素
            found = await automation.find_and_click("Learn more", max_attempts=2)
            self.log_test("自动化查找并点击元素", found, "找到并点击了元素")
            
            # 测试等待元素
            await self.client.browser_navigate("https://example.com")
            await asyncio.sleep(2)
            element_found = await automation.wait_for_element("Example", timeout=5)
            self.log_test("自动化等待元素", element_found, "找到元素")
            
            # 测试截图并保存
            screenshot_path = self.logs_dir / "test_automation_screenshot.png"
            await automation.take_screenshot_and_save(str(screenshot_path))
            self.log_test("自动化截图并保存", True, f"已保存到 {screenshot_path}")
            
        except Exception as e:
            self.log_test("自动化功能", False, str(e))

    async def test_error_handling(self):
        """测试 9: 错误处理"""
        print("\n【测试 9】错误处理")
        print("-" * 60)
        
        try:
            # 测试无效的 URL
            try:
                result = await self.client.browser_open("invalid://not-a-valid-url")
                # 检查结果是否包含错误信息
                if isinstance(result, dict) and ("error" in result or "status" in result):
                    self.log_test("无效 URL 错误处理", True, f"正确处理错误: {result.get('error', result.get('status', ''))}")
                else:
                    self.log_test("无效 URL 错误处理", False, f"未正确处理错误，结果: {result}")
            except Exception as e:
                self.log_test("无效 URL 错误处理", True, f"正确捕获异常: {str(e)[:50]}")
            
            # 测试无效的操作类型
            try:
                await self.client.browser_act(0, "invalid_action")
                self.log_test("无效操作类型错误处理", False, "应该抛出异常")
            except ValueError as e:
                self.log_test("无效操作类型错误处理", True, f"正确捕获异常: {str(e)}")
            except Exception as e:
                self.log_test("无效操作类型错误处理", True, f"正确捕获异常: {str(e)[:50]}")
            
            # 测试无效的 JavaScript
            try:
                await self.client.browser_evaluate("invalid javascript syntax")
                self.log_test("无效 JavaScript 错误处理", False, "应该抛出异常")
            except Exception as e:
                self.log_test("无效 JavaScript 错误处理", True, f"正确捕获异常: {str(e)[:50]}")
            
        except Exception as e:
            self.log_test("错误处理", False, str(e))

    async def cleanup(self):
        """清理环境"""
        print("\n【环境清理】")
        print("-" * 60)
        
        try:
            if self.client:
                await self.client.close()
                self.log_test("关闭客户端连接", True)
        except Exception as e:
            self.log_test("环境清理", False, str(e))

    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("OpenClaw Browser 客户端完整测试套件")
        print("=" * 60)
        
        # 设置浏览器环境
        if not await self.setup_browser():
            print("\n环境设置失败，无法继续测试")
            return
        
        # 运行所有测试
        await self.test_tab_management()
        await self.test_page_snapshot()
        await asyncio.sleep(3)  # 添加等待时间
        
        await self.test_screenshot()
        await asyncio.sleep(3)  # 添加等待时间
        
        await self.test_ui_actions()
        await asyncio.sleep(3)  # 添加等待时间
        
        await self.test_javascript_execution()
        await asyncio.sleep(3)  # 添加等待时间
        
        await self.test_console_logs()
        await asyncio.sleep(3)  # 添加等待时间
        
        await self.test_profile_management()
        await asyncio.sleep(3)  # 添加等待时间
        
        await self.test_automation_features()
        await asyncio.sleep(3)  # 添加等待时间
        
        await self.test_error_handling()
        
        # 清理环境
        await self.cleanup()
        
        # 打印测试摘要
        self.print_summary()
        
        # 保存测试结果到文件
        with open("test_results.json", "w", encoding="utf-8") as f:
            json.dump({
                "passed": self.passed,
                "failed": self.failed,
                "total": self.passed + self.failed,
                "pass_rate": f"{self.passed / (self.passed + self.failed) * 100:.1f}%" if (self.passed + self.failed) > 0 else "0%",
                "results": self.test_results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试结果已保存到 test_results.json")


async def main():
    """主函数"""
    tester = OpenClawBrowserClientTest()
    await tester.run_all_tests()


if __name__ == "__main__":
    print("注意：请确保在 Chrome 中点击了 OpenClaw 扩展图标并连接了标签页")
    print("如果扩展图标显示红色感叹号，请确保 Gateway 正在运行")
    print()
    asyncio.run(main())
