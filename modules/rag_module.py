class RAGModule:
    def __init__(self, use_embeddings=False):
        self.use_embeddings = use_embeddings
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Load industry knowledge from markdown files"""
        import os
        knowledge = {}
        kb_path = "data/industry_knowledge"

        for industry in ['retail', 'healthcare', 'ecommerce', 'aviation']:
            file_path = os.path.join(kb_path, f"{industry}.md")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    knowledge[industry] = f.read()
            except:
                knowledge[industry] = ""

        return knowledge

    def search(self, query, industry):
        """Search relevant knowledge"""
        if self.use_embeddings:
            return self._faiss_search(query, industry)
        else:
            return self._keyword_search(query, industry)

    def _keyword_search(self, query, industry):
        """Simple keyword-based search"""
        if industry not in self.knowledge_base:
            return "暂无该行业的知识库内容"

        content = self.knowledge_base[industry]

        # Extract relevant sections based on keywords
        keywords = query.lower().split()
        lines = content.split('\n')

        relevant_sections = []
        for i, line in enumerate(lines):
            if any(kw in line.lower() for kw in keywords):
                # Get context (3 lines before and after)
                start = max(0, i-3)
                end = min(len(lines), i+4)
                relevant_sections.append('\n'.join(lines[start:end]))

        if relevant_sections:
            return '\n\n'.join(relevant_sections[:2])  # Return top 2 matches
        else:
            # Return industry overview if no specific match
            return '\n'.join(lines[:20])

    def _faiss_search(self, query, industry):
        """FAISS-based semantic search (for future API upgrade)"""
        # Placeholder for future implementation
        return self._keyword_search(query, industry)

    def get_industry_overview(self, industry):
        """Get full industry knowledge"""
        if industry in self.knowledge_base and self.knowledge_base[industry]:
            return self.knowledge_base[industry]

        # Fallback to built-in knowledge if files not found
        fallback = {
            'retail': """### 🛒 零售行业需求预测

零售行业需求受多种因素影响，包括季节性、促销活动、节假日效应和消费者行为变化。

**关键特征：**
- 强烈的季节性波动（春节、双十一、618等）
- 促销活动带来的短期需求峰值
- 长期趋势受宏观经济影响

**预测建议：**
- 建议使用至少2年历史数据以捕捉季节性
- 将促销日历作为外部变量纳入模型""",
            'healthcare': """### 🏥 医疗行业需求预测

医疗需求预测对资源配置、人员排班和药品库存管理至关重要。

**关键特征：**
- 季节性疾病模式（流感季、过敏季）
- 人口老龄化带来的长期增长趋势
- 突发公共卫生事件的不确定性

**预测建议：**
- 结合历史就诊数据和流行病学数据
- 考虑节假日对就诊量的影响""",
            'ecommerce': """### 📦 电商行业需求预测

电商需求预测需要处理高频数据、大促活动和用户行为的快速变化。

**关键特征：**
- 大促活动（双十一、618）带来极端峰值
- 用户增长和留存对需求的长期影响
- 品类和SKU级别的细粒度预测需求

**预测建议：**
- 区分大促期间和日常期间分别建模
- 利用用户行为数据作为领先指标""",
            'aviation': """### ✈️ 航空行业需求预测

航空需求预测对航班排班、机组资源和收益管理具有重要意义。

**关键特征：**
- 明显的旅游旺季和商务出行规律
- 节假日和寒暑假的需求高峰
- 宏观经济和突发事件的敏感性

**预测建议：**
- 结合历史预订数据和实际出行数据
- 建立航线级别的精细化预测模型"""
        }
        return fallback.get(industry, "暂无该行业的知识库内容")
