"""
语料索引 — Agent对话中的问答路径自动记录
"""
import json
from pathlib import Path
from datetime import datetime


class CorpusIndex:
    """语料索引管理器"""

    def __init__(self, data_dir: str):
        self.dir = Path(data_dir) / ".insigoo-memory"
        self.file = self.dir / "corpus_index.json"
        self.md = self.dir / "corpus_index.md"

    def record(self, question: str, answer_file: str):
        """Agent 成功回答一条知识库问题 → 记录到语料库"""
        data = self._load()
        key = f"{question[:80]} → {answer_file[:80]}"
        if key not in data:
            data[key] = {"q": question[:80], "file": answer_file, "count": 0, "first": datetime.now().isoformat()}
        data[key]["count"] += 1
        data[key]["last"] = datetime.now().isoformat()
        self._save(data)
        self._write_md(data)

    def hot_paths(self, min_count: int = 5) -> list:
        """热路径：频次高的语料"""
        data = self._load()
        return [(k, v) for k, v in data.items() if v["count"] >= min_count]

    def get_for_query(self, question: str) -> dict:
        """查询时优先匹配语料库"""
        data = self._load()
        for k, v in data.items():
            if question[:30] in k or any(w in k for w in question.split()):
                return v
        return None

    def _load(self) -> dict:
        if self.file.exists():
            return json.loads(self.file.read_text(encoding="utf-8"))
        return {}

    def _save(self, data: dict):
        self.dir.mkdir(exist_ok=True)
        self.file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _write_md(self, data: dict):
        """生成 corpus_index.md"""
        lines = ["# corpus_index — 语料索引\n", "> Agent 从对话中自动提炼的问答路径\n"]
        lines.append("| 用户问 | Agent找到 | 频次 | 最后使用 |")
        lines.append("|--------|----------|:--:|---------|")

        for k, v in sorted(data.items(), key=lambda x: -x[1]["count"]):
            hot = "🔥 " if v["count"] >= 5 else ""
            last = v.get("last", "")[:10]
            lines.append(f"| {hot}{v['q'][:40]} | {v['file'][:40]} | {v['count']} | {last} |")

        self.md.write_text("\n".join(lines), encoding="utf-8")
