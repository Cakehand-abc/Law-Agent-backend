import logging
from app.schemas.contract import ContractChunk, RoutedChunk

try:
    import ahocorasick
except ImportError:
    # Fallback to pure python implementation or dummy
    ahocorasick = None
    logging.warning("pyahocorasick is not installed. Using dummy matching.")

class CostAwareGateway:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CostAwareGateway, cls).__new__(cls, *args, **kwargs)
            cls._instance.init_ac_automaton()
        return cls._instance
        
    def init_ac_automaton(self):
        """
        初始化 AC 自动机并注入核心高险关键词
        """
        high_risk_keywords = [
            "对赌", "回购", "一票否决", "反稀释", "优先清偿", 
            "排他", "独家", "竞业禁止", "限制竞争", "违约金", 
            "损害赔偿上限", "连带责任", "知识产权归属", "专利转让"
        ]
        
        if ahocorasick:
            self.A = ahocorasick.Automaton()
            for idx, key in enumerate(high_risk_keywords):
                self.A.add_word(key, (idx, key))
            self.A.make_automaton()
        else:
            self.high_risk_keywords = high_risk_keywords
            
    async def route_chunk(self, chunk: ContractChunk) -> RoutedChunk:
        """
        室友 B 负责实现的高性能分流路由算法
        """
        # 1. 语义缓存拦截 (Check Redis)
        # Mock logic
        
        # 2. AC 自动机多模式匹配
        has_high_risk_word = False
        content_to_scan = chunk.content_with_meta
        
        if ahocorasick:
            for end_index, (idx, keyword) in self.A.iter_search(content_to_scan):
                has_high_risk_word = True
                break
        else:
            for word in self.high_risk_keywords:
                if word in content_to_scan:
                    has_high_risk_word = True
                    break
                    
        # 3. 动态模型路由
        if has_high_risk_word:
            return RoutedChunk(
                chunk_id=chunk.chunk_id,
                content=chunk.content_with_meta,
                risk_tag="HIGH_RISK",
                target_model="deepseek-v4"
            )
        else:
            return RoutedChunk(
                chunk_id=chunk.chunk_id,
                content=chunk.content_with_meta,
                risk_tag="LOW_COST",
                target_model="qwen-2.5-7b-instruct"
            )
