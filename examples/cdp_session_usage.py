"""CDP Session 使用示例

演示如何使用 AeroTest 的 CDP 集成功能连接浏览器并获取 DOM

注意：运行前需要先启动 Chrome/Edge 并开启远程调试：
    chrome.exe --remote-debugging-port=9222

Week 3 功能展示：
- CDP 连接管理
- 页面导航
- DOM 获取
- 基本页面操作
"""

import asyncio
from pathlib import Path

from aerotest.browser.cdp import CDPConnection, CDPConnectionConfig, CDPSession
from aerotest.browser.dom import DomService
from aerotest.utils import get_logger

logger = get_logger("examples.cdp_session")


async def example1_basic_connection():
    """示例 1: 基础连接"""
    print("\n" + "=" * 60)
    print("示例 1: 基础连接")
    print("=" * 60)
    
    # 1. 创建连接配置
    config = CDPConnectionConfig(
        host="localhost",
        port=9222,
        timeout=30.0,
    )
    
    # 2. 创建连接
    connection = CDPConnection(config)
    
    try:
        # 3. 连接到浏览器
        await connection.connect()
        print(f"✅ 已连接到浏览器: {config.http_url}")
        
        # 4. 获取可用目标
        targets = await connection.get_targets()
        print(f"\n📋 找到 {len(targets)} 个页面:")
        for i, target in enumerate(targets, 1):
            print(f"   {i}. {target.title or '(无标题)'}")
            print(f"      URL: {target.url}")
            print(f"      ID: {target.target_id}")
        
    finally:
        # 5. 断开连接
        await connection.disconnect()
        print("\n✅ 已断开连接")


async def example2_create_session():
    """示例 2: 创建会话"""
    print("\n" + "=" * 60)
    print("示例 2: 创建会话")
    print("=" * 60)
    
    # 1. 使用默认配置连接
    async with CDPSession.connect() as session:
        print(f"✅ 会话已创建")
        print(f"   目标 ID: {session.target_info.target_id}")
        print(f"   会话 ID: {session.session_id}")
        print(f"   当前 URL: {session.target_info.url}")


async def example3_navigate():
    """示例 3: 页面导航"""
    print("\n" + "=" * 60)
    print("示例 3: 页面导航")
    print("=" * 60)
    
    async with CDPSession.connect() as session:
        # 导航到目标页面
        url = "https://example.com"
        print(f"\n🔄 正在导航到: {url}")
        
        success = await session.navigate(url)
        
        if success:
            print(f"✅ 导航成功")
            
            # 获取页面信息
            title = await session.get_page_title()
            current_url = await session.get_page_url()
            
            print(f"   标题: {title}")
            print(f"   URL: {current_url}")


async def example4_get_dom():
    """示例 4: 获取 DOM 树"""
    print("\n" + "=" * 60)
    print("示例 4: 获取 DOM 树")
    print("=" * 60)
    
    async with CDPSession.connect() as session:
        # 导航到测试页面
        await session.navigate("https://example.com")
        
        # 获取 DOM 树
        print("\n🔄 正在获取 DOM 树...")
        dom_tree = await session.get_dom_tree()
        
        print(f"✅ DOM 树获取成功")
        print(f"   根节点: {dom_tree.node_name}")
        print(f"   节点类型: {dom_tree.node_type}")
        print(f"   后端节点 ID: {dom_tree.backend_node_id}")


async def example5_dom_service_integration():
    """示例 5: DomService 集成（核心功能）"""
    print("\n" + "=" * 60)
    print("示例 5: DomService 集成（核心功能）")
    print("=" * 60)
    
    async with CDPSession.connect() as session:
        # 导航到目标页面
        await session.navigate("https://example.com")
        
        # 方法 1: 手动获取 DOM 并使用 DomService
        print("\n方法 1: 手动流程")
        dom_tree = await session.get_dom_tree()
        
        service = DomService()
        state, timing = service.serialize_dom_tree(dom_tree)
        
        print(f"   ✅ 找到 {len(state.selector_map)} 个可交互元素")
        print(f"   ⏱️ 序列化耗时: {timing.get('serialize_accessible_elements_total', 0)*1000:.1f}ms")
        
        # 获取 LLM 表示
        llm_repr = service.get_llm_representation(state)
        print(f"\n📝 LLM 表示预览（前 500 字符）:")
        print(llm_repr[:500])


