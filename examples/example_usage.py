import asyncio
import sys
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from openclaw_browser_client import OpenClawBrowserClient


async def example_1_basic_usage():
    """示例 1: 基本使用 - 检查状态、启动浏览器、打开网页"""
    print("=" * 60)
    print("示例 1: 基本使用")
    print("=" * 60)
    
    async with OpenClawBrowserClient() as client:
        # 检查浏览器状态
        print("\n1. 检查浏览器状态...")
        status = await client.browser_status()
        print(f"状态: {status}")
        
        # 启动浏览器
        print("\n2. 启动浏览器...")
        await client.browser_start()
        print("浏览器已启动")
        
        # 打开网页
        print("\n3. 打开网页...")
        await client.browser_open("https://example.com")
        print("已打开 https://example.com")
        
        # 等待页面加载
        await asyncio.sleep(2)
        
        # 获取标签页列表
        print("\n4. 获取标签页列表...")
        tabs = await client.browser_tabs()
        print(f"标签页数量: {len(tabs)}")
        for i, tab in enumerate(tabs, 1):
            print(f"  {i}. {tab.title} - {tab.url}")


async def example_2_tab_management():
    """示例 2: 标签页管理"""
    print("\n" + "=" * 60)
    print("示例 2: 标签页管理")
    print("=" * 60)
    
    async with OpenClawBrowserClient() as client:
        # 打开多个标签页
        print("\n1. 打开多个标签页...")
        urls = [
            "https://example.com",
            "https://www.python.org",
            "https://github.com"
        ]
        
        for url in urls:
            await client.browser_open(url)
            await asyncio.sleep(1)
            print(f"已打开: {url}")
        
        # 列出所有标签页
        print("\n2. 列出所有标签页...")
        tabs = await client.browser_tabs()
        for i, tab in enumerate(tabs, 1):
            print(f"  {i}. {tab.title} - {tab.url}")
        
        # 导航到新 URL
        print("\n3. 导航到新 URL...")
        if tabs:
            await client.browser_navigate("https://httpbin.org")
            await asyncio.sleep(2)
            print("已导航到 https://httpbin.org")
        
        # 关闭最后一个标签页
        print("\n4. 关闭标签页...")
        tabs = await client.browser_tabs()
        if tabs and tabs[-1].id:
            await client.browser_close(tabs[-1].id)
            print(f"已关闭标签页: {tabs[-1].title}")


async def example_3_profile_management():
    """示例 3: 浏览器配置管理"""
    print("\n" + "=" * 60)
    print("示例 3: 浏览器配置管理")
    print("=" * 60)
    
    async with OpenClawBrowserClient() as client:
        # 列出所有配置
        print("\n1. 列出所有浏览器配置...")
        profiles = await client.browser_profiles()
        print(f"配置列表: {profiles}")
        
        # 创建新配置
        print("\n2. 创建新配置 'test-profile'...")
        try:
            result = await client.browser_create_profile("test-profile")
            print(f"创建结果: {result}")
        except Exception as e:
            print(f"创建配置失败（可能已存在）: {e}")
        
        # 再次列出配置
        print("\n3. 再次列出所有配置...")
        profiles = await client.browser_profiles()
        print(f"更新后的配置列表: {profiles}")


async def example_4_javascript_execution():
    """示例 4: JavaScript 执行"""
    print("\n" + "=" * 60)
    print("示例 4: JavaScript 执行")
    print("=" * 60)
    
    async with OpenClawBrowserClient() as client:
        # 打开网页
        print("\n1. 打开网页...")
        await client.browser_open("https://example.com")
        await asyncio.sleep(2)
        
        # 获取页面标题
        print("\n2. 获取页面标题...")
        result = await client.browser_evaluate("document.title")
        title = result.get("result", "")
        print(f"   页面标题: {title}")
        
        # 获取页面 URL
        print("\n3. 获取页面 URL...")
        result = await client.browser_evaluate("window.location.href")
        url = result.get("result", "")
        print(f"   页面 URL: {url}")
        
        # 获取链接数量
        print("\n4. 获取页面链接数量...")
        result = await client.browser_evaluate("document.querySelectorAll('a').length")
        links_count = result.get("result", 0)
        print(f"   链接数量: {links_count}")
        
        # 获取 H1 元素内容
        print("\n5. 获取 H1 元素内容...")
        result = await client.browser_evaluate("document.querySelector('h1')?.textContent")
        h1_text = result.get("result", "")
        print(f"   H1 内容: {h1_text}")
        
        # 获取页面文本长度
        print("\n6. 获取页面文本长度...")
        result = await client.browser_evaluate("document.body.innerText")
        inner_text = result.get("result", "")
        print(f"   文本长度: {len(inner_text)}")
        
        # 获取页面语言
        print("\n7. 获取页面语言...")
        result = await client.browser_evaluate("document.documentElement.lang")
        lang = result.get("result", "")
        print(f"   页面语言: {lang}")
        
        # 获取页面字符集
        print("\n8. 获取页面字符集...")
        result = await client.browser_evaluate("document.characterSet")
        charset = result.get("result", "")
        print(f"   页面字符集: {charset}")


async def main():
    """运行所有示例"""
    print("OpenClaw Browser 工具 Python 客户端示例")
    print("=" * 60)
    
    try:
        # 运行各个示例
        await example_1_basic_usage()
        await example_2_tab_management()
        await example_3_profile_management()
        await example_4_javascript_execution()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
