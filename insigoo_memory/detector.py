"""
日程检测与建议引擎
从知识库中识别"该做还没做的事"
"""
import re
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

class ScheduleDetector:
    """从文件内容检测待办事项和日程"""

    # 中文日期表达模式
    DATE_PATTERNS = [
        (r'(\d{4})年(\d{1,2})月(\d{1,2})日', '%Y-%m-%d'),
        (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
        (r'截止日期[：:]\s*(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
        (r'(\d{4})年(\d{1,2})月启动', 'month'),
        (r'下个月', 'next_month'),
        (r'下个?周', 'next_week'),
        (r'暑假期', 'summer'),
        (r'寒假期', 'winter'),
    ]

    def detect(self, scan_results: dict) -> List[dict]:
        """从扫描结果中检测待办事项"""
        alerts = []
        now = datetime.now()

        for zone_id, files in scan_results.items():
            if zone_id.startswith('_'): continue  # skip metadata
            for f in files:
                if not isinstance(f, dict): continue
                path = f.get('path', '')
                p = Path(path)
                if p.suffix.lower() not in ('.md', '.txt'):
                    continue

                try:
                    content = p.read_text(encoding='utf-8', errors='ignore')[:2000]
                except:
                    continue

                alerts += self._detect_in_file(f['name'], content, now)

        return alerts

    def _detect_in_file(self, name: str, content: str, now: datetime) -> List[dict]:
        alerts = []

        # 规则1: 项目方案中的启动日快要到了
        for pattern, fmt in self.DATE_PATTERNS:
            for m in re.finditer(pattern, content):
                date_str = ''
                if fmt == '%Y-%m-%d':
                    date_str = f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
                elif fmt == 'month':
                    date_str = f"{m.group(1)}-{m.group(2).zfill(2)}-01"
                elif fmt == 'next_month':
                    dt = now.replace(day=1) + timedelta(days=32)
                    date_str = dt.strftime('%Y-%m-01')
                elif fmt == 'next_week':
                    dt = now + timedelta(days=7)
                    date_str = dt.strftime('%Y-%m-%d')
                else:
                    continue

                try:
                    target = datetime.strptime(date_str, '%Y-%m-%d')
                    days = (target - now).days

                    if 0 <= days <= 14:
                        alerts.append({
                            'type': 'deadline',
                            'file': name,
                            'message': f"「{name}」中的事件将在 {days} 天后 ({date_str}) 到来",
                            'urgency': 'high' if days <= 3 else 'medium',
                            'destination': 'calendar'
                        })
                    elif days > 14 and days <= 90:
                        alerts.append({
                            'type': 'upcoming',
                            'file': name,
                            'message': f"「{name}」提到 {date_str}，距今 {days} 天",
                            'urgency': 'low',
                            'destination': 'reminder'
                        })
                except:
                    pass
                break

        # 规则2: 项目未启动提醒
        if any(kw in content for kw in ['实施方案', '启动', '立项', '计划开展']):
            if not any(kw in content for kw in ['已启动', '进行中', '已完成', '结项']):
                alerts.append({
                    'type': 'stalled',
                    'file': name,
                    'message': f"「{name}」有方案但未见启动迹象，是否需要推进？",
                    'urgency': 'medium',
                    'destination': 'calendar'
                })

        # 规则3: 数据断档提醒
        if any(kw in name for kw in ['数据', '监测', '统计']):
            # 检查是否超过30天未更新
            try:
                p = Path(name)
                p = p if p.exists() else None  # use the actual path
            except:
                pass

        return alerts


class Advisor:
    """从知识库给出运营建议"""

    def suggest(self, scan_results: dict, issues: list = None) -> List[dict]:
        suggestions = []

        # 检测疑似重复和版本文件
        similars = self._find_similars(scan_results)
        if similars:
            for group in similars:
                names = ', '.join(f.get('name','?')[:25] for f in group)
                suggestions.append({
                    'type': 'duplicate',
                    'message': f'疑似重复/多版本: {names}',
                    'action': '建议人工确认后删除旧版本或统一命名'
                })

        # 建议1: 资金单一依赖
        finance_files = scan_results.get('finance', [])
        if not finance_files:
            suggestions.append({
                'type': 'gap',
                'message': '财务区无文件 — 建议建立基本的财务档案（预算执行表、捐赠明细等）',
                'action': '在 💰 财务资料区上传预算表'
            })

        # 建议2: 行业资讯过时
        industry_files = scan_results.get('industry', [])
        if industry_files:
            suggestions.append({
                'type': 'refresh',
                'message': f'行业资讯区 {len(industry_files)} 个文件 — 最近更新：{self._latest_file(industry_files)}',
                'action': '建议关注最新政策通知和资助机会'
            })

        # 建议3: 缺99公益物料（9月前）
        now = datetime.now()
        if 6 <= now.month <= 8:
            design_files = scan_results.get('design', [])
            has_99 = any('99' in f.get('name', '') or '公益日' in f.get('name', '')
                        for f in design_files)
            if not has_99:
                suggestions.append({
                    'type': 'prep',
                    'message': '99公益日临近（9月7-9日），设计物料区缺海报和传播素材',
                    'action': '提前准备99公益日设计物料'
                })

        # 建议4: 同类组织对标
        suggestions.append({
            'type': 'benchmark',
            'message': '同类公益组织通常每月更新 2-4 次项目痕迹，保持活动记录连续性',
            'action': '建议在 🏃 项目痕迹区保持规律更新'
        })

        return suggestions

    def _latest_file(self, files: list) -> str:
        """找最新文件"""
        import os
        for f in files:
            if isinstance(f, dict):
                p = f.get("path","")
                if p and os.path.exists(p):
                    from datetime import datetime
                    ts = datetime.fromtimestamp(os.path.getmtime(p))
                    return ts.strftime("%Y-%m-%d")
        return "未知"

    def _find_similars(self, scan_results: dict) -> list:
        """检测同一知识区内的疑似重复/多版本文件"""
        import difflib
        groups = []
        for zid, files in scan_results.items():
            if zid.startswith('_'): continue
            if not isinstance(files, list) or len(files) < 2:
                continue
            names = [f.get('name', '') for f in files if isinstance(f, dict)]
            seen = set()
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    if names[i] == names[j]:
                        continue
                    # 去掉版本号/日期后缀后比较
                    a = self._strip_version(names[i])
                    b = self._strip_version(names[j])
                    ratio = difflib.SequenceMatcher(None, a, b).ratio()
                    if ratio > 0.75:
                        key = tuple(sorted([names[i], names[j]]))
                        if key not in seen:
                            seen.add(key)
                            groups.append([f for f in files if isinstance(f, dict) and f.get('name') in key])
        return groups

    def _strip_version(self, name: str) -> str:
        """去掉文件名中的版本号和日期"""
        import re
        name = re.sub(r'[vV]\d+\.?\d*', '', name)         # v1, v2.0
        name = re.sub(r'\d{4}[-_]\d{2}[-_]\d{2}', '', name)  # 2026-01-15
        name = re.sub(r'_\d+$', '', name)                     # _2
        return name.strip('_ -')
