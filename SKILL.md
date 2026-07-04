---
name: insigoo-memory
version: 0.3.0
description: 公益组织 AI 知识管家 — 自动分类、自动索引、主动提醒。适用于：初始化知识库、扫描文件结构、检查知识健康度、生成9区看板、检测日程待办。用户上传文件时自动触发分类归档。
author: insigoo · 米斯蒂 & 虾米
trigger_keywords: [知识库, 文件分类, 文件管理, 归档, 整理文件, 看板, 日程提醒, insigoo-memory]
tags: [知识库, 公益, NPO, 文件管理, 自动分类]
---

# insigoo-memory

> 公益组织的 AI 知识管家。把文件丢进去，自动分类、自动索引、主动告诉你该做什么。

---

## 什么时候用这个 SKILL

### 文字触发

当用户提到以下任意关键词时加载本 SKILL：

- "整理一下这些文件" / "帮我看看项目文件"
- "知识库" / "文件分类" / "归档"
- "insigoo-memory" / "看板"
- "检查文件健康" / "日程提醒"
- "项目书评估" / "诊断项目" / "帮我看看这个方案"
- "行业资讯" / "今日日报"

### 文件上传触发（自动）

当用户在对话窗口上传/分享文件时，Agent 应自动执行以下流程：

**① 无需等待用户指令**，直接读取文件内容并调用分类器
**② 将文件保存到对应知识区文件夹**
**③ 告知用户分类结果**，格式："📁 [文件名] → [emoji] [知识区]"

示例：
```
用户: [上传了 儿童之家项目书.docx]
Agent: 📁 儿童之家项目书.docx → 📝 项目方案（85%）
       已保存至「项目方案」文件夹。
       需要我诊断这份项目书吗？
```

---

## 安装

```bash
cd D:/workbuddy/insigoo-memory && pip install -e .
```

验证安装：
```bash
insigoo-memory --help
```

---

## 核心命令

### 1. 初始化 — 首次扫描目录

```bash
insigoo-memory init -w <目标目录> -i <议题1> <议题2>
```

示例：
```bash
insigoo-memory init -w "D:/机构文件" -i 环保 教育
```

**输出**：
- 9 区分类统计
- 行业知识包安装（自动下载所选议题的政策/标准/术语）
- 行业资讯日报
- 日程检测结果
- 运营建议
- 扫描结果保存到 `<目标目录>/.insigoo-memory/`
- 看板生成到 `<目标目录>/.insigoo-memory/dashboard.html`

### 2. 看板 — 打开 Web 界面

```bash
insigoo-memory dashboard -w <目标目录>
```

自动在浏览器打开 9 区可视化看板。

### 3. 重新扫描

```bash
insigoo-memory scan -w <目标目录>
```

### 4. 健康检查

```bash
insigoo-memory doctor -w <目标目录>
```

检查项：
- 扫描结果是否存在
- 9 个知识区哪几个为空
- 未分类文件数量
- 疑似重复文件

---

## 9 个知识区

| ID | 名称 | 装什么 |
|----|------|--------|
| `industry` | 📰 行业资讯 | 政策通知、资助机会、同行动态 |
| `research` | 📚 研究学习 | 行业报告、方法论、课程笔记 |
| `design` | 🎨 设计物料 | 海报、Logo、公众号素材 |
| `project_plan` | 📝 项目方案 | 计划书、申请表、预算 |
| `project_trace` | 🏃 项目痕迹 | 活动照片、签到表、志愿者名单 |
| `finance` | 💰 财务资料 | 预算执行、捐赠记录、审计报告 |
| `mne` | 📊 监测评估 | 指标定义、满意度调查、评估报告 |
| `closure` | 📦 结项资料 | 结项报告、成果总结 |
| `admin` | 🏢 行政人事 | 章程、理事会纪要、员工手册 |

---

## 常见任务脚本

### 任务 A：用户给了你一个目录，说"帮我整理一下"

```bash
# 1. 扫描
insigoo-memory init -w <目录> -i 环保

# 2. 打开看板
insigoo-memory dashboard -w <目录>

# 3. 告诉用户结果
# 有多少文件、分到了哪些区域、发现了什么待办
```

### 任务 B：用户说"检查一下知识库健康度"

```bash
insigoo-memory doctor -w <目录>
```

然后根据 `doctor` 的输出，告诉用户：
- 哪些区域缺数据
- 哪些文件未被分类
- 有没有疑似重复文件

### 任务 C：用户安装了新版本的 insigoo-memory

```bash
cd D:/workbuddy/insigoo-memory && pip install -e . --upgrade
```

---

## 故障排查

| 问题 | 解决 |
|------|------|
| `insigoo-memory: command not found` | pip install -e . 未执行 |
| 分类准确率低 | 当前基于关键词匹配，第二阶段将接入本地 LLM |
| 看板打不开 | 检查 `.insigoo-memory/scan_result.json` 是否存在 |
| 扫描很慢 | 文件超过 1000 个时建议分批扫 |

---

## 项目路径

```
D:/workbuddy/insigoo-memory/
├── setup.py
├── PRODUCT.md           ← 面向公益机构的产品文档
├── insigoo_memory/
│   ├── cli.py           ← init / scan / dashboard / doctor
│   ├── classifier.py    ← 文件分类引擎（规则+LLM）
│   ├── nine_zones.py    ← 9区定义
│   └── detector.py      ← 日程检测+建议引擎
```

---

*insigoo 因思阁 · 让每一个公益组织都有自己的 AI 知识管家*
