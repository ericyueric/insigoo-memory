"""
知识图谱生成器 — 基于关键词共现的文件关系图谱
"""
from collections import defaultdict

class GraphBuilder:
    """构建文件关联图谱 — 关键词共现"""

    def build(self, scan_results: dict) -> dict:
        nodes = []
        edges = []
        node_index = {}
        keyword_index = defaultdict(list)

        # 1. 提取所有文件的关键词
        for zid, files in scan_results.items():
            if not isinstance(files, list):
                continue
            for f in files:
                name = f.get('name', '')
                path = f.get('path', '')
                nid = f"{zid}_{name}"
                keywords = self._extract_keywords(name)
                nodes.append({'id': nid, 'name': name, 'zone': zid, 'keywords': keywords})
                node_index[nid] = len(nodes) - 1
                for kw in keywords:
                    keyword_index[kw].append(nid)

        # 2. 同关键词连接文件
        edge_set = set()
        for kw, files in keyword_index.items():
            if len(files) < 2:
                continue
            for i in range(len(files)):
                for j in range(i + 1, len(files)):
                    key = tuple(sorted([files[i], files[j]]))
                    if key not in edge_set:
                        edge_set.add(key)
                        edges.append({'source': files[i], 'target': files[j], 'keyword': kw})

        return {'nodes': nodes, 'edges': edges}

    def _extract_keywords(self, text: str) -> list:
        """从文件名提取关键词"""
        import re
        # 去掉扩展名、版本号、日期
        text = re.sub(r'\.[^.]+$', '', text)
        text = re.sub(r'[vV]\d+\.?\d*', '', text)
        text = re.sub(r'\d{4}[-_]\d{2}[-_]\d{2}', '', text)
        # 按分隔符拆分
        parts = re.split(r'[-_（）\(\)\s]+', text)
        # 过滤太短和太长的词
        return [p for p in parts if 2 <= len(p) <= 10 and not p.isdigit()]

    def to_cytoscape(self, scan_results: dict) -> list:
        """生成 Cytoscape.js 格式（可直接嵌 HTML）"""
        graph = self.build(scan_results)
        return [
            {'data': {'id': n['id'], 'label': n['name'][:30], 'group': n['zone']}}
            for n in graph['nodes']
        ], [
            {'data': {'id': f"{e['source']}_{e['target']}", 'source': e['source'], 'target': e['target']}}
            for e in graph['edges']
        ]
