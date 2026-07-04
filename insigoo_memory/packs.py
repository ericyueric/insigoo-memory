"""
行业知识包安装器 — 根据用户选择的议题安装对应知识包
"""
import os, shutil
from pathlib import Path
from .nine_zones import ZONES

# 议题 → 知识包文件映射
ISSUE_PACKS = {
    "教育": "education.md", "助学": "education.md",
    "医疗": "healthcare.md", "卫生": "healthcare.md", "健康": "healthcare.md",
    "环保": "environment.md", "环境": "environment.md", "生态": "environment.md",
    "儿童": "children.md", "少儿": "children.md",
    "养老": "elderly.md", "老年": "elderly.md", "老龄": "elderly.md",
    "残障": "disability.md", "残疾": "disability.md", "无障碍": "disability.md",
    "社区": "community.md", "治理": "community.md",
    "救灾": "emergency.md", "应急": "emergency.md", "防灾": "emergency.md",
    "妇女": "women.md", "女性": "women.md",
    "文化": "culture.md", "非遗": "culture.md",
    "乡村": "rural.md", "扶贫": "rural.md", "振兴": "rural.md",
    "志愿": "volunteer.md", "公益": "volunteer.md",
}

PACKS_DIR = Path(__file__).parent / "knowledge_packs"


def install_packs(issues: list, target_dir: str):
    """根据用户选择的议题，安装对应知识包到目标目录"""
    research_dir = Path(target_dir) / "研究学习"
    research_dir.mkdir(parents=True, exist_ok=True)

    installed = []
    seen = set()

    for issue in issues:
        # 模糊匹配
        for key, pack_file in ISSUE_PACKS.items():
            if key in issue and key not in seen:
                src = PACKS_DIR / pack_file
                if src.exists():
                    dst = research_dir / pack_file
                    shutil.copy(src, dst)
                    installed.append(f"{pack_file} ({key})")
                    seen.add(key)
                    break

    return installed
