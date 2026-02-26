import asyncio
import json
import base64
import sys
from datetime import datetime
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from openclaw_browser_client import OpenClawBrowserClient, BrowserSnapshot


class OpenClawBrowserClientTest:
    """OpenClaw Browser 客户端测试套件"""

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
        
        snapshot_dict = {
            "content": snapshot.content if hasattr(snapshot, 'content') else None,
            "refs": snapshot.refs if hasattr(snapshot, 'refs') else {},
            "metadata": snapshot.metadata if hasattr(snapshot, 'metadata') else {},
            "timestamp": datetime.now().isoformat()
        }
        
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
            
            self.log_test("连接到 OpenClaw Gateway", True)
            
            status = await self.client.browser_status()
            self.log_test("获取浏览器状态", True, f"运行中: {status.get('running', False)}")
            
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
            
            profiles = await self.client.browser_profiles()
            self.log_test("获取浏览器配置列表", True, f"配置数量: {len(profiles.get('profiles', []))}")
            
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
            tabs_before = await self.client.browser_tabs()
            self.log_test("获取标签页列表", True, f"标签页数量: {len(tabs_before)}")
            
            result = await self.client.browser_open("https://httpbin.org")
            self.log_test("打开新标签页", True)
            
            await asyncio.sleep(2)
            
            tabs_after = await self.client.browser_tabs()
            self.log_test("验证标签页数量增加", len(tabs_after) > len(tabs_before), 
                        f"之前: {len(tabs_before)}, 之后: {len(tabs_after)}")
            
            await self.client.browser_navigate("https://example.com")
            self.log_test("导航到新 URL", True)
            
            await asyncio.sleep(2)
            
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
            await self.client.browser_navigate("https://example.com")
            await asyncio.sleep(2)
            
            tabs = await self.client.browser_tabs()
            if not tabs:
                self.log_test("页面快照", False, "没有可用的标签页")
                return
            
            snapshot = await self.client.browser_snapshot(mode="ai")
            self.log_test("获取 AI 模式快照", bool(snapshot.content), 
                        f"内容长度: {len(snapshot.content)}, 元素数量: {len(snapshot.refs)}")
            self.save_snapshot(snapshot, "ai_mode")
            
            snapshot_aria = await self.client.browser_snapshot(mode="aria")
            self.log_test("获取 ARIA 模式快照", bool(snapshot_aria.content),
                        f"内容长度: {len(snapshot_aria.content)}")
            self.save_snapshot(snapshot_aria, "aria_mode")
            
            snapshot_compact = await self.client.browser_snapshot(mode="ai", compact=True)
            self.log_test("获取紧凑模式快照", bool(snapshot_compact.content),
                        f"内容长度: {len(snapshot_compact.content)}")
            self.save_snapshot(snapshot_compact, "compact_mode")
            
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
            await self.client.browser_navigate("https://example.com")
            await asyncio.sleep(2)
            
            tabs = await self.client.browser_tabs()
            if not tabs:
                self.log_test("截图功能", False, "没有可用的标签页")
                return
            
            screenshot = await self.client.browser_screenshot()
            
            if "data" in screenshot:
                self.log_test("获取截图", True, f"数据长度: {len(screenshot.get('data', ''))}")
            elif "path" in screenshot:
                self.log_test("获取截图", True, f"文件路径: {screenshot.get('path', '')}")
            else:
                self.log_test("获取截图", False, f"返回字段: {list(screenshot.keys())}")
            
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

    async def test_javascript_execution(self):
        """测试 4: JavaScript 执行"""
        print("\n【测试 4】JavaScript 执行")
        print("-" * 60)
        
        try:
            await self.client.browser_navigate("https://example.com")
            await asyncio.sleep(2)
            
            tabs = await self.client.browser_tabs()
            if not tabs:
                self.log_test("JavaScript 执行", False, "没有可用的标签页")
                return
            
            # 测试 1: 获取页面标题
            print("  [测试 1] 获取页面标题")
            result = await self.client.browser_evaluate("document.title")
            title = result.get("result", "")
            self.log_test("执行简单 JavaScript", bool(title), f"结果: {title}")
            
            # 测试 2: 获取链接数量
            print("  [测试 2] 获取链接数量")
            result = await self.client.browser_evaluate("document.querySelectorAll('a').length")
            links_count = result.get("result", 0)
            self.log_test("执行复杂 JavaScript", True, f"链接数量: {links_count}")
            
            # 测试 3: 获取 H1 元素内容
            print("  [测试 3] 获取 H1 元素内容")
            result = await self.client.browser_evaluate("document.querySelector('h1').textContent")
            h1_text = result.get("result", "")
            self.log_test("获取页面元素", bool(h1_text), f"H1 内容: {h1_text}")
            
            # 测试 4: 修改页面背景颜色
            print("  [测试 4] 修改页面背景颜色")
            result = await self.client.browser_evaluate("document.body.style.backgroundColor = '#f0f0f0'")
            self.log_test("修改页面内容", True, "背景颜色已修改")
            
            # 测试 5: 使用可选链操作符（参考 scrape_comic.py）
            print("  [测试 5] 使用可选链操作符")
            result = await self.client.browser_evaluate("document.querySelector('h1')?.textContent")
            text = result.get("result", "")
            self.log_test("可选链操作符", bool(text), f"结果: {text}")
            
            # 测试 6: 获取 URL 并使用正则表达式（参考 scrape_comic.py）
            print("  [测试 6] 获取 URL 并使用正则表达式")
            result = await self.client.browser_evaluate("window.location.href")
            url = result.get("result", "")
            self.log_test("获取页面 URL", bool(url), f"URL: {url}")
            
            # 测试 7: 使用 innerText 和正则表达式（参考 scrape_comic.py）
            print("  [测试 7] 使用 innerText 和正则表达式")
            result = await self.client.browser_evaluate("document.body.innerText")
            inner_text = result.get("result", "")
            self.log_test("获取页面文本", bool(inner_text), f"文本长度: {len(inner_text)}")
            
            # 测试 8: 查询特定元素（参考 scrape_comic.py）
            print("  [测试 8] 查询特定元素")
            result = await self.client.browser_evaluate("document.querySelector('h1')?.textContent.trim()")
            trimmed_text = result.get("result", "")
            self.log_test("查询并修剪文本", bool(trimmed_text), f"结果: {trimmed_text}")
            
            # 测试 9: 获取元素属性
            print("  [测试 9] 获取元素属性")
            result = await self.client.browser_evaluate("document.querySelector('h1')?.tagName")
            tag_name = result.get("result", "")
            self.log_test("获取元素标签名", bool(tag_name), f"标签名: {tag_name}")
            
            # 测试 10: 获取页面元数据
            print("  [测试 10] 获取页面元数据")
            result = await self.client.browser_evaluate("document.querySelector('meta[name=\"description\"]')?.content")
            description = result.get("result", "")
            self.log_test("获取页面描述", True, f"描述: {description if description else '无描述'}")
            
            # 测试 11: 检查元素是否存在
            print("  [测试 11] 检查元素是否存在")
            result = await self.client.browser_evaluate("document.querySelector('h1') !== null")
            exists = result.get("result", False)
            self.log_test("检查元素存在", exists, f"H1 元素存在: {exists}")
            
            # 测试 12: 获取所有段落文本
            print("  [测试 12] 获取所有段落文本")
            result = await self.client.browser_evaluate("document.querySelectorAll('p').length")
            p_count = result.get("result", 0)
            self.log_test("获取段落数量", True, f"段落数量: {p_count}")
            
            # 测试 13: 获取页面语言
            print("  [测试 13] 获取页面语言")
            result = await self.client.browser_evaluate("document.documentElement.lang")
            lang = result.get("result", "")
            self.log_test("获取页面语言", bool(lang), f"语言: {lang}")
            
            # 测试 14: 获取页面字符集
            print("  [测试 14] 获取页面字符集")
            result = await self.client.browser_evaluate("document.characterSet")
            charset = result.get("result", "")
            self.log_test("获取页面字符集", bool(charset), f"字符集: {charset}")
            
        except Exception as e:
            self.log_test("JavaScript 执行", False, str(e))

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
        print("OpenClaw Browser 客户端测试套件")
        print("=" * 60)
        
        # 设置浏览器环境
        if not await self.setup_browser():
            print("\n环境设置失败，无法继续测试")
            return
        
        # 运行所有测试
        await self.test_tab_management()
        await self.test_page_snapshot()
        await asyncio.sleep(2)
        
        await self.test_screenshot()
        await asyncio.sleep(2)
        
        await self.test_javascript_execution()
        
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
