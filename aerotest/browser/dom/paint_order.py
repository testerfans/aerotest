"""绘制顺序移除�?

用于计算哪些元素应该根据绘制顺序参数被移�?

来源: browser-use v0.11.2
"""

from collections import defaultdict
from dataclasses import dataclass

from aerotest.browser.dom.views import SimplifiedNode


@dataclass(frozen=True, slots=True)
class Rect:
    """封闭轴对齐矩形，(x1,y1) 为左下角�?x2,y2) 为右上角"""
    x1: float
    y1: float
    x2: float
    y2: float

    def __post_init__(self) -> None:
        """验证矩形有效�?""
        if not (self.x1 <= self.x2 and self.y1 <= self.y2):
            pass  # 静默忽略无效矩形

    def area(self) -> float:
        """计算矩形面积"""
        return (self.x2 - self.x1) * (self.y2 - self.y1)

    def intersects(self, other: 'Rect') -> bool:
        """检查是否与另一个矩形相�?""
        return not (
            self.x2 <= other.x1 or 
            other.x2 <= self.x1 or 
            self.y2 <= other.y1 or 
            other.y2 <= self.y1
        )

    def contains(self, other: 'Rect') -> bool:
        """检查是否包含另一个矩�?""
        return (
            self.x1 <= other.x1 and 
            self.y1 <= other.y1 and 
            self.x2 >= other.x2 and 
            self.y2 >= other.y2
        )


class RectUnionPure:
    """
    维护不相交的矩形集合
    无外部依�?- 适用于几千个矩形
    """

    __slots__ = ('_rects',)

    def __init__(self) -> None:
        self._rects: list[Rect] = []

    def _split_diff(self, a: Rect, b: Rect) -> list[Rect]:
        """
        返回最�?4 个矩形的列表 = a \ b
        假设 a �?b 相交
        """
        parts = []

        # 底部切片
        if a.y1 < b.y1:
            parts.append(Rect(a.x1, a.y1, a.x2, b.y1))
        
        # 顶部切片
        if b.y2 < a.y2:
            parts.append(Rect(a.x1, b.y2, a.x2, a.y2))

        # 中间（垂直）条：y 重叠�?[max(a.y1,b.y1), min(a.y2,b.y2)]
        y_lo = max(a.y1, b.y1)
        y_hi = min(a.y2, b.y2)

        # 左切�?
        if a.x1 < b.x1:
            parts.append(Rect(a.x1, y_lo, b.x1, y_hi))
        
        # 右切�?
        if b.x2 < a.x2:
            parts.append(Rect(b.x2, y_lo, a.x2, y_hi))

        return parts

    def contains(self, r: Rect) -> bool:
        """
        如果 r 完全被当前并集覆盖则返回 True
        """
        if not self._rects:
            return False

        stack = [r]
        for s in self._rects:
            new_stack = []
            for piece in stack:
                if s.contains(piece):
                    # piece 完全消失
                    continue
                if piece.intersects(s):
                    new_stack.extend(self._split_diff(piece, s))
                else:
                    new_stack.append(piece)
            if not new_stack:  # 全部被吃�?- 被覆�?
                return True
            stack = new_stack
        return False  # 有东西幸�?

    def add(self, r: Rect) -> bool:
        """
        插入 r，除非它已经被覆�?
        如果并集增长则返�?True
        """
        if self.contains(r):
            return False

        pending = [r]
        i = 0
        while i < len(self._rects):
            s = self._rects[i]
            new_pending = []
            changed = False
            for piece in pending:
                if piece.intersects(s):
                    new_pending.extend(self._split_diff(piece, s))
                    changed = True
                else:
                    new_pending.append(piece)
            pending = new_pending
            if changed:
                # s 未改变；继续下一个现有矩�?
                i += 1
            else:
                i += 1

        # 任何剩余的片段都是新的、不重叠的区�?
        self._rects.extend(pending)
        return True


class PaintOrderRemover:
    """
    根据绘制顺序参数计算应该移除的元�?
    """

    def __init__(self, root: SimplifiedNode):
        self.root = root

    def calculate_paint_order(self) -> None:
        """计算绘制顺序并标记应该被忽略的元�?""
        all_simplified_nodes_with_paint_order: list[SimplifiedNode] = []

        def collect_paint_order(node: SimplifiedNode) -> None:
            """递归收集具有绘制顺序的节�?""
            if (
                node.original_node.snapshot_node
                and node.original_node.snapshot_node.paint_order is not None
                and node.original_node.snapshot_node.bounds is not None
            ):
                all_simplified_nodes_with_paint_order.append(node)

            for child in node.children:
                collect_paint_order(child)

        collect_paint_order(self.root)

        # 按绘制顺序分�?
        grouped_by_paint_order: defaultdict[int, list[SimplifiedNode]] = defaultdict(list)

        for node in all_simplified_nodes_with_paint_order:
            if (
                node.original_node.snapshot_node 
                and node.original_node.snapshot_node.paint_order is not None
            ):
                grouped_by_paint_order[node.original_node.snapshot_node.paint_order].append(node)

        rect_union = RectUnionPure()

        # 从高到低处理绘制顺序
        for paint_order, nodes in sorted(grouped_by_paint_order.items(), key=lambda x: -x[0]):
            rects_to_add = []

            for node in nodes:
                if not node.original_node.snapshot_node or not node.original_node.snapshot_node.bounds:
                    continue

                rect = Rect(
                    x1=node.original_node.snapshot_node.bounds.x,
                    y1=node.original_node.snapshot_node.bounds.y,
                    x2=node.original_node.snapshot_node.bounds.x + node.original_node.snapshot_node.bounds.width,
                    y2=node.original_node.snapshot_node.bounds.y + node.original_node.snapshot_node.bounds.height,
                )

                if rect_union.contains(rect):
                    node.ignored_by_paint_order = True

                # 如果不透明度小�?0.8 或背景色透明，则不添加节�?
                if node.original_node.snapshot_node.computed_styles:
                    bg_color = node.original_node.snapshot_node.computed_styles.get(
                        'background-color', 'rgba(0, 0, 0, 0)'
                    )
                    opacity = float(node.original_node.snapshot_node.computed_styles.get('opacity', '1'))
                    
                    if bg_color == 'rgba(0, 0, 0, 0)' or opacity < 0.8:
                        continue

                rects_to_add.append(rect)

            for rect in rects_to_add:
                rect_union.add(rect)

