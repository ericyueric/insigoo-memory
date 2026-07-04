"""
增强版看板 — 上传文件 / 诊断 / 知识产权声明
"""
import json, os, subprocess, tempfile, shutil
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser, threading, cgi


class DashboardServer:
    def __init__(self, watch_dir: str, port: int = 5055):
        self.watch_dir = watch_dir
        self.data_dir = Path(watch_dir) / ".insigoo-memory"
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
                elif self.path == "/api/diagnose":
                    self._json({"ready": True, "hint": "POST /api/diagnose with body {\"text\":\"...\"}"})
                elif self.path in ("/", ""):
                    self.path = "/index.html"; super().do_GET()
                else:
                    super().do_GET()

            def do_POST(self):
                if self.path == "/api/upload":
                    content_len = int(self.headers.get('Content-Length', 0))
                    body = self.rfile.read(content_len)
                    data = json.loads(body)
                    result = outer._handle_upload(data)
                    self._json(result)
                elif self.path == "/api/diagnose":
                    content_len = int(self.headers.get('Content-Length', 0))
                    body = self.rfile.read(content_len)
                    data = json.loads(body)
                    result = outer._diagnose(data.get("text", ""))
                    self._json(result)
                elif self.path == "/api/rescan":
                    outer._rescan()
                    self._json({"ok": True})
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
        r = FileClassifier().batch_classify(self.watch_dir)
        with open(self.data_dir / "scan_result.json", "w", encoding="utf-8") as fh:
            json.dump(r, fh, ensure_ascii=False, indent=2)

    ZONE_DIRS = {
        "industry": "行业资讯", "research": "研究学习", "design": "设计物料",
        "project_plan": "项目方案", "project_trace": "项目痕迹", "finance": "财务资料",
        "mne": "监测评估", "closure": "结项资料", "admin": "行政人事",
    }

    def _handle_upload(self, data: dict) -> dict:
        """JSON upload: {filename, content} — 写入文件后重分类 → 移动到对应知识区文件夹"""
        try:
            fname = data.get("filename", "uploaded_file.txt")
            content = data.get("content", "")
            dest = Path(self.watch_dir) / Path(fname).name
            dest.write_text(content, encoding="utf-8")
            from .classifier import FileClassifier
            zone, score = FileClassifier().classify(str(dest))
            # 移动到对应知识区文件夹
            zone_dir_name = self.ZONE_DIRS.get(zone.id, "未分类")
            zone_dir = Path(self.watch_dir) / zone_dir_name
            zone_dir.mkdir(exist_ok=True)
            final_path = zone_dir / dest.name
            shutil.move(str(dest), str(final_path))
            self._rescan()
            return {"ok": True, "filename": fname, "zone": zone.name, "emoji": zone.emoji,
                    "confidence": score, "moved_to": str(final_path)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _diagnose(self, text: str) -> dict:
        from .assess import Diagnostician
        return Diagnostician().assess(text)

    def _build_interactive(self) -> str:
        scan = json.dumps(self._scan_data(), ensure_ascii=False)
        return HTML_TEMPLATE.replace("__WATCH_DIR__", self.watch_dir).replace("__DATA_JSON__", scan)

    @staticmethod
    def build_dashboard_html(watch_dir: str, scan_data: dict) -> str:
        """静态方法：根据扫描数据生成看板 HTML（供 CLI 直接调用）"""
        return HTML_TEMPLATE.replace("__WATCH_DIR__", watch_dir).replace(
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
.status{display:flex;gap:12px;margin-bottom:14px;flex-wrap:wrap}
.stat{background:#161b22;border:1px solid #30363d;padding:7px 14px;border-radius:8px;font-size:12px}.stat strong{color:#58a6ff}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:12px}
.zone-card{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:12px;cursor:pointer;transition:border-color .2s}
.zone-card:hover{border-color:#58a6ff}.zone-card.empty{opacity:0.5}
.zone-header{display:flex;align-items:center;gap:8px;margin-bottom:4px}
.zone-emoji{font-size:18px}.zone-name{font-weight:600;font-size:14px}
.zone-count{margin-left:auto;background:#238636;color:#fff;padding:2px 10px;border-radius:20px;font-size:12px;font-weight:600}
.zone-count.zero{background:#30363d}.zone-desc{color:#8b949e;font-size:11px;margin-bottom:6px}
.zone-files{list-style:none;font-size:11px;display:none;max-height:200px;overflow-y:auto}
.zone-files.show{display:block}.zone-files li{padding:2px 0;color:#c9d1d9;border-bottom:1px solid #21262d}
.zone-files li:last-child{border-bottom:none}
.panel{margin-top:14px;background:#161b22;border:1px solid #30363d;border-radius:10px;padding:14px}
.panel h3{font-size:14px;margin-bottom:8px}
#diag-input{width:100%;min-height:80px;background:#0d1117;border:1px solid #30363d;color:#e1e4e8;padding:10px;border-radius:8px;font-size:12px;resize:vertical;margin-bottom:8px}
#diag-result{font-size:12px;line-height:1.6}
#diag-result .pass{color:#3fb950}#diag-result .fail{color:#f85149}
.upload-area{border:2px dashed #30363d;border-radius:10px;padding:20px;text-align:center;color:#8b949e;font-size:13px;margin-bottom:10px;cursor:pointer}
.upload-area:hover{border-color:#58a6ff;color:#e1e4e8}
.upload-area input{display:none}
.footer{margin-top:30px;padding:16px;background:#0d1117;border:1px solid #21262d;border-radius:10px;font-size:11px;color:#8b949e;line-height:1.7}
.footer h4{color:#e1e4e8;font-size:13px;margin-bottom:8px}
.footer a{color:#58a6ff}
.toast{position:fixed;top:16px;right:16px;background:#238636;color:#fff;padding:10px 20px;border-radius:8px;font-size:13px;z-index:999;display:none}
</style>
</head>
<body>
<h1>🧠 insigoo-memory</h1>
<p class="subtitle">📁 __WATCH_DIR__</p>

<div class="toolbar">
    <input type="text" id="search" placeholder="搜索文件名..." oninput="filter()">
    <button class="btn" onclick="render()">🔄 刷新</button>
    <button class="btn" onclick="rescan()">🔄 重新扫描</button>
    <button class="btn btn2" onclick="showPanel('diag-panel')">📋 项目诊断</button>
    <button class="btn" onclick="showPanel('upload-panel')">📤 上传文件</button>
</div>

<!-- Upload Panel -->
<div class="panel" id="upload-panel" style="display:none">
    <h3>📤 上传文件到知识库</h3>
    <div class="upload-area" onclick="document.getElementById('file-input').click()">
        <input type="file" id="file-input" onchange="handleUpload(this.files[0])">
        点击选择文件，或拖拽文件到此处
    </div>
    <div id="upload-result" style="font-size:12px;margin-top:8px"></div>
</div>

<!-- Diagnosis Panel -->
<div class="panel" id="diag-panel" style="display:none">
    <h3>📋 项目书诊断 (SIA L1 逻辑自洽)</h3>
    <textarea id="diag-input" placeholder="粘贴项目方案内容..."></textarea>
    <button class="btn" onclick="diagnose()">🔍 开始诊断</button>
    <div id="diag-result" style="margin-top:10px"></div>
</div>

<div class="status">
    <div class="stat">📄 <strong id="total">-</strong> 个文件</div>
    <div class="stat">📂 <strong id="zones_filled">-</strong> 个区域</div>
    <div class="stat">💡 <a href="#" onclick="showPanel('diag-panel')" style="color:#58a6ff">项目诊断</a></div>
</div>

<div class="grid" id="grid"></div>

<!-- Footer -->
<div class="footer">
<h4>📜 知识产权说明</h4>
<p>
<strong>insigoo-memory</strong> 由因思阁(insigoo)自主开发。<br>
<strong>借鉴的开源技术</strong>：Python标准库(http.server,argparse,dataclasses)、Ollama(本地LLM推理)、FAISS(向量索引)、LanceDB(嵌入式向量库设计理念)、EverOS(Markdown原生记忆层理念)。<br>
<strong>自研创新</strong>：9区NGO知识分类模型、SIA L1项目逻辑自洽评估框架(7原则)、12行业知识包体系、3级索引机制(目录/项目/场景)、日程检测与运营建议引擎、离线零成本部署方案。<br>
<strong>联系</strong>：<a href="mailto:insigoo@insigoo.cn">insigoo@insigoo.cn</a>
</p>
</div>

<div class="toast" id="toast"></div>

<script>
const EMBEDDED = __DATA_JSON__;
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
        const list = Array.isArray(files) ? files.map(f =>
            `<li><span title="${f.path||''}">${f.name||'?'}</span></li>`
        ).join('') || '<li style="color:#8b949e">（暂无文件）</li>' : '';
        return `<div class="zone-card${files.length===0?' empty':''}" onclick="this.querySelector('.zone-files').classList.toggle('show')">
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
    ['upload-panel','diag-panel'].forEach(x => {
        document.getElementById(x).style.display = (x===id ? 'block' : 'none');
    });
}

async function rescan() {
    toast('⏳ 重新扫描中...');
    await fetch('/api/rescan');
    await load();
    toast('✅ 扫描完成');
}

async function handleUpload(file) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async e => {
        const content = e.target.result;
        const r = await fetch('/api/upload', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({filename: file.name, content: content})
        });
        const d = await r.json();
        if (d.ok) {
            document.getElementById('upload-result').innerHTML =
                `✅ ${d.filename} → ${d.emoji} ${d.zone} (${d.confidence}%)
                 <br><span style="color:#8b949e;font-size:11px">📁 已保存至 ${d.moved_to}</span>`;
            await load();
        } else {
            document.getElementById('upload-result').innerHTML = `❌ ${d.error}`;
        }
    };
    reader.readAsText(file);
}

async function diagnose() {
    const text = document.getElementById('diag-input').value;
    if (!text) return toast('请先粘贴项目方案内容');
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
    setTimeout(() => t.style.display='none', 3000);
}

load();
setInterval(load, 60000);
</script>
</body>
</html>"""


def start_dashboard(watch_dir: str, port: int = 5055):
    server = DashboardServer(watch_dir, port)
    threading.Thread(target=server.start, daemon=True).start()
    import time; time.sleep(1.5)
    webbrowser.open(f"http://localhost:{port}")
    print("   看板已在浏览器中打开。按 Ctrl+C 停止。")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\n   👋 看板已关闭")
