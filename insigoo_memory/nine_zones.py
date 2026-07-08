"""
九大知识区定义 — 公益组织的知识结构
"""
from dataclasses import dataclass, field
from typing import List

@dataclass
class Zone:
    id: str
    name: str
    emoji: str
    description: str
    keywords: List[str] = field(default_factory=list)
    file_patterns: List[str] = field(default_factory=list)
    lint_rules: List[str] = field(default_factory=list)

ZONES = [
    Zone(
        id="industry",
        name="行业资讯",
        emoji="📰",
        description="政策速递、行业动向、资助机会、同行动态",
        keywords=["政策", "法规", "通知", "资助", "基金会", "招标", "行业报告", "新闻", "简报", "备忘录", "协议"],
        file_patterns=["*政策*", "*通知*", "*新闻*", "*简报*", "*资讯*", "*备忘录*", "*合作协议*", "*战略合作*", "*联合公告*", "*杂志*", "*征文*", "*媒体*", "*采访*"],
        lint_rules=["7天未读提醒", "同类资讯聚合"]
    ),
    Zone(
        id="research",
        name="研究学习",
        emoji="📚",
        description="行业报告、最佳实践、方法论、课程笔记",
        keywords=["研究", "报告", "评估", "方法论", "最佳实践", "案例", "文献", "论文", "学习", "课程"],
        file_patterns=["*研究*", "*论文*", "*课程*", "*学习*", "*文献*", "*方法论*", "*教程*", "*指南*", "*调查报告*", "*现状调查*"],
        lint_rules=["引用过时资料的提醒"]
    ),
    Zone(
        id="design",
        name="设计物料",
        emoji="🎨",
        description="海报模板、公众号素材、品牌手册、公益传播",
        keywords=["海报", "设计", "模板", "VI", "品牌", "公众号", "推文", "宣传", "易拉宝", "展板", "H5"],
        file_patterns=["*海报*", "*设计*", "*模板*", "*品牌*", "*VI*", "*.psd", "*.ai", "*.cdr"],
        lint_rules=["缺99公益日物料提醒", "品牌一致性检查"]
    ),
    Zone(
        id="project_plan",
        name="项目方案",
        emoji="📝",
        description="项目计划书、逻辑框架、预算模板、理论模型",
        keywords=["项目", "方案", "计划", "申请", "投标", "逻辑框架", "预算", "理论", "立项"],
        file_patterns=["*项目方案*", "*项目计划*", "*项目书*", "*申请书*", "*投标*", "*立项*", "*项目建议书*"],
        lint_rules=["相似项目推荐", "未启动项目提醒"]
    ),
    Zone(
        id="project_trace",
        name="项目痕迹",
        emoji="🏃",
        description="活动记录、照片归档、志愿者信息、受益人档案",
        keywords=["活动", "签到", "照片", "志愿者", "受益人", "参与者", "记录", "通讯录", "名单"],
        file_patterns=["*活动*", "*签到*", "*照片*", "*志愿者*", "*受益人*", "*名单*", "*.jpg", "*.png", "*通讯录*", "*议程*", "*参会*"],
        lint_rules=["照片与签到不一致", "活动频率异常", "志愿者流失预警"]
    ),
    Zone(
        id="finance",
        name="财务资料",
        emoji="💰",
        description="预算执行、捐赠明细、审计报告、报销单据",
        keywords=["财务", "预算", "审计", "报销", "发票", "捐赠", "支出", "收入", "年报", "税务"],
        file_patterns=["*财务*", "*预算*", "*审计*", "*报销*", "*发票*", "*年报*", "*票据*", "*记账*", "*决算*", "*签收*"],
        lint_rules=["预算执行率提醒", "单一资助方占比过高"]
    ),
    Zone(
        id="mne",
        name="监测评估",
        emoji="📊",
        description="指标定义、数据采集模板、评估报告、满意度调查",
        keywords=["监测", "评估", "指标", "数据", "统计", "满意度", "调查", "问卷", "基线", "终期"],
        file_patterns=["*监测*", "*评估报告*", "*评估*", "*指标*", "*数据*", "*问卷*", "*基线*", "*满意度*", "*KPI*"],
        lint_rules=["数据更新断档提醒", "指标达标预警", "数据采集周期提醒"]
    ),
    Zone(
        id="closure",
        name="结项资料",
        emoji="📦",
        description="结项报告、成果汇编、经验沉淀、对外传播稿",
        keywords=["结项", "总结", "成果", "复盘", "经验", "传播", "新闻稿", "感谢信"],
        file_patterns=["*结项*", "*总结*", "*成果*", "*复盘*", "*新闻稿*"],
        lint_rules=["项目到期未结项", "结项报告模板缺失"]
    ),
    Zone(
        id="admin",
        name="行政人事",
        emoji="🏢",
        description="章程、理事会纪要、员工手册、培训记录、年检材料",
        keywords=["章程", "理事会", "制度", "人事", "员工", "合同", "年检", "注册", "证件"],
        file_patterns=["*章程*", "*制度*", "*人事*", "*合同*", "*年检*", "*理事会*", "*手册*"],
        lint_rules=["年检到期提醒", "证件有效期检查"]
    ),
]
