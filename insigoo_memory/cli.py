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
    """初始化知识库"""
    watch_dirs = args.watch or [os.getcwd()]
    if isinstance(watch_dirs, str):
        watch_dirs = [watch_dirs]
    issues = args.issues or ["教育"]
    max_size = getattr(args, 'max_size', 50)  # MB
    port = getattr(args, 'port', 5055)

    print(f"\n🧠 insigoo-memory v0.1.0")
    print(f"   正在扫描 {len(watch_dirs)} 个目录:")
    for wd in watch_dirs:
        print(f"     📁 {wd}")
    print(f"   关注议题: {', '.join(issues)}\n")

    # 分类所有目录
    cls = FileClassifier()
    all_results = {}
    for wd in watch_dirs:
        results = cls.batch_classify(wd)
        # 合并结果
        for zid, files in results.items():
            if zid not in all_results:
                all_results[zid] = []
            all_results[zid].extend(files)

    results = all_results

    # 统计
    total = sum(len(v) for k, v in results.items() if k != 'uncategorized')
    uncat = len(results.get('uncategorized', []))
    print(f"   ✅ 找到 {total} 个文件，跨 9 个知识区")
    if uncat:
        print(f"   ⚠ {uncat} 个文件暂未分类\n")
    else:
        print()

    # 输出 9 区看板
    print("═══ 9 区看板 ═══\n")
    for zone in ZONES:
        files = results.get(zone.id, [])
        icon = "📊" if len(files) > 0 else "📭"
        print(f"  {zone.emoji} {zone.name:6}  {len(files):>4} 个文件")
        if len(files) <= 3 and len(files) > 0:
            for f in files[:3]:
                print(f"     └─ {f['name'][:50]}")
        print()

    # 存储结果（存在第一个目录下）
    outdir = Path(watch_dirs[0]) / ".insigoo-memory"
    outdir.mkdir(exist_ok=True)
    # 同时记录扫描的所有目录
    results = dict(results)
    results['_scanned_dirs'] = watch_dirs
    with open(outdir / "scan_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"📁 扫描结果已保存到 {outdir}/scan_result.json")

    # 安装行业知识包
    from .packs import install_packs
    installed = install_packs(issues, str(outdir.parent))
    if installed:
        print(f"\n📦 已安装行业知识包:")
        for p in installed:
            print(f"   ✅ {p}")

    # 生成日报
    from .assess import NewsFetcher
    nf = NewsFetcher()
    briefing = nf.daily_briefing(str(outdir.parent), issues)
    (outdir / "daily_briefing.md").write_text(briefing, encoding="utf-8")
    print(f"\n📰 行业资讯日报已生成")

    # 日程检测 + 建议
    from .detector import ScheduleDetector, Advisor
    detector = ScheduleDetector()
    alerts = detector.detect(results)
    if alerts:
        print(f"\n🔔 发现 {len(alerts)} 个待办:")
        for a in alerts[:5]:
            icon = {'high':'🔴','medium':'🟡','low':'🟢'}.get(a['urgency'],'⚪')
            print(f"   {icon} {a['message'][:80]}")
        if len(alerts) > 5:
            print(f"   ... 还有 {len(alerts)-5} 个")

    advisor = Advisor()
    suggestions = advisor.suggest(results)
    print(f"\n💡 运营建议 ({len(suggestions)} 条):")
    for s in suggestions[:3]:
        print(f"   → {s['message'][:80]}")

    print(f"\n🌐 启动看板: insigoo-memory dashboard")


def cmd_scan(args):
    """重新扫描目录"""
    watch_dir = args.watch or os.getcwd()
    cls = FileClassifier()
    results = cls.batch_classify(watch_dir)
    total = sum(len(v) for v in results.values())
    print(f"扫描完成: {total} 个文件")
    outdir = Path(watch_dir) / ".insigoo-memory"
    outdir.mkdir(exist_ok=True)
    with open(outdir / "scan_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def cmd_dashboard(args):
    """生成交互式看板（纯静态 HTML，双击打开即可）"""
    watch_dir = args.watch or os.getcwd()
    from .dashboard import DashboardServer
    import json as _json

    result_file = Path(watch_dir) / ".insigoo-memory" / "scan_result.json"
    if not result_file.exists():
        print("⚠ 请先运行 insigoo-memory init")
        return

    with open(result_file, "r", encoding="utf-8") as f:
        scan_data = _json.load(f)

    html = DashboardServer.build_dashboard_html(watch_dir, scan_data)
    out = Path(watch_dir) / ".insigoo-memory" / "dashboard.html"
    out.write_text(html, encoding="utf-8")
    print(f"✅ 看板已生成: {out}")
    print(f"   双击打开即可使用 — 搜索、点击展开、实时过滤")
    if sys.platform == 'win32':
        os.startfile(str(out))


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

    p_dash = sub.add_parser('dashboard')
    p_dash.add_argument('-w', '--watch')

    p_doc = sub.add_parser('doctor')
    p_doc.add_argument('-w', '--watch')

    p_diag = sub.add_parser('diagnose', help='项目书诊断')
    p_diag.add_argument('-f', '--file', help='项目文件路径')
    p_diag.add_argument('-t', '--text', help='项目文本')

    p_brief = sub.add_parser('brief', help='行业日报')
    p_brief.add_argument('-w', '--watch')
    p_brief.add_argument('-i', '--issues', nargs='+')

    args = parser.parse_args()
    if args.command == 'init': cmd_init(args)
    elif args.command == 'scan': cmd_scan(args)
    elif args.command == 'dashboard': cmd_dashboard(args)
    elif args.command == 'doctor': cmd_doctor(args)
    elif args.command == 'diagnose': cmd_diagnose(args)
    elif args.command == 'brief': cmd_brief(args)
    else: parser.print_help()


if __name__ == '__main__':
    main()
