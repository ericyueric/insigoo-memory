"""
看板 — 九区知识看板，支持多文件夹、文件预览/打开、诊断（需LLM API）
"""
import json, os, subprocess, shutil
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser, threading


class DashboardServer:
    def __init__(self, watch_dirs: list, port: int = 5055):
        self.watch_dirs = watch_dirs
        self.primary = watch_dirs[0] if watch_dirs else os.getcwd()
        self.data_dir = Path(self.primary) / ".insigoo-memory"
        self.port = port

    def start(self):
        self.data_dir.mkdir(exist_ok=True)
        html = self._build_interactive()
        (self.data_dir / "dashboard.html").write_text(html, encoding="utf-8")
        (self.data_dir / "index.html").write_text(html, encoding="utf-8")
        prev = os.getcwd()
        os.chdir(str(self.data_dir))
        print(f"   🌐 看板已启动: http://localhost:{self.port}")
        try:
            HTTPServer(("127.0.0.1", self.port), self._handler()).serve_forever()
        finally:
            os.chdir(prev)

    def _handler(self):
        outer = self
        class H(SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/api/scan":
                    self._json(outer._scan_data())
                elif self.path == "/api/watched":
                    self._json({"dirs": outer.watch_dirs})
                elif self.path in ("/", ""):
                    self.path = "/index.html"; super().do_GET()
                elif self.path.startswith("/api/open"):
                    from urllib.parse import urlparse, parse_qs, unquote
                    qs = parse_qs(urlparse(self.path).query)
                    fp = unquote(qs.get("path", [""])[0])
                    if fp and os.path.exists(fp):
                        os.startfile(fp) if os.name == 'nt' else subprocess.Popen(['xdg-open', fp])
                        self._json({"ok": True, "opened": fp})
                    else:
                        self._json({"ok": False, "error": f"文件不存在: {fp}"})
                else:
                    super().do_GET()

            def do_POST(self):
                cl = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(cl)) if cl > 0 else {}
                if self.path == "/api/diagnose":
                    self._json(outer._diagnose(body.get("text", "")))
                elif self.path == "/api/rescan":
                    outer._rescan()
                    self._json({"ok": True})
                elif self.path == "/api/add-dir":
                    d = body.get("dir", "")
                    if d and os.path.isdir(d) and d not in outer.watch_dirs:
                        outer.watch_dirs.append(d)
                        outer._save_dirs()
                        outer._rescan()
                        self._json({"ok": True, "dir": d})
                    else:
                        self._json({"ok": False, "error": "目录不存在或已添加"})
                else:
                    self.send_response(404); self.end_headers()

            def _json(self, data):
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

            def log_message(self, *a): pass
        return H

    def _scan_data(self):
        f = self.data_dir / "scan_result.json"
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}

    def _rescan(self):
        from .classifier import FileClassifier
        from .nine_zones import ZONES
        fc = FileClassifier()
        merged = {z.id: [] for z in ZONES}
        merged['uncategorized'] = []
        seen = set()
        for wd in self.watch_dirs:
            for zid, files in fc.batch_classify(wd, skip_dirs={".insigoo-memory", ".workbuddy"}).items():
                for f in files:
                    key = f['name'] + f.get('path', '')
                    if key not in seen:
                        seen.add(key)
                        merged[zid].append(f)
        with open(self.data_dir / "scan_result.json", "w", encoding="utf-8") as fh:
            json.dump(merged, fh, ensure_ascii=False, indent=2)

    def _save_dirs(self):
        with open(self.data_dir / "watched_dirs.json", "w", encoding="utf-8") as f:
            json.dump(self.watch_dirs, f, ensure_ascii=False)

    def _diagnose(self, text: str) -> dict:
        from .assess import Diagnostician
        return Diagnostician().assess(text)

    def _build_interactive(self) -> str:
        dirs_json = json.dumps(self.watch_dirs, ensure_ascii=False)
        scan = json.dumps(self._scan_data(), ensure_ascii=False)
        return HTML_TEMPLATE.replace("__WATCH_DIRS__", dirs_json).replace("__DATA_JSON__", scan)

    @staticmethod
    def build_dashboard_html(watch_dirs: list, scan_data: dict) -> str:
        return HTML_TEMPLATE.replace("__WATCH_DIRS__", json.dumps(watch_dirs, ensure_ascii=False)).replace(
            "__DATA_JSON__", json.dumps(scan_data, ensure_ascii=False))


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>insigoo-memory · 知识库看板</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f1117;color:#e1e4e8;padding:20px;max-width:1200px;margin:0 auto}
h1{font-size:22px;margin-bottom:2px}.subtitle{color:#8b949e;font-size:12px;margin-bottom:12px}
.toolbar{display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap;align-items:center}
.toolbar input{flex:1;min-width:180px;background:#161b22;border:1px solid #30363d;color:#e1e4e8;padding:8px 14px;border-radius:8px;font-size:13px;outline:none}
.toolbar input:focus{border-color:#58a6ff}
.btn{background:#238636;border:none;color:#fff;padding:7px 14px;border-radius:8px;cursor:pointer;font-size:12px;font-weight:600;white-space:nowrap}
.btn:hover{background:#2ea043}.btn2{background:#1f6feb}.btn2:hover{background:#388bfd}
.btn-sm{background:#30363d;border:none;color:#c9d1d9;padding:3px 8px;border-radius:4px;cursor:pointer;font-size:11px}
.btn-sm:hover{background:#484f58}
.status{display:flex;gap:12px;margin-bottom:14px;flex-wrap:wrap}
.stat{background:#161b22;border:1px solid #30363d;padding:7px 14px;border-radius:8px;font-size:12px}.stat strong{color:#58a6ff}
.watched{font-size:11px;color:#8b949e;margin-bottom:12px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.watched span{background:#1a2332;padding:3px 10px;border-radius:12px;font-size:11px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:12px}
.zone-card{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:12px;transition:border-color .2s}
.zone-card:hover{border-color:#58a6ff}.zone-card.empty{opacity:0.5}
.zone-header{display:flex;align-items:center;gap:8px;margin-bottom:4px}
.zone-emoji{font-size:18px}.zone-name{font-weight:600;font-size:14px}
.zone-count{margin-left:auto;background:#238636;color:#fff;padding:2px 10px;border-radius:20px;font-size:12px;font-weight:600}
.zone-count.zero{background:#30363d}.zone-desc{color:#8b949e;font-size:11px;margin-bottom:6px}
.zone-files{list-style:none;font-size:11px;display:none;max-height:220px;overflow-y:auto}
.zone-files.show{display:block}.zone-files li{padding:4px 0;color:#c9d1d9;border-bottom:1px solid #21262d;display:flex;justify-content:space-between;align-items:center;gap:8px}
.zone-files li:last-child{border-bottom:none}
.zone-files li .fname{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;cursor:pointer}
.zone-files li .fname:hover{color:#58a6ff;text-decoration:underline}
.zone-files li .fpath{font-size:10px;color:#484f58;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.panel{margin-top:14px;background:#161b22;border:1px solid #30363d;border-radius:10px;padding:14px}
.panel h3{font-size:14px;margin-bottom:8px}
#diag-input{width:100%;min-height:80px;background:#0d1117;border:1px solid #30363d;color:#e1e4e8;padding:10px;border-radius:8px;font-size:12px;resize:vertical;margin-bottom:8px}
#diag-result{font-size:12px;line-height:1.6}
#diag-result .pass{color:#3fb950}#diag-result .fail{color:#f85149}
.diag-hint{background:#1a2332;border:1px solid #1f6feb;border-radius:8px;padding:10px 14px;font-size:12px;color:#8b949e;margin-bottom:10px}
.diag-hint strong{color:#58a6ff}
.add-dir{display:flex;gap:6px;margin-bottom:10px}
.add-dir input{flex:1;background:#161b22;border:1px solid #30363d;color:#e1e4e8;padding:6px 10px;border-radius:6px;font-size:12px}
.footer{margin-top:30px;padding:16px;background:#0d1117;border:1px solid #21262d;border-radius:10px;font-size:11px;color:#8b949e;line-height:1.7}
.footer h4{color:#e1e4e8;font-size:13px;margin-bottom:8px}
.footer a{color:#58a6ff}
.toast{position:fixed;top:16px;right:16px;background:#238636;color:#fff;padding:10px 20px;border-radius:8px;font-size:13px;z-index:999;display:none}
</style>
</head>
<body>
<h1>🧠 insigoo-memory</h1>
<p class="subtitle">公益组织 AI 知识管家 · 九区看板</p>

<div class="watched" id="watched-dirs"></div>

<div class="toolbar">
    <input type="text" id="search" placeholder="搜索文件名..." oninput="filter()">
    <button class="btn btn2" onclick="showPanel('add-dir-panel')">📂 关联文件夹</button>
    <button class="btn" onclick="rescan()">🔄 重新扫描</button>
    <button class="btn btn2" onclick="showPanel('diag-panel')">📋 项目诊断</button>
</div>

<!-- Add Directory -->
<div class="panel" id="add-dir-panel" style="display:none">
    <h3>📂 关联知识库文件夹</h3>
    <div class="add-dir">
        <input type="text" id="add-dir-input" placeholder="输入文件夹路径，如 D:\Documents\项目文件">
        <button class="btn" onclick="addDir()">➕ 关联并扫描</button>
    </div>
</div>

<!-- Diagnosis Panel -->
<div class="panel" id="diag-panel" style="display:none">
    <h3>📋 项目书诊断 (SIA L1 逻辑自洽)</h3>
    <div class="diag-hint">
        ⚠️ <strong>离线模式</strong>：诊断基于内置规则检查。<br>
        如需 AI 深度分析，请在终端设置 LLM API Key：<br>
        <code style="background:#0d1117;padding:2px 6px;border-radius:4px">ollama pull qwen2.5:7b</code> 启动本地模型，或设置 <code style="background:#0d1117;padding:2px 6px;border-radius:4px">DEEPSEEK_API_KEY</code> 环境变量。
    </div>
    <textarea id="diag-input" placeholder="粘贴项目方案内容..."></textarea>
    <button class="btn" onclick="diagnose()">🔍 开始诊断</button>
    <div id="diag-result" style="margin-top:10px"></div>
</div>

<div class="status">
    <div class="stat">📄 <strong id="total">-</strong> 个文件</div>
    <div class="stat">📂 <strong id="zones_filled">-</strong> 个区域</div>
</div>

<div class="grid" id="grid"></div>

<div class="footer">
<h4>📜 知识产权说明</h4>
<p>
<strong>insigoo-memory</strong> 由因思阁(insigoo)自主开发。<br>
<strong>借鉴的开源技术</strong>：Python标准库、Ollama、FAISS。<br>
<strong>自研创新</strong>：9区NGO知识分类模型、SIA L1项目逻辑自洽评估框架(7原则)、12行业知识包体系、4级索引机制(目录/项目/场景/语料)。<br>
<strong>联系</strong>：<a href="mailto:insigoo@insigoo.cn">insigoo@insigoo.cn</a>
</p>
</div>

<div class="toast" id="toast"></div>

<script>
const EMBEDDED = __DATA_JSON__;
const WATCHDIRS = __WATCH_DIRS__;
let scanData = EMBEDDED;
const ZONES = [
    {id:"industry",emoji:"📰",name:"行业资讯",desc:"政策通知、资助机会、同行动态"},
    {id:"research",emoji:"📚",name:"研究学习",desc:"行业报告、方法论、课程笔记"},
    {id:"design",emoji:"🎨",name:"设计物料",desc:"海报、Logo、公众号素材"},
    {id:"project_plan",emoji:"📝",name:"项目方案",desc:"计划书、申请表、预算"},
    {id:"project_trace",emoji:"🏃",name:"项目痕迹",desc:"活动照片、签到表、志愿者名单"},
    {id:"finance",emoji:"💰",name:"财务资料",desc:"预算执行、捐赠记录、审计报告"},
    {id:"mne",emoji:"📊",name:"监测评估",desc:"指标定义、满意度调查、评估报告"},
    {id:"closure",emoji:"📦",name:"结项资料",desc:"结项报告、成果总结"},
    {id:"admin",emoji:"🏢",name:"行政人事",desc:"章程、理事会纪要、员工手册"},
];

async function load() {
    try { const r = await fetch('/api/scan'); scanData = await r.json(); } catch(e) {}
    render();
}

function renderWatched() {
    const el = document.getElementById('watched-dirs');
    el.innerHTML = '📁 知识库文件夹: ' + WATCHDIRS.map(d =>
        `<span title="${d}">${d.split(/[\\/]/).pop()||d}</span>`
    ).join('');
}
renderWatched();

function filter() {
    const q = document.getElementById('search').value.toLowerCase();
    document.querySelectorAll('.zone-card').forEach(card => {
        const files = card.querySelectorAll('li');
        let hasMatch = false;
        files.forEach(f => {
            if (q && !f.textContent.toLowerCase().includes(q)) f.style.display='none';
            else { f.style.display=''; hasMatch = true; }
        });
        card.classList.toggle('empty', !hasMatch && q.length > 0);
    });
}

function render() {
    const grid = document.getElementById('grid'); let total = 0, filled = 0;
    grid.innerHTML = ZONES.map(z => {
        const files = scanData[z.id] || [];
        if (Array.isArray(files)) { total += files.length; if (files.length > 0) filled++; }
        const list = Array.isArray(files) ? files.map(f => {
            const fp = f.path || '';
            const name = f.name || '?';
            const displayPath = fp.length > 60 ? '...' + fp.slice(-57) : fp;
            return `<li>
                <span class="fname" onclick="openFile('${fp.replace(/'/g,"\\'")}')" title="${fp}">${name}</span>
                <span class="fpath" title="${fp}">${displayPath}</span>
                <button class="btn-sm" onclick="openFile('${fp.replace(/'/g,"\\'")}')">📂</button>
            </li>`;
        }).join('') || '<li style="color:#8b949e">（暂无文件）</li>' : '';
        return `<div class="zone-card${files.length===0?' empty':''}" onclick="event.target.tagName==='DIV'&&this.querySelector('.zone-files').classList.toggle('show')">
            <div class="zone-header">
                <span class="zone-emoji">${z.emoji}</span>
                <span class="zone-name">${z.name}</span>
                <span class="zone-count${files.length===0?' zero':''}">${files.length||0}</span>
            </div>
            <div class="zone-desc">${z.desc}</div>
            <ul class="zone-files">${list}</ul>
        </div>`;
    }).join('');
    document.getElementById('total').textContent = total;
    document.getElementById('zones_filled').textContent = filled + '/9';
}

function showPanel(id) {
    ['add-dir-panel','diag-panel'].forEach(x => {
        document.getElementById(x).style.display = (x===id ? 'block' : 'none');
    });
}

function openFile(path) {
    if (!path) return;
    // 统一转正斜杠，避免反斜杠编码问题
    const safe = path.replace(/\\/g, '/');
    fetch('/api/open?path=' + encodeURIComponent(safe))
        .then(r => r.json())
        .then(d => {
            if (d.ok) {
                toast('📂 已打开 ' + (d.opened || '').split(/[\\/]/).pop());
            } else {
                navigator.clipboard?.writeText(path);
                toast('❌ ' + (d.error || '无法打开'));
            }
        })
        .catch(() => {
            navigator.clipboard?.writeText(path);
            toast('⚠️ 请通过 http://localhost:5055 访问看板');
        });
}

async function rescan() {
    toast('⏳ 重新扫描中...');
    await fetch('/api/rescan', {method:'POST'});
    await load();
    toast('✅ 扫描完成');
}

async function addDir() {
    const dir = document.getElementById('add-dir-input').value.trim();
    if (!dir) return toast('请输入文件夹路径');
    const r = await fetch('/api/add-dir', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({dir})
    });
    const d = await r.json();
    if (d.ok) {
        WATCHDIRS.push(d.dir);
        renderWatched();
        toast('✅ 已关联: ' + d.dir.split(/[\\/]/).pop());
        await load();
    } else {
        toast('❌ ' + (d.error || '添加失败'));
    }
}

async function diagnose() {
    const text = document.getElementById('diag-input').value;
    if (!text) return toast('请先粘贴项目方案内容');
    toast('⏳ 诊断中...');
    const r = await fetch('/api/diagnose', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({text})
    });
    const d = await r.json();
    const result = document.getElementById('diag-result');
    result.innerHTML = `
        <p style="margin-bottom:8px"><strong>📊 总评：${d.verdict}</strong> (${d.score.pass}/7 项通过)</p>
        ${d.principles.map(p => `<div class="${p.status.includes('通过')?'pass':'fail'}">${p.status} ${p.name}: ${p.desc}</div>`).join('')}
        ${d.suggestions?.length ? '<p style="margin-top:8px"><strong>💡 建议：</strong></p>'+d.suggestions.map(s=>`<div style="color:#d2991d">→ ${s}</div>`).join('') : ''}
    `;
}

function toast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg; t.style.display='block';
    setTimeout(() => t.style.display='none', 2800);
}

load();
setInterval(load, 60000);
</script>
</body>
</html>"""


def start_dashboard(watch_dirs: list, port: int = 5055):
    server = DashboardServer(watch_dirs, port)
    threading.Thread(target=server.start, daemon=True).start()
    import time; time.sleep(1.5)
    webbrowser.open(f"http://localhost:{port}")
    print("   看板已在浏览器中打开。按 Ctrl+C 停止。")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\n   👋 看板已关闭")
