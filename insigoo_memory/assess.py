"""
行业资讯检索 — 基于知识库生成每日资讯简报
"""
from pathlib import Path
from datetime import datetime


class NewsFetcher:
    """从本地知识库 + 行业知识包中提取最新资讯"""

    def daily_briefing(self, watch_dir: str, issues: list) -> str:
        """生成每日资讯简报"""
        research_dir = Path(watch_dir) / "研究学习"
        industry_dir = Path(watch_dir) / "行业资讯"

        briefing = []
        briefing.append(f"## 📰 行业资讯日报 · {datetime.now().strftime('%Y-%m-%d')}")
        briefing.append(f"关注议题: {', '.join(issues)}\n")

        # 行业知识包热点
        briefing.append("### 📋 行业知识要点")
        for issue in issues:
            pack_file = research_dir / f"{issue}.md"
            if not pack_file.exists():
                # Try fuzzy match
                for f in research_dir.glob("*.md"):
                    if issue in f.stem:
                        pack_file = f
                        break
            if pack_file.exists():
                content = pack_file.read_text(encoding="utf-8", errors="ignore")
                # 提取政策部分作为热点
                for line in content.split("\n"):
                    if line.startswith("- 《"):
                        briefing.append(f"  {line.strip()}")
                        break
                break

        if not any("《" in b for b in briefing):
            briefing.append("  暂无热点政策更新")

        # 行业资讯区最新动态
        briefing.append("\n### 📂 最近更新的行业文件")
        if industry_dir.exists():
            files = sorted(industry_dir.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)
            for f in files[:5]:
                if f.suffix in ('.md', '.txt'):
                    mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%m-%d %H:%M")
                    briefing.append(f"  - {f.name} ({mtime})")

        if not any(f.is_file() for f in list(industry_dir.glob("*")) if industry_dir.exists()):
            briefing.append("  （暂无文件。建议定期添加政策通知和资助信息）")

        # 热门关键词
        briefing.append("\n### 🔑 近期高频关键词")
        briefing.append("  提示：insigoo-memory reflect 可自动分析高频关键词")
        briefing.append("\n---")
        briefing.append("*由 insigoo-memory 自动生成*")

        return "\n".join(briefing)


class Diagnostician:
    """项目书诊断 — 基于 SIA L1 逻辑自洽评估框架"""

    def assess(self, project_text: str) -> dict:
        """对项目文本做 L1 逻辑自洽评估"""
        report = {
            "title": "项目书诊断报告",
            "timestamp": datetime.now().isoformat(),
            "principles": [],
            "findings": [],
            "score": {"pass": 0, "partial": 0, "fail": 0},
            "suggestions": []
        }

        # 检查7条原则（简化版 — 关键词检测）
        checks = [
            ("受益方中心", "是否明确列出受益群体？", ["受益", "服务对象", "目标群体", "受助"]),
            ("逻辑自洽", "目标→方法→行动是否完整？", ["目标", "方法", "行动", "步骤", "流程"]),
            ("证据为本", "是否有数据或案例支撑？", ["数据", "统计", "调查", "案例", "证据", "调研"]),
            ("适度量化", "是否有可衡量的指标？", ["指标", "%", "人数", "人次", "数量", "增长率"]),
            ("诚实归因", "是否区分贡献与归因？", ["贡献", "归因", "因果", "影响"]),
            ("透明可复现", "方法和假设是否公开说明？", ["方法", "假设", "前提", "说明"]),
            ("持续改进", "是否有复盘或改进机制？", ["复盘", "改进", "优化", "迭代", "反馈"]),
        ]

        for name, desc, keywords in checks:
            found = any(kw in project_text for kw in keywords)
            if found:
                report["principles"].append({"name": name, "status": "✅ 通过", "desc": desc})
                report["score"]["pass"] += 1
            else:
                report["principles"].append({"name": name, "status": "⚠ 缺失", "desc": desc})
                report["score"]["fail"] += 1
                report["suggestions"].append(f"建议补充{name}相关内容: {desc}")

        if report["score"]["pass"] >= 6:
            report["verdict"] = "✅ 项目书逻辑较完整，可以进入下一步评估"
        elif report["score"]["pass"] >= 4:
            report["verdict"] = "🟡 项目书基本可行，但存在明显缺口，建议补充后重新评估"
        else:
            report["verdict"] = "🔴 项目书存在较多缺失，建议重新梳理逻辑框架后再评估"

        return report
