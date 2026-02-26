#!/usr/bin/env python3
"""
OpenClaw Browser 命令行工具
提供简单的命令行接口来调用 OpenClaw Browser 工具
"""
import asyncio
import argparse
import sys
import json
from openclaw_browser_client import OpenClawBrowserClient


async def cmd_status(args):
    """检查浏览器状态"""
    async with OpenClawBrowserClient(gateway_url=args.url, token=args.token) as client:
        result = await client.browser_status(profile=args.profile)
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def cmd_start(args):
    """启动浏览器"""
    async with OpenClawBrowserClient(gateway_url=args.url, token=args.token) as client:
        result = await client.browser_start(profile=args.profile)
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def cmd_stop(args):
    """停止浏览器"""
    async with OpenClawBrowserClient(gateway_url=args.url, token=args.token) as client:
        result = await client.browser_stop(profile=args.profile)
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def cmd_open(args):
    """打开 URL"""
    async with OpenClawBrowserClient(gateway_url=args.url, token=args.token) as client:
        result = await client.browser_open(args.url_to_open, profile=args.profile)
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def cmd_tabs(args):
    """列出所有标签页"""
    async with OpenClawBrowserClient(gateway_url=args.url, token=args.token) as client:
        tabs = await client.browser_tabs(profile=args.profile)
        for i, tab in enumerate(tabs, 1):
            print(f"{i}. [{tab.id}] {tab.title}")
            print(f"   URL: {tab.url}")


async def cmd_snapshot(args):
    """获取页面快照"""
    async with OpenClawBrowserClient(gateway_url=args.url, token=args.token) as client:
        snapshot = await client.browser_snapshot(
            mode=args.mode,
            profile=args.profile,
            interactive=args.interactive,
            compact=args.compact
        )
        print("=== 页面快照 ===")
        print(snapshot.content)
        print(f"\n=== 元素引用 ({len(snapshot.refs)} 个) ===")
        for ref, element in list(snapshot.refs.items())[:20]:
            print(f"  {ref}: {str(element)[:100]}")


async def cmd_screenshot(args):
    """截图并保存"""
    async with OpenClawBrowserClient(gateway_url=args.url, token=args.token) as client:
        result = await client.browser_screenshot(profile=args.profile)
        
        if "data" in result:
            import base64
            image_data = result["data"]
            if image_data.startswith("data:image"):
                image_data = image_data.split(",")[1]
            
            image_bytes = base64.b64decode(image_data)
            filename = args.output or "screenshot.png"
            
            with open(filename, "wb") as f:
                f.write(image_bytes)
            print(f"✓ 截图已保存到: {filename}")
        else:
            print("✗ 截图失败")


async def cmd_evaluate(args):
    """执行 JavaScript"""
    async with OpenClawBrowserClient(gateway_url=args.url, token=args.token) as client:
        result = await client.browser_evaluate(args.javascript, profile=args.profile)
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def cmd_profiles(args):
    """列出所有浏览器配置"""
    async with OpenClawBrowserClient(gateway_url=args.url, token=args.token) as client:
        result = await client.browser_profiles()
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def cmd_create_profile(args):
    """创建新的浏览器配置"""
    async with OpenClawBrowserClient(gateway_url=args.url, token=args.token) as client:
        result = await client.browser_create_profile(args.name, args.cdp_url)
        print(json.dumps(result, indent=2, ensure_ascii=False))


async def cmd_delete_profile(args):
    """删除浏览器配置"""
    async with OpenClawBrowserClient(gateway_url=args.url, token=args.token) as client:
        result = await client.browser_delete_profile(args.name)
        print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw Browser 命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 检查状态
  python openclaw_browser_cli.py status
  
  # 启动浏览器
  python openclaw_browser_cli.py start
  
  # 打开网页
  python openclaw_browser_cli.py open https://example.com
  
  # 获取快照
  python openclaw_browser_cli.py snapshot --mode ai
  
  # 截图
  python openclaw_browser_cli.py screenshot --output mypage.png
  
  # 执行 JavaScript
  python openclaw_browser_cli.py evaluate "document.title"
  
  # 列出所有标签页
  python openclaw_browser_cli.py tabs
  
  # 使用认证
  python openclaw_browser_cli.py status --token your-token
        """
    )
    
    # 全局参数
    parser.add_argument("--url", default="ws://127.0.0.1:18789", 
                       help="OpenClaw Gateway WebSocket URL (默认: ws://127.0.0.1:18789)")
    parser.add_argument("--token", help="认证 token (如果启用了认证)")
    parser.add_argument("--profile", help="浏览器配置名称 (默认: chrome)")
    
    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # status 命令
    subparsers.add_parser("status", help="检查浏览器状态")
    
    # start 命令
    subparsers.add_parser("start", help="启动浏览器")
    
    # stop 命令
    subparsers.add_parser("stop", help="停止浏览器")
    
    # open 命令
    open_parser = subparsers.add_parser("open", help="打开 URL")
    open_parser.add_argument("url_to_open", help="要打开的 URL")
    
    # tabs 命令
    subparsers.add_parser("tabs", help="列出所有标签页")
    
    # snapshot 命令
    snapshot_parser = subparsers.add_parser("snapshot", help="获取页面快照")
    snapshot_parser.add_argument("--mode", choices=["ai", "aria"], default="ai",
                                help="快照模式 (默认: ai)")
    snapshot_parser.add_argument("--interactive", action="store_true",
                                help="包含交互元素")
    snapshot_parser.add_argument("--compact", action="store_true",
                                help="紧凑模式")
    
    # screenshot 命令
    screenshot_parser = subparsers.add_parser("screenshot", help="截图")
    screenshot_parser.add_argument("--output", "-o", help="输出文件名 (默认: screenshot.png)")
    
    # evaluate 命令
    eval_parser = subparsers.add_parser("evaluate", help="执行 JavaScript")
    eval_parser.add_argument("javascript", help="要执行的 JavaScript 代码")
    
    # profiles 命令
    subparsers.add_parser("profiles", help="列出所有浏览器配置")
    
    # create-profile 命令
    create_profile_parser = subparsers.add_parser("create-profile", help="创建新的浏览器配置")
    create_profile_parser.add_argument("name", help="配置名称")
    create_profile_parser.add_argument("--cdp-url", help="CDP URL (可选)")
    
    # delete-profile 命令
    delete_profile_parser = subparsers.add_parser("delete-profile", help="删除浏览器配置")
    delete_profile_parser.add_argument("name", help="配置名称")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 命令映射
    commands = {
        "status": cmd_status,
        "start": cmd_start,
        "stop": cmd_stop,
        "open": cmd_open,
        "tabs": cmd_tabs,
        "snapshot": cmd_snapshot,
        "screenshot": cmd_screenshot,
        "evaluate": cmd_evaluate,
        "profiles": cmd_profiles,
        "create-profile": cmd_create_profile,
        "delete-profile": cmd_delete_profile,
    }
    
    # 执行命令
    try:
        asyncio.run(commands[args.command](args))
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
