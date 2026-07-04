"""
文件自动分类器 — 把文件丢进去，自动判断属于哪个知识区
"""
import os
import re
from pathlib import Path
from typing import Optional
from .nine_zones import ZONES, Zone

class FileClassifier:
    """三步判定法：文件名 → 目录结构 → 内容关键词"""

    def __init__(self):
        self._compile_patterns()

    def _compile_patterns(self):
        for zone in ZONES:
            zone._compiled_keywords = zone.keywords

    def classify(self, filepath: str, use_llm: bool = False) -> tuple:
        """
        判定文件属于哪个知识区。
        如果置信度 < 50%，且 use_llm=True，查询 LLM
        """
        path = Path(filepath)
        filename = path.name.lower()
        dirname = path.parent.name.lower() if path.parent.name else ""

        scores = {}
        # 一次性读取文件内容（所有zone共用）
        content = ""
        if path.suffix.lower() in ('.md', '.txt', '.csv', '.json', '.html'):
            try:
                content = path.read_text(encoding='utf-8', errors='ignore')[:1000]
            except:
                pass

        for zone in ZONES:
            score = 0

            # 第1步：文件名模式匹配（权重 50%）
            for pattern in zone.file_patterns:
                if self._glob_match(filename, pattern):
                    score += 50
                    break

            # 第2步：目录名匹配（权重 30%）
            for kw in zone.keywords:
                if kw.lower() in dirname:
                    score += 30
                    break

            # 第3步：内容关键词（每个命中+5，取消固定+20）
            if content:
                kw_matches = sum(1 for kw in zone.keywords if kw in content)
                score += min(kw_matches * 5, 25)

            scores[zone.id] = min(score, 100)

        # 特殊内容信号检测（比关键词更可靠，直接覆盖）
        if content:
            if '姓名' in content and '签到' in content:
                scores['project_trace'] = 95
            if '合作期限' in content and ('备忘录' in content or '协议' in content):
                scores['industry'] = 90
            if '问卷' in content and ('%' in content or '家' in content) and '调查' in content:
                scores['research'] = 85

        # 文件名信号（对二进制文件尤为重要）
        if any(k in filename for k in ['预算', '报销', '决算', '票据', '记账', '签收']):
            scores['finance'] = max(scores.get('finance', 0), 85)
        if any(k in filename for k in ['餐费', '租车', '交通费', '文具', '办公用品']):
            scores['finance'] = max(scores.get('finance', 0), 80)

        best = max(scores, key=scores.get)
        best_score = scores[best]
        best_zone = next(z for z in ZONES if z.id == best)

        # 低置信度 → LLM 辅助
        if best_score < 30:
            llm_zone = self._llm_classify(filepath)
            if llm_zone:
                return llm_zone, 80  # LLM 分类给 80% 置信度
            best_zone = Zone(
                id="uncategorized",
                name="未分类",
                emoji="?",
                description="需要人工确认",
                keywords=[]
            )

        return best_zone, best_score

    def _glob_match(self, filename: str, pattern: str) -> bool:
        """简化版 glob 匹配"""
        pattern = pattern.lower().replace('*', '')
        return pattern in filename

    def _llm_classify(self, filepath: str) -> Optional[Zone]:
        """用 LLM 辅助分类（Ollama qwen2.5）"""
        path = Path(filepath)
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')[:500]
        except Exception:
            return None

        zone_list = '\n'.join(
            f"- {z.id}: {z.name} — {z.description}"
            for z in ZONES
        )
        prompt = f"""请判断以下文件属于哪个知识区。只返回区域ID。

文件路径: {path.name}
文件内容片段:
{content[:300]}

可选区域:
{zone_list}

返回格式: 只返回一个单词（区域ID），比如 project_plan"""

        try:
            import requests
            r = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'qwen2.5:7b',
                    'prompt': prompt,
                    'stream': False,
                    'options': {'num_predict': 20}
                },
                timeout=15
            )
            response = r.json().get('response', '').strip().lower()
            for z in ZONES:
                if z.id in response:
                    return z
        except Exception:
            pass
    def batch_classify(self, root_dir: str, max_mb: int = None, mtime_cache: dict = None) -> dict:
        """批量扫描目录，返回分类结果"""
        results = {z.id: [] for z in ZONES}
        results['uncategorized'] = []

        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in files:
                fp = os.path.join(root, f)
                # 跳过超大文件
                if max_mb:
                    try:
                        if os.path.getsize(fp) > max_mb * 1024 * 1024:
                            continue
                    except: pass
                # 增量：跳过未修改的文件
                if mtime_cache and fp in mtime_cache:
                    try:
                        if os.path.getmtime(fp) == mtime_cache[fp]:
                            continue
                    except: pass
                zone, score = self.classify(fp)
                results[zone.id].append({
                    'path': fp, 'name': f,
                    'zone': zone.name, 'emoji': zone.emoji,
                    'confidence': score
                })

        return results
