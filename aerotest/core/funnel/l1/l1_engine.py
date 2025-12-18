"""L1 引擎

L1 层的主引擎，整合所�?L1 组件
"""

from typing import Optional

from aerotest.browser.dom.views import SerializedDOMState
from aerotest.core.funnel.base import BaseFunnelLayer
from aerotest.core.funnel.l1.intent_recognizer import IntentRecognizer
from aerotest.core.funnel.l1.entity_extractor import EntityExtractor
from aerotest.core.funnel.l1.slot_filler import SlotFiller
from aerotest.core.funnel.l1.synonym_mapper import SynonymMapper
from aerotest.core.funnel.types import ActionSlot, FunnelContext


class L1Engine(BaseFunnelLayer):
    """L1 规则槽位引擎
    
    从自然语言指令中提取结构化的操作信�?
    
    完整的处理流程：
    1. 使用 SlotFiller 填充基础槽位（内部调�?IntentRecognizer �?EntityExtractor�?
    2. 使用 SynonymMapper 扩展关键�?
    3. 返回完整�?ActionSlot
    
    Example:
        ```python
        engine = L1Engine()
        
        # 异步处理
        context = FunnelContext(instruction="点击提交按钮")
        context = await engine.process(context)
        slot = context.action_slot
        
        # 同步提取
        slot = engine.extract_slot("点击提交按钮")
        ```
    """
    
    def __init__(
        self,
        enable_synonym_expansion: bool = True,
        max_synonyms: int = 10,
    ):
        """
        初始�?L1 引擎
        
        Args:
            enable_synonym_expansion: 是否启用同义词扩�?
            max_synonyms: 每个关键词最多扩展的同义词数�?
        """
        super().__init__("L1")
        
        # 初始化各个组�?
        self.intent_recognizer = IntentRecognizer()
        self.entity_extractor = EntityExtractor()
        self.slot_filler = SlotFiller()
        self.synonym_mapper = SynonymMapper(max_synonyms=max_synonyms)
        
        self.enable_synonym_expansion = enable_synonym_expansion
        
        self.logger.info(
            f"L1 引擎初始化完�?(同义词扩�? {enable_synonym_expansion})"
        )
    
    async def process(
        self,
        context: FunnelContext,
        dom_state: Optional[SerializedDOMState] = None,
    ) -> FunnelContext:
        """
        处理自然语言指令，提取槽位信�?
        
        Args:
            context: 漏斗上下�?
            dom_state: DOM 状态（L1 不需要）
            
        Returns:
            更新后的上下文（包含 action_slot�?
        """
        self.log_start()
        
        instruction = context.instruction
        
        # 1. 使用 SlotFiller 填充槽位（内部整合了 IntentRecognizer �?EntityExtractor�?
        slot = self.slot_filler.fill(instruction)
        
        # 2. 同义词扩展（如果启用�?
        if self.enable_synonym_expansion and slot.keywords:
            expanded_keywords = self.synonym_mapper.get_all_synonyms(slot.keywords)
            slot.keywords = expanded_keywords
            
            self.logger.debug(
                f"关键词扩�? {len(slot.keywords)} 个关键词"
            )
        
        # 3. 更新上下�?
        context.action_slot = slot
        
        # 4. 记录详细信息
        self.logger.info(
            f"L1 处理完成: action={slot.action.value}, "
            f"type={slot.target_type.value if slot.target_type else 'None'}, "
            f"keywords={len(slot.keywords)}, "
            f"confidence={slot.confidence:.2f}"
        )
        
        self.log_end()
        return context
    
    def extract_slot(self, instruction: str) -> ActionSlot:
        """
        提取槽位信息（同步版本，用于外部调用�?
        
        Args:
            instruction: 自然语言指令
            
        Returns:
            动作槽位
        """
        # 使用 SlotFiller 填充槽位
        slot = self.slot_filler.fill(instruction)
        
        # 同义词扩�?
        if self.enable_synonym_expansion and slot.keywords:
            expanded_keywords = self.synonym_mapper.get_all_synonyms(slot.keywords)
            slot.keywords = expanded_keywords
        
        return slot
    
    def extract_batch(self, instructions: list[str]) -> list[ActionSlot]:
        """
        批量提取槽位
        
        Args:
            instructions: 指令列表
            
        Returns:
            槽位列表
        """
        return [self.extract_slot(instruction) for instruction in instructions]
    
    def validate_slot(self, slot: ActionSlot) -> bool:
        """
        验证槽位是否有效
        
        Args:
            slot: 动作槽位
            
        Returns:
            是否有效
        """
        # 基本验证
        if not slot:
            return False
        
        # 置信度阈�?
        if slot.confidence < 0.3:
            self.logger.warning(f"槽位置信度过�? {slot.confidence:.2f}")
            return False
        
        # 必须有关键词
        if not slot.keywords:
            self.logger.warning("槽位缺少关键�?)
            return False
        
        return True

