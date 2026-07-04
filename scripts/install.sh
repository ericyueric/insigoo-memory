#!/bin/bash
# insigoo-memory 一键安装
cd "$(dirname "$0")/.." && pip install -e . && echo "✅ insigoo-memory installed" || echo "❌ install failed"