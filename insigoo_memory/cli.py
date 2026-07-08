"""
CLI 入口 — insigoo-memory 命令行工具
用法: insigoo-memory init | scan | doctor | dashboard
"""
import sys
import os
import json
from pathlib import Path
from .classifier import FileClassifier
from .nine_zones import ZONES

def cmd_init(args):
    """初始化知识库 — 交互式向导"""
    watch_dirs = list(args.watch) if args.watch else []

    # 交互式：询问目录
    if not watch_dirs:
        print("\n🧠 insigoo-memory v0.4.0")
        print("   公益组织 AI 知识管家\n")
        d = input("📁 请输入知识库文件夹路径: ").strip()
        if not d:
            print("❌ 未输入路径，已取消")
            return
        if not os.path.isdir(d):
            print(f"❌ 目录不存在: {d}")
            return
        watch_dirs = [d]

    issues = args.issues or ["公益", "环境", "教育"]
    max_size = getattr(args, 'max_size', 100)
    port = getattr(args, 'port', 5055)

    print(f"\n   正在扫描 {len(watch_dirs)} 个目录:")
    for wd in watch_dirs:
        print(f"     📁 {wd}")
    print(f"   关注议题: {', '.join(issues)}")
    print(f"   跳过 >{max_size}MB 的文件\n")

    # 分类
    cls = FileClassifier()
    from .nine_zones import ZONES
    merged = {z.id: [] for z in ZONES}
    merged['uncategorized'] = []
    seen = set()
    for wd in watch_dirs:
        results = cls.batch_classify(wd, max_mb=max_size, skip_dirs={".insigoo-memory", ".git", ".workbuddy"})
        for zid, files in results.items():
            for f in files:
                key = f['name'] + f.get('path', '')
                if key not in seen:
                    seen.add(key)
                    merged[zid].append(f)

    total = sum(len(v) for k, v in merged.items() if k != 'uncategorized')
    uncat = len(merged.get('uncategorized', []))
    print(f"   ✅ 找到 {total} 个文件，跨 9 个知识区")
    if uncat:
        print(f"   ⚠ {uncat} 个文件暂未分类")

    # 保存结果 + 目录配置
    outdir = Path(watch_dirs[0]) / ".insigoo-memory"
    outdir.mkdir(exist_ok=True)
    merged['_watched_dirs'] = watch_dirs
    with open(outdir / "scan_result.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    with open(outdir / "watched_dirs.json", "w", encoding="utf-8") as f:
        json.dump(watch_dirs, f, ensure_ascii=False)

    # 四级索引
    from .corpus import CorpusIndex
    CorpusIndex(str(outdir.parent))._write_md({})
    print(f"\n🧬 四级索引体系已就绪")

    # 输出九区看板
    print("\n═══ 9 区看板 ═══\n")
    for zone in ZONES:
        files = merged.get(zone.id, [])
        bar = "█" * min(len(files) // 20, 30) if len(files) > 0 else ""
        print(f"  {zone.emoji} {zone.name:6s}  {len(files):>5d}  {bar}")

    # 打开看板
    print(f"\n🌐 看板已生成: {outdir}/dashboard.html")
    if sys.platform == 'win32':
        os.startfile(str(outdir / "dashboard.html"))

    # 日报
    from .assess import NewsFetcher
    try:
        nf = NewsFetcher()
        briefing = nf.daily_briefing(str(outdir.parent), issues)
        (outdir / "daily_briefing.md").write_text(briefing, encoding="utf-8")
        print(f"\n📰 行业资讯日报已生成")
    except:
        pass

    print(f"\n💡 提示:")
    print(f"   关联更多文件夹: insigoo-memory scan --add <路径>")
    print(f"   重新扫描: insigoo-memory scan")
    print(f"   项目诊断: insigoo-memory diagnose -f <文件>")
    print(f"   启动看板: insigoo-memory dashboard")


def cmd_scan(args):
    """重新扫描目录，支持 --add 添加新文件夹"""
    watch_dir = args.watch or os.getcwd()

    # 加载已有关联目录
    cfg_file = Path(watch_dir) / ".insigoo-memory" / "watched_dirs.json"
    watched = json.loads(cfg_file.read_text(encoding="utf-8")) if cfg_file.exists() else [watch_dir]

    # --add 添加新目录
    if hasattr(args, 'add') and args.add:
        for d in args.add:
            d = os.path.abspath(d)
            if os.path.isdir(d) and d not in watched:
                watched.append(d)
                print(f"   📂 已关联: {d}")

    skip = set(args.skip or [])
    cls = FileClassifier()
    from .nine_zones import ZONES
    merged = {z.id: [] for z in ZONES}
    merged['uncategorized'] = []
    seen = set()

    for wd in watched:
        results = cls.batch_classify(wd, skip_dirs=skip)
        for zid, files in results.items():
            for f in files:
                key = f['name'] + f.get('path', '')
                if key not in seen:
                    seen.add(key)
                    merged[zid].append(f)

    total = sum(len(v) for v in merged.values())
    print(f"扫描完成: {total} 个文件（{len(watched)} 个目录）")
    outdir = Path(watch_dir) / ".insigoo-memory"
    outdir.mkdir(exist_ok=True)
    merged['_watched_dirs'] = watched
    with open(outdir / "scan_result.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    with open(outdir / "watched_dirs.json", "w", encoding="utf-8") as f:
        json.dump(watched, f, ensure_ascii=False)


def cmd_dashboard(args):
    """生成交互式看板并启动本地服务（支持文件打开）"""
    watch_dir = args.watch or os.getcwd()

    # 加载关联目录
    cfg_file = Path(watch_dir) / ".insigoo-memory" / "watched_dirs.json"
    watched = json.loads(cfg_file.read_text(encoding="utf-8")) if cfg_file.exists() else [watch_dir]

    result_file = Path(watch_dir) / ".insigoo-memory" / "scan_result.json"
    if not result_file.exists():
        print("⚠ 请先运行 insigoo-memory init")
        return

    with open(result_file, "r", encoding="utf-8") as f:
        scan_data = json.load(f)
    scan_data.pop('_watched_dirs', None)

    from .dashboard import DashboardServer
    html = DashboardServer.build_dashboard_html(watched, scan_data)
    out = Path(watch_dir) / ".insigoo-memory" / "dashboard.html"
    out.write_text(html, encoding="utf-8")

    # 启动本地 server（必须，文件打开功能依赖 /api/open）
    port = getattr(args, 'port', 5055)
    server = DashboardServer(watched, port)
    import threading
    t = threading.Thread(target=server.start, daemon=True)
    t.start()
    import time; time.sleep(0.5)

    print(f"🌐 看板已启动: http://localhost:{port}")
    print(f"   📂 点击文件→自动用系统程序打开")
    print(f"   按 Ctrl+C 停止")
    if sys.platform == 'win32':
        os.startfile(f"http://localhost:{port}")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\n   👋 看板已关闭")


def cmd_doctor(args):
    watch_dir = args.watch or os.getcwd()
    result_file = Path(watch_dir) / ".insigoo-memory" / "scan_result.json"

    print("🩺 insigoo-memory 健康检查\n")
    issues = []

    if not result_file.exists():
        issues.append("❌ 未扫描 — 请先运行 insigoo-memory scan")
    else:
        print("   ✅ 扫描结果存在")
        with open(result_file, "r", encoding="utf-8") as f:
            results = json.load(f)

        # 检查各知识区
        for zone in ZONES:
            files = results.get(zone.id, [])
            if len(files) == 0:
                issues.append(f"⚠ {zone.emoji} {zone.name} 为空 — 该区域无文件")

        # 检查低置信度分类
        uncat = results.get('uncategorized', [])
        if uncat:
            issues.append(f"⚠ {len(uncat)} 个文件未能自动分类")

        # 重复文件检查
        paths = []
        for zid, files in results.items():
            if zid.startswith('_'): continue
            for f in files:
                if isinstance(f, dict):
                    paths.append(f['name'])
        dupes = [p for p in set(paths) if paths.count(p) > 1]
        if dupes:
            issues.append(f"⚠ {len(dupes)} 个疑似重复文件")

    if issues:
        print()
        for i in issues:
            print(f"   {i}")
    else:
        print("\n   ✅ 健康评分: 100/100")

    return len(issues) == 0


def cmd_diagnose(args):
    """项目书诊断"""
    from .assess import Diagnostician
    d = Diagnostician()
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8", errors="ignore")
    elif args.text:
        text = args.text
    else:
        print("请提供 -f 文件路径 或 -t 文本内容")
        return
    report = d.assess(text)
    print(f"\n📋 项目书诊断报告")
    print(f"  评分: {report['verdict']}")
    print(f"  通过 {report['score']['pass']}/7 项原则\n")
    for p in report['principles']:
        print(f"  {p['status']} {p['name']}: {p['desc']}")
    if report['suggestions']:
        print(f"\n💡 改进建议 ({len(report['suggestions'])}条):")
        for s in report['suggestions']:
            print(f"  → {s}")


def cmd_brief(args):
    """行业日报"""
    watch_dir = args.watch or os.getcwd()
    issues = args.issues or ["教育"]
    from .assess import NewsFetcher
    nf = NewsFetcher()
    briefing = nf.daily_briefing(watch_dir, issues)
    result_file = Path(watch_dir) / ".insigoo-memory" / "daily_briefing.md"
    result_file.parent.mkdir(parents=True, exist_ok=True)
    result_file.write_text(briefing, encoding="utf-8")
    print(f"\n📰 行业资讯日报已生成: {result_file}")
    print(briefing)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='insigoo-memory')
    sub = parser.add_subparsers(dest='command')

    p_init = sub.add_parser('init')
    p_init.add_argument('-w', '--watch', nargs='+')
    p_init.add_argument('-i', '--issues', nargs='+')
    p_init.add_argument('--port', type=int, default=5055, help='看板端口')
    p_init.add_argument('--max-size', type=int, default=50, help='跳过大于此MB的文件')

    p_scan = sub.add_parser('scan')
    p_scan.add_argument('-w', '--watch')
    p_scan.add_argument('--skip', nargs='+', help='排除目录')
    p_scan.add_argument('--add', nargs='+', help='关联新文件夹')

    p_dash = sub.add_parser('dashboard')
    p_dash.add_argument('-w', '--watch')
    p_dash.add_argument('-p', '--port', type=int, default=5055)

    p_doc = sub.add_parser('doctor')
    p_doc.add_argument('-w', '--watch')

    p_diag = sub.add_parser('diagnose', help='项目书诊断')
    p_diag.add_argument('-f', '--file', help='项目文件路径')
    p_diag.add_argument('-t', '--text', help='项目文本')

    p_brief = sub.add_parser('brief', help='行业日报')
    p_brief.add_argument('-w', '--watch')
    p_brief.add_argument('-i', '--issues', nargs='+')

    p_corpus = sub.add_parser('corpus', help='语料索引')
    p_corpus.add_argument('-w', '--watch')
    p_corpus.add_argument('-q', '--question')
    p_corpus.add_argument('-a', '--answer')

    args = parser.parse_args()
    if args.command == 'init': cmd_init(args)
    elif args.command == 'scan': cmd_scan(args)
    elif args.command == 'dashboard': cmd_dashboard(args)
    elif args.command == 'doctor': cmd_doctor(args)
    elif args.command == 'diagnose': cmd_diagnose(args)
    elif args.command == 'brief': cmd_brief(args)
    elif args.command == 'corpus': cmd_corpus(args)
    else: parser.print_help()


def cmd_corpus(args):
    """语料索引: 记录问答 或 查看热路径"""
    watch_dir = args.watch or os.getcwd()
    from .corpus import CorpusIndex
    ci = CorpusIndex(watch_dir)
    if args.question and args.answer:
        ci.record(args.question, args.answer)
        print(f"✅ 已记录语料")
    else:
        hot = ci.hot_paths()
        if hot:
            print(f"\n🔥 热路径 ({len(hot)} 条):")
            for k, v in hot[:10]:
                print(f"   {v['count']}× {v['q'][:50]} → {v['file'][:40]}")
        else:
            print("暂无热路径（频次不足5）")

def cmd_brief(args):
    """行业日报"""
    watch_dir = args.watch or os.getcwd()
    from .assess import NewsFetcher
    issues = args.issues or []
    nf = NewsFetcher()
    briefing = nf.daily_briefing(watch_dir, issues)
    print(briefing)


if __name__ == '__main__':
    main()
