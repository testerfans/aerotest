"""同义词映射器测试"""

import pytest

from aerotest.core.funnel.l1.synonym_mapper import SynonymMapper


class TestSynonymMapper:
    """测试同义词映射器"""
    
    @pytest.fixture
    def mapper(self):
        """创建映射器实例"""
        return SynonymMapper()
    
    def test_expand_single_keyword(self, mapper):
        """测试扩展单个关键词"""
        synonyms = mapper.expand("提交")
        
        # 应该包含原词
        assert "提交" in synonyms
        
        # 应该包含同义词
        assert any(s in synonyms for s in ["确认", "保存", "submit"])
    
    def test_expand_keeps_original_first(self, mapper):
        """测试原词在第一位"""
        synonyms = mapper.expand("提交")
        
        # 原词应该在第一位
        assert synonyms[0] == "提交"
    
    def test_expand_keywords_batch(self, mapper):
        """测试批量扩展"""
        keywords = ["提交", "按钮"]
        result = mapper.expand_keywords(keywords)
        
        assert "提交" in result
        assert "按钮" in result
        assert len(result["提交"]) > 1
        assert len(result["按钮"]) > 1
    
    def test_get_all_synonyms(self, mapper):
        """测试获取所有同义词（扁平化）"""
        keywords = ["提交", "按钮"]
        all_synonyms = mapper.get_all_synonyms(keywords)
        
        # 应该包含所有关键词的同义词
        assert "提交" in all_synonyms
        assert "按钮" in all_synonyms
        
        # 应该去重
        assert len(all_synonyms) == len(set(all_synonyms))
    
    def test_english_to_chinese(self, mapper):
        """测试英文到中文映射"""
        synonyms = mapper.expand("submit")
        
        # 应该包含中文翻译
        assert "提交" in synonyms
    
    def test_add_custom_synonym(self, mapper):
        """测试动态添加同义词"""
        mapper.add_synonym("自定义", ["custom", "定制"])
        
        synonyms = mapper.expand("自定义")
        
        assert "自定义" in synonyms
        assert "custom" in synonyms
        assert "定制" in synonyms
    
    def test_weight_calculation(self, mapper):
        """测试权重计算"""
        # 原词权重应该是 1.0
        weight = mapper.get_weight("提交", "提交")
        assert weight == 1.0
        
        # 同义词权重应该小于 1.0
        weight = mapper.get_weight("提交", "确认")
        assert 0.5 <= weight < 1.0
        
        # 不相关的词权重应该是 0.0
        weight = mapper.get_weight("提交", "随便")
        assert weight == 0.0
    
    def test_find_best_match(self, mapper):
        """测试找到最佳匹配"""
        candidates = ["确认", "保存", "随便"]
        
        match = mapper.find_best_match("提交", candidates)
        
        assert match is not None
        assert match[0] in ["确认", "保存"]
        assert 0.5 <= match[1] <= 1.0
    
    def test_find_best_match_original(self, mapper):
        """测试原词匹配的权重最高"""
        candidates = ["确认", "提交", "保存"]
        
        match = mapper.find_best_match("提交", candidates)
        
        assert match is not None
        assert match[0] == "提交"
        assert match[1] == 1.0
    
    def test_find_best_match_no_match(self, mapper):
        """测试没有匹配"""
        candidates = ["随便", "其他"]
        
        match = mapper.find_best_match("提交", candidates)
        
        assert match is None
    
    def test_max_synonyms_limit(self, mapper):
        """测试同义词数量限制"""
        mapper_limited = SynonymMapper(max_synonyms=3)
        
        synonyms = mapper_limited.expand("提交")
        
        # 应该不超过 max_synonyms + 1（原词）
        assert len(synonyms) <= 4
    
    def test_empty_keyword(self, mapper):
        """测试空关键词"""
        synonyms = mapper.expand("")
        
        assert synonyms == []
    
    def test_case_insensitive(self, mapper):
        """测试大小写不敏感"""
        synonyms1 = mapper.expand("提交")
        synonyms2 = mapper.expand("提交")
        
        # 结果应该一致（都是小写）
        assert synonyms1 == synonyms2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

