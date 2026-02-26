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
    """最简单的示例 - 打开网页并获取标签页信息"""
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
        
        # 4. 获取标签页列表
        print("\n3. 获取标签页列表...")
        tabs = await client.browser_tabs()
        print(f"   ✓ 标签页数量: {len(tabs)}")
        for i, tab in enumerate(tabs, 1):
            print(f"     {i}. {tab.title} - {tab.url}")
        
        # 5. 导航到新 URL
        print("\n4. 导航到新 URL...")
        await client.browser_navigate("https://www.python.org")
        await asyncio.sleep(2)
        print("   ✓ 已导航到 https://www.python.org")
        
        # 6. 再次获取标签页
        print("\n5. 再次获取标签页列表...")
        tabs = await client.browser_tabs()
        for i, tab in enumerate(tabs, 1):
            print(f"     {i}. {tab.title} - {tab.url}")
        
        print("\n" + "=" * 50)
        print("✓ 示例运行完成！")
        print("=" * 50)


async def profile_example():
    """配置管理示例"""
    print("\n配置管理示例")
    print("=" * 50)
    
    async with OpenClawBrowserClient() as client:
        # 获取浏览器状态
        print("\n1. 获取浏览器状态...")
        status = await client.browser_status()
        print(f"   ✓ 状态: {status}")
        
        # 列出所有配置
        print("\n2. 列出所有浏览器配置...")
        profiles = await client.browser_profiles()
        print(f"   ✓ 配置数量: {len(profiles.get('profiles', []))}")
        for i, profile in enumerate(profiles.get('profiles', []), 1):
            print(f"     {i}. {profile}")
        
        print("\n" + "=" * 50)


async def main():
    """运行所有入门示例"""
    print("OpenClaw Browser 工具 - 入门示例集合")
    print("确保 OpenClaw Gateway 正在运行 (端口 18789)")
    print("=" * 50)
    
    try:
        await simple_example()
        await profile_example()
        
        print("\n" + "=" * 50)
        print("✓ 所有入门示例运行完成！")
        print("=" * 50)
        print("\n下一步:")
        print("  - 查看 example_usage.py 了解更多示例")
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
