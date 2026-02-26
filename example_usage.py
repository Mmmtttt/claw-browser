import asyncio
from openclaw_browser_client import OpenClawBrowserClient, BrowserAutomation


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
        
        # 获取快照
        print("\n4. 获取页面快照...")
        snapshot = await client.browser_snapshot(mode="ai")
        print(f"快照内容:\n{snapshot.content[:500]}...")
        
        # 截图
        print("\n5. 截图...")
        screenshot = await client.browser_screenshot()
        print(f"截图结果: {screenshot}")


async def example_2_google_search():
    """示例 2: Google 搜索"""
    print("\n" + "=" * 60)
    print("示例 2: Google 搜索")
    print("=" * 60)
    
    async with OpenClawBrowserClient() as client:
        automation = BrowserAutomation(client)
        
        # 打开 Google
        print("\n1. 打开 Google...")
        await client.browser_open("https://www.google.com")
        await asyncio.sleep(2)
        
        # 获取快照
        print("\n2. 获取页面快照...")
        snapshot = await client.browser_snapshot(mode="ai")
        print(f"找到 {len(snapshot.refs)} 个可交互元素")
        
        # 查找搜索框并输入
        print("\n3. 查找搜索框...")
        search_ref = None
        for ref, element in snapshot.refs.items():
            if isinstance(ref, int):
                element_str = str(element).lower()
                if "search" in element_str or "input" in element_str:
                    search_ref = ref
                    print(f"找到搜索框: ref={ref}")
                    break
        
        if search_ref:
            print("\n4. 输入搜索内容...")
            await automation.type_text(search_ref, "OpenClaw AI assistant")
            await asyncio.sleep(1)
            
            print("\n5. 按回车搜索...")
            await client.browser_act(search_ref, "press", value="Enter")
            await asyncio.sleep(3)
            
            print("\n6. 获取搜索结果快照...")
            snapshot = await client.browser_snapshot(mode="ai")
            print(f"搜索结果快照:\n{snapshot.content[:800]}...")
        else:
            print("未找到搜索框")


async def example_3_tab_management():
    """示例 3: 标签页管理"""
    print("\n" + "=" * 60)
    print("示例 3: 标签页管理")
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
        
        # 切换到第一个标签页
        if tabs:
            print(f"\n3. 切换到第一个标签页...")
            await client.browser_focus(tabs[0].id)
            await asyncio.sleep(1)
            
            # 获取快照
            snapshot = await client.browser_snapshot(mode="ai")
            print(f"当前页面: {snapshot.content[:200]}...")


async def example_4_javascript_execution():
    """示例 4: 执行 JavaScript"""
    print("\n" + "=" * 60)
    print("示例 4: 执行 JavaScript")
    print("=" * 60)
    
    async with OpenClawBrowserClient() as client:
        # 打开网页
        print("\n1. 打开网页...")
        await client.browser_open("https://example.com")
        await asyncio.sleep(2)
        
        # 执行 JavaScript 获取页面标题
        print("\n2. 执行 JavaScript 获取页面标题...")
        result = await client.browser_evaluate("document.title")
        print(f"页面标题: {result}")
        
        # 执行 JavaScript 获取页面 URL
        print("\n3. 执行 JavaScript 获取页面 URL...")
        result = await client.browser_evaluate("window.location.href")
        print(f"页面 URL: {result}")
        
        # 执行 JavaScript 修改页面内容
        print("\n4. 执行 JavaScript 修改页面内容...")
        await client.browser_evaluate("document.body.style.backgroundColor = '#f0f0f0'")
        await client.browser_evaluate("document.body.innerHTML += '<h1>Hello from Python!</h1>'")
        await asyncio.sleep(1)
        
        # 获取修改后的快照
        snapshot = await client.browser_snapshot(mode="ai")
        print(f"修改后的页面:\n{snapshot.content[:500]}...")


async def example_5_profile_management():
    """示例 5: 浏览器配置管理"""
    print("\n" + "=" * 60)
    print("示例 5: 浏览器配置管理")
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


async def example_6_with_authentication():
    """示例 6: 使用认证"""
    print("\n" + "=" * 60)
    print("示例 6: 使用认证")
    print("=" * 60)
    
    # 如果你的 Gateway 启用了认证，取消下面的注释并设置你的 token
    token = None  # 替换为你的实际 token
    
    if token:
        async with OpenClawBrowserClient(token=token) as client:
            print("\n1. 使用认证连接...")
            status = await client.browser_status()
            print(f"认证成功，状态: {status}")
    else:
        print("\n跳过认证示例（未设置 token）")


async def example_7_advanced_automation():
    """示例 7: 高级自动化 - 完整的浏览流程"""
    print("\n" + "=" * 60)
    print("示例 7: 高级自动化")
    print("=" * 60)
    
    async with OpenClawBrowserClient() as client:
        automation = BrowserAutomation(client)
        
        # 打开并快照
        print("\n1. 打开 GitHub 并获取快照...")
        snapshot = await automation.open_and_snapshot("https://github.com")
        print(f"快照内容:\n{snapshot.content[:600]}...")
        
        # 等待特定元素
        print("\n2. 等待搜索框出现...")
        found = await automation.wait_for_element("search", timeout=5)
        print(f"搜索框{'已找到' if found else '未找到'}")
        
        # 查找并点击
        print("\n3. 查找并点击 'Sign in'...")
        clicked = await automation.find_and_click("Sign in", max_attempts=2)
        print(f"{'成功点击' if clicked else '未找到或点击失败'}")
        
        await asyncio.sleep(2)
        
        # 截图保存
        print("\n4. 截图并保存...")
        try:
            await automation.take_screenshot_and_save("screenshot.png")
            print("截图已保存到 screenshot.png")
        except Exception as e:
            print(f"截图保存失败: {e}")


async def main():
    """运行所有示例"""
    print("OpenClaw Browser 工具 Python 客户端示例")
    print("=" * 60)
    
    try:
        # 运行各个示例
        await example_1_basic_usage()
        await example_2_google_search()
        await example_3_tab_management()
        await example_4_javascript_execution()
        await example_5_profile_management()
        await example_6_with_authentication()
        await example_7_advanced_automation()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