async def example6_screenshot():
    """示例 6: 截图"""
    print("\n" + "=" * 60)
    print("示例 6: 截图")
    print("=" * 60)
    
    async with CDPSession.connect() as session:
        # 导航到目标页面
        await session.navigate("https://example.com")
        
        # 截图
        print("\n📸 正在截图...")
        screenshot_data = await session.screenshot()
        
        # 保存截图
        screenshot_path = Path("screenshot.png")
        screenshot_path.write_bytes(screenshot_data)
        
        print(f"✅ 截图已保存: {screenshot_path.absolute()}")
        print(f"   大小: {len(screenshot_data)} 字节 ({len(screenshot_data)/1024:.1f} KB)")


async def example7_execute_javascript():
    """示例 7: 执行 JavaScript"""
    print("\n" + "=" * 60)
    print("示例 7: 执行 JavaScript")
    print("=" * 60)
    
    async with CDPSession.connect() as session:
        await session.navigate("https://example.com")
        
        # 执行 JavaScript
        print("\n🔧 执行 JavaScript...")
        
        # 获取窗口大小
        result = await session.evaluate("""
            ({
                width: window.innerWidth,
                height: window.innerHeight,
                scrollX: window.scrollX,
                scrollY: window.scrollY,
            })
        """)
        
        window_info = result.get("result", {}).get("value", {})
        print(f"✅ 窗口信息:")
        print(f"   宽度: {window_info.get('width')}px")
        print(f"   高度: {window_info.get('height')}px")
        print(f"   滚动 X: {window_info.get('scrollX')}px")
        print(f"   滚动 Y: {window_info.get('scrollY')}px")


async def example8_error_handling():
    """示例 8: 错误处理"""
    print("\n" + "=" * 60)
    print("示例 8: 错误处理")
    print("=" * 60)
    
    # 尝试连接到不存在的端口
    config = CDPConnectionConfig(port=9999)
    connection = CDPConnection(config)
    
    try:
        await connection.connect()
    except ConnectionError as e:
        print(f"❌ 预期的错误: {e}")
        print("   这是正常的，因为端口 9999 没有运行浏览器")


async def run_all_examples():
    """运行所有示例"""
    print("\n" + "=" * 80)
    print(" " * 20 + "AeroTest CDP Session 使用示例")
    print("=" * 80)
    
    print("\n⚠️  运行前准备:")
    print("   1. 启动 Chrome 并开启远程调试:")
    print("      chrome.exe --remote-debugging-port=9222")
    print("   2. 或使用 Edge:")
    print("      msedge.exe --remote-debugging-port=9222")
    print("\n   按 Enter 继续...")
    # input()  # 取消注释以等待用户输入
    
    examples = [
        ("基础连接", example1_basic_connection),
        ("创建会话", example2_create_session),
        ("页面导航", example3_navigate),
        ("获取 DOM 树", example4_get_dom),
        ("DomService 集成", example5_dom_service_integration),
        ("截图", example6_screenshot),
        ("执行 JavaScript", example7_execute_javascript),
        ("错误处理", example8_error_handling),
    ]
    
    for i, (name, example_func) in enumerate(examples, 1):
        try:
            print(f"\n\n{'─' * 80}")
            print(f"运行示例 {i}/{len(examples)}: {name}")
            print(f"{'─' * 80}")
            await example_func()
            
        except Exception as e:
            logger.error(f"示例 {i} 运行失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 继续运行下一个示例
            print(f"\n⚠️ 跳过此示例，继续下一个...")
    
    print("\n\n" + "=" * 80)
    print(" " * 25 + "✅ 所有示例运行完成！")
    print("=" * 80 + "\n")


def main():
    """主函数"""
    try:
        asyncio.run(run_all_examples())
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except Exception as e:
        logger.error(f"运行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

