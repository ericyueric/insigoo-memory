#!/bin/bash
# insigoo-memory 健康检查
cd "$(dirname "$0")/.."

echo "🧠 insigoo-memory skill check"
echo "==============================="

# 检查核心模块
for f in insigoo_memory/cli.py insigoo_memory/classifier.py insigoo_memory/nine_zones.py insigoo_memory/detector.py; do
    [ -f "$f" ] && echo "  ✅ $f" || echo "  ❌ $f MISSING"
done

# 检查 CLI 可用性
insigoo-memory --version 2>/dev/null && echo "  ✅ CLI works" || echo "  ⚠ CLI not installed (run scripts/install.sh)"

echo ""
echo "📦 Skill structure:"
echo "  SKILL.md      — Agent instructions"
echo "  setup.py      — pip install entry"
echo "  insigoo_memory/ — Python engine"
echo "  scripts/      — install.sh, verify.sh"
echo "  references/   — PRODUCT.md (human doc)"

echo ""
echo "Done."