# 知识库索引 (Knowledge Index)

> **最后更新**: YYYY-MM-DD
> **维护者**: [姓名/角色]
> **用途**: 三层索引系统 — 目录索引(按文件位置) + 主题索引(按知识实体) + 受治理查询场景索引(GDT-KB 六要素+六约束)

---

## 使用说明

本文件是知识库的**核心入口**，包含三层索引：
- **第1层：目录索引** — 按文件位置查找（"XX文件在哪？"）
- **第2层：主题索引** — 按知识实体查找（"关于XX主题有什么？"）
- **第3层：提问场景索引** — 按问题查找路径（"我想知道XX，去哪找？"）

**维护规则**：每次新增/修改文档后，必须同步更新本索引。

---

## 第1层：目录索引（按文件位置）

### 快速索引表

| 类别 | 位置 | 关键内容 |
|------|------|----------|
| **组织简介** | org/intro.md | 组织使命、愿景、业务范围 |
| **项目A** | projects/项目A/ | 项目A相关文档 |
| **项目B** | projects/项目B/ | 项目B相关文档 |
| **会议纪要** | org/meetings/ | 各类会议记录 |
| **制度流程** | org/policies/ | 内部制度、操作流程 |
| **成员档案** | org/members/ | 团队成员信息 |
| **方法论** | methods/ | 工作方法、工具使用 |
| **案例库** | cases/ | 实践案例 |
| **外部资源** | resources/ | 参考资料、行业报告 |
| **工作记录** | daily/ | 日常工作记录 |
| **归档** | archive/ | 过时但保留的文档 |

### 项目索引

#### 项目A
| 文件 | 说明 |
|------|------|
| projects/项目A/README.md | 项目概述 |
| projects/项目A/计划.md | 项目计划 |
| projects/项目A/进展.md | 进展追踪 |

#### 项目B
| 文件 | 说明 |
|------|------|
| projects/项目B/README.md | 项目概述 |

### 组织文档

| 文件 | 说明 |
|------|------|
| org/meetings/YYYY-MM-DD_会议主题.md | 会议纪要 |
| org/policies/XX制度.md | 制度文档 |

---

## 第2层：主题索引（按知识实体/主题）

> 每个主题提炼关键信息，方便快速复习，无需翻原始文件。

### 组织简介

- **全称**：[组织全称]
- **定位**：[一句话描述]
- **使命**：[使命陈述]
- **业务范围**：[主要业务]
- **关键文件**：`org/intro.md`

### 项目A

- **类型**：[项目类型]
- **状态**：进行中 / 已完成 / 暂停
- **负责人**：[姓名]
- **关键里程碑**：[列出]
- **关键文件**：`projects/项目A/README.md`

### [其他主题...]

- **主题名**：
- **关键信息**：
- **关键文件**：

---

## 第3层：受治理查询场景索引（GDT-KB 六要素 + 六约束）

> 每个高频查询场景写一份"受治理查询契约"，而非一行映射。闲聊/自由问题不写此层。详见 `references/three_layer_index.md` v1.1。

### 组织介绍类（示例）

```yaml
- scenario_id: kb.org.intro
  display_name: 组织基本介绍检索
  question_examples:
    - "我们组织是做什么的？"
    - "团队有谁？"
  source_scope: [org]
  mapping_table:
    - 组织简介 → org/intro.md
    - 团队成员 → org/members/
  query_spec:
    retrieve_within: source_scope
    must_cite: true
  compute_and_report:
    method: SAG 语义检索
    report_framework: 知识卡片（标题/出处/摘要）
  output_format: [引用文档原文, 知识卡片（带出处）]
  open_params: []
  locked_contract:
    label_synthesis: "AI 分析"
    version: v1.0.0
  fallback: BLOCKED
  status: PUBLISHED
```

### 项目查询类（示例）

```yaml
- scenario_id: kb.project.progress
  display_name: 项目进展检索
  question_examples:
    - "项目A进展如何？"
    - "项目A的计划是什么？"
  source_scope: [projects]
  mapping_table:
    - 进展 → projects/项目A/进展.md
    - 计划 → projects/项目A/计划.md
  query_spec:
    retrieve_within: source_scope
    must_cite: true
  compute_and_report:
    method: SAG 语义检索
    report_framework: 知识卡片
  output_format: [引用文档原文, 知识卡片]
  open_params: [项目名]
  locked_contract:
    label_synthesis: "AI 分析"
    version: v1.0.0
  fallback: BLOCKED
  status: PUBLISHED
```

> **双模式提示**：日常自由提问（"最近大家在忙啥"）走闲聊/自由模式，不写此层；只有 recurring、需准确/可审计的查询才固化为上方契约。

### 会议/制度类 / 方法工具类 / 历史归档类

> 同上格式，按需补充 `scenario_id` 与 `source_scope`。

---

## 上下文管理规则

| 场景 | 触发动作 |
|------|----------|
| 会话开始/任务开始 | 读取本索引 |
| 询问项目进展 | 查第2层(主题索引) → 项目子目录 |
| 询问具体信息 | 查第3层(提问场景索引) → 秒级定位 |
| 新增文档 | 更新第1层(目录索引) + 判断是否更新第2层 |
| 用户问"XX在哪" | 先过判定层：命中 GDT 触发场景 → 加载契约受治理检索；否则 → 闲聊/自由灵活检索 |

---

## 变更历史

| 时间 | 操作 | 条目 |
|------|------|------|
| YYYY-MM-DD | 初始化 | 首次创建索引 |

---

*此文件是知识库的核心入口，每次检索知识时优先查看*
