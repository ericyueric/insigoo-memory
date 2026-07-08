"""
文件自动分类器 — 把文件丢进去，自动判断属于哪个知识区
v0.3.2: 快速模式 — 文件名/目录名命中即返回，不读内容
"""
import os
from pathlib import Path
from .nine_zones import ZONES, Zone


class FileClassifier:
    """两步判定法：文件名/目录名 → 内容关键词（仅在必要时读文件）"""

    def classify(self, filepath: str) -> tuple:
        path = Path(filepath)
        filename = path.name.lower()
        dirname = path.parent.name.lower() if path.parent.name else ""

        scores = {}

        for zone in ZONES:
            score = 0

            # 第1步：文件名模式匹配（权重 60%）
            for pattern in zone.file_patterns:
                if self._glob_match(filename, pattern):
                    score += 60
                    break

            # 第2步：目录名匹配（权重 40%）
            for kw in zone.keywords:
                if kw.lower() in dirname:
                    score += 40
                    break

            scores[zone.id] = min(score, 100)

        # 文件名强信号
        finance_names = {'预算', '报销', '决算', '票据', '记账', '签收', '餐费', '租车', '交通费', '文具', '办公用品', '发票'}
        if any(k in filename for k in finance_names):
            scores['finance'] = 95

        trace_names = {'签到', '活动照片', '志愿者', '名单', '通讯录', '议程', '参会', '记录'}
        if any(k in filename for k in trace_names):
            scores['project_trace'] = 95

        if any(k in filename for k in {'项目书', '申请书', '投标', '立项', '建议书', '方案'}):
            scores['project_plan'] = 95

        if any(k in filename for k in {'结项', '总结报告', '成果汇编', '复盘'}):
            scores['closure'] = 95

        if any(k in filename for k in {'监测', '评估报告', '指标', '问卷', '基线', '满意度'}):
            scores['mne'] = 95

        best = max(scores, key=scores.get)
        best_score = scores[best]

        # 只有低置信度（<50）时才读文件内容
        if best_score < 50:
            content = ""
            if path.suffix.lower() in ('.md', '.txt', '.csv', '.json', '.html'):
                try:
                    content = path.read_text(encoding='utf-8', errors='ignore')[:1000]
                except:
                    pass

            if content:
                for zone in ZONES:
                    kw_hits = sum(1 for kw in zone.keywords if kw in content)
                    scores[zone.id] = min(scores.get(zone.id, 0) + kw_hits * 5, 100)

                if '姓名' in content and '签到' in content:
                    scores['project_trace'] = 95
                if '合作期限' in content and ('备忘录' in content or '协议' in content):
                    scores['industry'] = 90
                if '问卷' in content and '调查' in content:
                    scores['research'] = 85

            best = max(scores, key=scores.get)
            best_score = scores[best]

        if best_score < 20:
            return Zone(id="uncategorized", name="未分类", emoji="❓", description="需要人工确认", keywords=[]), 0

        return next(z for z in ZONES if z.id == best), best_score

    def _glob_match(self, filename: str, pattern: str) -> bool:
        return pattern.lower().replace('*', '') in filename

    def batch_classify(self, root_dir: str, max_mb: int = None,
                       skip_dirs: set = None) -> dict:
        results = {z.id: [] for z in ZONES}
        results['uncategorized'] = []
        skip_dirs = skip_dirs or set()
        cnt = 0

        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs
                       if not d.startswith('.') and d not in skip_dirs]
            for f in files:
                fp = os.path.join(root, f)
                cnt += 1
                if cnt % 500 == 0:
                    print(f"  ... {cnt} 个文件已扫描", flush=True)

                if max_mb:
                    try:
                        if os.path.getsize(fp) > max_mb * 1024 * 1024:
                            continue
                    except:
                        pass

                zone, score = self.classify(fp)
                results[zone.id].append({
                    'path': fp, 'name': f,
                    'zone': zone.name, 'emoji': zone.emoji,
                    'confidence': score
                })

        return results
