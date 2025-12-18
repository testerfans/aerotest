"""L1 引擎使用示例

演示如何使用 L1 规则槽位引擎提取自然语言指令的结构化信息
"""

import asyncio

from aerotest.core.funnel.l1.l1_engine import L1Engine
from aerotest.core.funnel.types import FunnelContext


async def basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("示例 1: 基础使用")
    print("=" * 60)
    
    # 创建 L1 引擎
    engine = L1Engine()
    
    # 测试指令
    instructions = [
        "点击提交按钮",
        "输入用户名",
        "选择下拉框",
        "在密码输入框输入 123456",
    ]
    
    for instruction in instructions:
        # 同步提取槽位
        slot = engine.extract_slot(instruction)
        
        print(f"\n指令: {instruction}")
        print(f"  动作: {slot.action.value}")
        print(f"  目标: {slot.target}")
        print(f"  类型: {slot.target_type.value if slot.target_type else 'None'}")
        print(f"  关键词: {slot.keywords[:5]}...")  # 只显示前 5 个
        print(f"  属性: {slot.attributes}")
        print(f"  值: {slot.value}")
        print(f"  置信度: {slot.confidence:.2f}")


async def async_usage():
    """异步使用示例"""
    print("\n" + "=" * 60)
    print("示例 2: 异步使用")
    print("=" * 60)
    
    engine = L1Engine()
    
    # 创建上下文
    context = FunnelContext(instruction="点击提交按钮")
    
    # 异步处理
    context = await engine.process(context)
    
    # 获取槽位
    slot = context.action_slot
    
    print(f"\n指令: {context.instruction}")
    print(f"槽位信息:")
    print(f"  动作: {slot.action.value}")
    print(f"  目标: {slot.target}")
    print(f"  类型: {slot.target_type.value if slot.target_type else 'None'}")
    print(f"  关键词数: {len(slot.keywords)}")
    print(f"  置信度: {slot.confidence:.2f}")


def synonym_expansion_demo():
    """同义词扩展演示"""
    print("\n" + "=" * 60)
    print("示例 3: 同义词扩展")
    print("=" * 60)
    
    # 启用同义词扩展
    engine_with_syn = L1Engine(enable_synonym_expansion=True)
    slot_with = engine_with_syn.extract_slot("点击提交按钮")
    
    # 禁用同义词扩展
    engine_without_syn = L1Engine(enable_synonym_expansion=False)
    slot_without = engine_without_syn.extract_slot("点击提交按钮")
    
    print(f"\n启用同义词扩展:")
    print(f"  关键词数: {len(slot_with.keywords)}")
    print(f"  关键词: {slot_with.keywords}")
    
    print(f"\n禁用同义词扩展:")
    print(f"  关键词数: {len(slot_without.keywords)}")
    print(f"  关键词: {slot_without.keywords}")


def batch_extraction():
    """批量提取示例"""
    print("\n" + "=" * 60)
    print("示例 4: 批量提取")
    print("=" * 60)
    
    engine = L1Engine()
    
    instructions = [
        "点击登录按钮",
        "输入邮箱",
        "勾选同意协议复选框",
        "选择国家下拉框",
        "在搜索框输入 AeroTest",
    ]
    
    # 批量提取
    slots = engine.extract_batch(instructions)
    
    print(f"\n批量处理 {len(instructions)} 条指令:\n")
    
    for i, (instruction, slot) in enumerate(zip(instructions, slots), 1):
        print(f"{i}. {instruction}")
        print(f"   -> 动作: {slot.action.value}, "
              f"类型: {slot.target_type.value if slot.target_type else 'None'}, "
              f"置信度: {slot.confidence:.2f}")


def validation_demo():
    """槽位验证示例"""
    print("\n" + "=" * 60)
    print("示例 5: 槽位验证")
    print("=" * 60)
    
    engine = L1Engine()
    
    instructions = [
        "点击提交按钮",          # 有效
        "随便看看",              # 低置信度
        "做一些操作",            # 模糊
    ]
    
    print()
    for instruction in instructions:
        slot = engine.extract_slot(instruction)
        is_valid = engine.validate_slot(slot)
        
        print(f"指令: {instruction}")
        print(f"  置信度: {slot.confidence:.2f}")
        print(f"  验证结果: {'✅ 有效' if is_valid else '❌ 无效'}")
        print()


def attribute_inference_demo():
    """属性推断示例"""
    print("\n" + "=" * 60)
    print("示例 6: 属性推断")
    print("=" * 60)
    
    engine = L1Engine(enable_synonym_expansion=False)  # 禁用同义词，方便查看
    
    test_cases = [
        ("点击提交按钮", "提交按钮会推断 type=submit"),
        ("输入密码", "密码输入框会推断 type=password"),
        ("填写邮箱", "邮箱输入框会推断 type=email"),
        ("搜索商品", "搜索相关会推断 role=search"),
    ]
    
    print()
    for instruction, description in test_cases:
        slot = engine.extract_slot(instruction)
        
        print(f"指令: {instruction}")
        print(f"  说明: {description}")
        print(f"  推断属性: {slot.attributes}")
        print()


async def main():
    """运行所有示例"""
    print("\n" + "🎯" * 30)
    print(" L1 规则槽位引擎 - 使用示例")
    print("🎯" * 30)
    
    # 运行示例
    await basic_usage()
    await async_usage()
    synonym_expansion_demo()
    batch_extraction()
    validation_demo()
    attribute_inference_demo()
    
    print("\n" + "=" * 60)
    print("✅ 所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

