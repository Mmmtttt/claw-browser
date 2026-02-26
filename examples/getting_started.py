"""
OpenClaw Browser 工具 - 入门示例
最简单的使用示例，帮助快速上手
"""
import asyncio
import sys
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from openclaw_browser_client import OpenClawBrowserClient


async def simple_example():
    """最简单的示例 - 打开网页并截图"""
    print("OpenClaw Browser 入门示例")
    print("=" * 50)
    
    # 创建客户端并连接
    async with OpenClawBrowserClient() as client:
        # 1. 启动浏览器
        print("\n1. 启动浏览器...")
        await client.browser_start()
        print("   ✓ 浏览器已启动")
        
        # 2. 打开网页
        print("\n2. 打开网页...")
        await client.browser_open("https://example.com")
        print("   ✓ 已打开 https://example.com")
        
        # 3. 等待页面加载
        await asyncio.sleep(2)
        
        # 4. 获取页面快照
        print("\n3. 获取页面快照...")
        snapshot = await client.browser_snapshot(mode="ai")
        print(f"   ✓ 快照获取成功")
        print(f"   页面标题: {snapshot.content[:100]}...")
        
        # 5. 截图
        print("\n4. 截图...")
        result = await client.browser_screenshot()
        print("   ✓ 截图完成")
        
        print("\n" + "=" * 50)
        print("✓ 示例运行完成！")
        print("=" * 50)


async def search_example():
    """搜索示例 - 在 Google 搜索"""
    print("\nGoogle 搜索示例")
    print("=" * 50)
    
    async with OpenClawBrowserClient() as client:
        # 打开 Google
        print("\n1. 打开 Google...")
        await client.browser_open("https://www.google.com")
        await asyncio.sleep(2)
        
        # 获取快照
        print("\n2. 获取页面快照...")
        snapshot = await client.browser_snapshot(mode="ai")
        
        # 查找搜索框
        print("\n3. 查找搜索框...")
        search_ref = None
        for ref, element in snapshot.refs.items():
            if isinstance(ref, int):
                element_str = str(element).lower()
                if "search" in element_str or "input" in element_str:
                    search_ref = ref
                    print(f"   ✓ 找到搜索框 (ref={ref})")
                    break
        
        if search_ref:
            # 输入搜索内容
            print("\n4. 输入搜索内容...")
            await client.browser_act(search_ref, "click")
            await asyncio.sleep(0.5)
            await client.browser_act(search_ref, "press", value="Control+A")
            await asyncio.sleep(0.2)
            await client.browser_act(search_ref, "type", value="OpenClaw AI")
            print("   ✓ 已输入: OpenClaw AI")
            
            # 按回车搜索
            print("\n5. 执行搜索...")
            await client.browser_act(search_ref, "press", value="Enter")
            await asyncio.sleep(3)
            print("   ✓ 搜索完成")
            
            # 获取搜索结果
            print("\n6. 获取搜索结果...")
            snapshot = await client.browser_snapshot(mode="ai")
            print(f"   ✓ 搜索结果预览:")
            print(f"   {snapshot.content[:300]}...")
        else:
            print("   ✗ 未找到搜索框")
        
        print("\n" + "=" * 50)


async def javascript_example():
    """JavaScript 执行示例"""
    print("\nJavaScript 执行示例")
    print("=" * 50)
    
    async with OpenClawBrowserClient() as client:
        # 打开网页
        print("\n1. 打开网页...")
        await client.browser_open("https://example.com")
        await asyncio.sleep(2)
        
        # 执行 JavaScript
        print("\n2. 执行 JavaScript 获取页面标题...")
        result = await client.browser_evaluate("document.title")
        print(f"   ✓ 页面标题: {result}")
        
        print("\n3. 执行 JavaScript 获取页面 URL...")
        result = await client.browser_evaluate("window.location.href")
        print(f"   ✓ 页面 URL: {result}")
        
        print("\n4. 执行 JavaScript 修改页面背景色...")
        await client.browser_evaluate("document.body.style.backgroundColor = '#f0f0f0'")
        print("   ✓ 背景色已修改")
        
        print("\n5. 执行 JavaScript 添加内容...")
        await client.browser_evaluate("document.body.innerHTML += '<h1>Hello from Python!</h1>'")
        print("   ✓ 内容已添加")
        
        print("\n" + "=" * 50)


async def main():
    """运行所有入门示例"""
    print("OpenClaw Browser 工具 - 入门示例集合")
    print("确保 OpenClaw Gateway 正在运行 (端口 18789)")
    print("=" * 50)
    
    try:
        await simple_example()
        await search_example()
        await javascript_example()
        
        print("\n" + "=" * 50)
        print("✓ 所有入门示例运行完成！")
        print("=" * 50)
        print("\n下一步:")
        print("  - 查看 example_usage.py 了解更多高级示例")
        print("  - 使用 openclaw_browser_cli.py 进行命令行操作")
        print("  - 阅读 README.md 了解完整文档")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        print("\n请检查:")
        print("  1. OpenClaw Gateway 是否正在运行")
        print("  2. 运行: openclaw gateway --port 18789")
        print("  3. 或访问: http://127.0.0.1:18789/")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
