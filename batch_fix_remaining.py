#!/usr/bin/env python3
"""批量修复剩余文件的编码问题"""

import subprocess
from pathlib import Path

# 需要修复的文件列表
FILES_TO_FIX = [
    'core/ooda/ooda_engine.py',
    'core/ooda/types.py',
    'browser/cdp/connection.py',
    'browser/cdp/session.py',
    'browser/cdp/types.py',
    'browser/dom/cdp_types.py',
    'browser/dom/dom_service.py',
    'browser/dom/enhanced_snapshot.py',
    'browser/dom/event_listener_detector.py',
    'browser/dom/paint_order.py',
    'browser/dom/serializer.py',
    'browser/dom/views.py',
    'core/funnel/l1/slot_filler.py',
    'core/funnel/l1_rule.py',
    'core/funnel/l2/attribute_matcher.py',
    'core/funnel/l2/scorer.py',
    'core/funnel/l2/type_matcher.py',
    'core/funnel/l3/anchor_locator.py',
    'core/funnel/l3/proximity_detector.py',
    'core/funnel/l3/types.py',
    'core/funnel/l4/context_extractor.py',
    'core/funnel/l4/prompt_builder.py',
    'core/funnel/l4/qwen_client.py',
    'core/funnel/l5/screenshot_service.py',
    'db/__init__.py',
    'db/migrations/env.py',
    'db/models/__init__.py',
]

# 编码映射
REPLACEMENTS = [
    ('�?', '的'),
    ('�?', '器'),
    ('信�?', '信息'),
    ('配�?', '配置'),
    ('初始�?', '初始化'),
    ('完�?', '完成'),
    ('�?', '个'),
    ('状�?', '状态'),
    ('�?', '在'),
    ('漏�?', '漏斗'),
    ('步�?', '步骤'),
    ('上下�?', '上下文'),
    ('策�?', '策略'),
    ('置信�?', '置信度'),
    ('�?', '类'),
    ('�?', '层'),
    ('引�?', '引擎'),
    ('元�?', '元素'),
    ('结�?', '结果'),
    ('验�?', '验证'),
    ('候�?', '候选'),
    ('列�?', '列表'),
    ('属�?', '属性'),
    ('匹�?', '匹配'),
    ('执�?', '执行'),
    ('记录�?', '记录器'),
    ('服�?', '服务'),
    ('�?', '为'),
    ('测�?', '测试'),
    ('包�?', '包含'),
    ('�?', '构'),
    ('组�?', '组件'),
    ('�?', '以'),
    ('�?', '框'),
    ('�?', '树'),
    ('序列�?', '序列化'),
    ('�?', '号'),
    ('返�?', '返回'),
    ('�?', '中'),
    ('节�?', '节点'),
    ('选择�?', '选择器'),
    ('标签�?', '标签名'),
    ('�?', '建'),
    ('�?', '据'),
    ('�?', '时'),
    ('�?', '间'),
    ('�?', '型'),
    ('�?', '连接'),
    ('会�?', '会话'),
    ('协�?', '协议'),
    ('�?', '传递'),
    ('�?', '过'),
    ('跳�?', '跳过'),
    ('�?', '分'),
    ('�?', '析'),
]

def main():
    base_dir = Path(__file__).parent
    aerotest_dir = base_dir / 'aerotest'
    
    fixed_count = 0
    
    for file_path in FILES_TO_FIX:
        full_path = aerotest_dir / file_path
        print(f"修复: {file_path}")
        
        try:
            # 使用git获取原始内容
            result = subprocess.run(
                ['git', 'show', f'HEAD:aerotest/{file_path}'],
                cwd=base_dir,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                print(f"  ❌ 无法获取原始内容: {result.stderr}")
                continue
            
            content = result.stdout
            
            # 应用所有替换
            for old, new in REPLACEMENTS:
                content = content.replace(old, new)
            
            # 写入文件
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            
            print(f"  ✅ 完成")
            fixed_count += 1
            
        except Exception as e:
            print(f"  ❌ 错误: {e}")
    
    print(f"\n✅ 总共修复 {fixed_count}/{len(FILES_TO_FIX)} 个文件")

if __name__ == '__main__':
    main()
