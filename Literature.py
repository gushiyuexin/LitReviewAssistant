import numpy as np

class Literature:
    def __init__(self, num, title, abstract, journal, publication_year, citation_count, DOI=None):
        self.num = num
        self.title = title
        self.abstract = abstract
        self.journal = journal
        self.journal_IF = 0
        self.publication_year = publication_year
        self.citation_count = citation_count
        self.LLM_extract_Info = {}
        self.DOI = DOI
        self.PaperImpact = 0

    def InfoPrint(self, current_year, debug_count, TitleList, InfoCount):
        print(debug_count)
        PrintStr = str(InfoCount) + ","
        PrintStr += self.title + ","
        for name in TitleList:
            PrintStr += self.LLM_extract_Info_Display(name) + ","
        PrintStr += self.journal + ","
        PrintStr += str(self.publication_year) + ","
        PrintStr += str(self.PaperImpactCal(current_year)) + ","
        PrintStr += str(self.DOI) + ","
        PrintStr += str(self.abstract.replace(",", "，")) + ","
        return PrintStr + "\n"

    def LLM_extract_Info_Display(self, InfoName):
        if type(self.LLM_extract_Info[InfoName]) == type([]):
            return "+".join(self.LLM_extract_Info[InfoName])
        else:
            return self.LLM_extract_Info[InfoName]

    def PaperImpactCal(self, current_year):
        # 论文影响力计算函数
        """
        years = max(current_year - int(self.publication_year), 1)
        PI = int(self.journal_IF)/2/years + np.log(int(self.citation_count) + 1) / years
        return PI
        """
        # 论文已发表年数
        years = max(current_year - int(self.publication_year), 1)
        # 期刊影响因子权重 (假设为 0.5，可调整)
        W_IF = 0.5
        # 引用次数权重 (假设为 0.5，可调整)
        W_C = 0.5
        # 引用速度：总引用次数 / 论文发表年数
        citation_rate = int(self.citation_count) / years

        # 时间衰减模型：这里采用指数衰减模型，可根据需求修改
        def time_decay(t, k=0.1):
            return 1 / (1 + np.exp(k * (t - 5)))  # t 为论文发表的年数，k 为衰减速率

        # 期刊影响因子的部分
        impact_factor_contribution = W_IF * (self.journal_IF / years)
        # 引用次数部分，考虑时间衰减的引用速度
        citation_contribution = W_C * np.log(1 + citation_rate) * time_decay(years)
        # 综合影响力得分 (PI)
        PI = impact_factor_contribution + citation_contribution
        # 返回最终的论文影响力
        return PI


