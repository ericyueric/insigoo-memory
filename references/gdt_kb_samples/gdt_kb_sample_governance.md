# GDT-KB 示范任务包 · 治理与内部制度文件检索

> **用途**：GDT-KB 适配示范样本之一，用「受治理查询场景索引」六要素 schema 落地「章程/理事会决议/内部制度检索」高频场景。
> **创建纪律**：遵循 `GDTcreater（未开源，本技能不依赖）` 六件套引擎，按 GDT-KB 语义映射落盘（见 `insigoo-memory` 2.5.4）。
> **对应标准**：`three_layer_index.md` v1.1 第 3 层 schema；`insigoo-memory` 2.4 契约。
> **双模式**：本任务包是**受治理（GDT 触发）**场景；闲聊/自由查询不加载本契约（见末尾双模式注解）。

---

## 0. 怎么用（给知识库管理员）

1. 复制下方 `contract` 块到 `knowledge_index.md` 第 3 层；
2. 把 `mapping_table` 的占位路径换成你知识库里的真实治理/制度节点；
3. 跑一次「验证证据」里的核对动作，确认命中正确，再把 `status` 置 `PUBLISHED`。

---

## 1. 受治理查询契约（契约本体 · 六要素 + 六约束）

```yaml
- scenario_id: kb.governance.doc                 # 命名：kb.<领域>.<动作>
  display_name: 治理与内部制度文件检索
  version: v1.0.0                                 # 约束④ 版本不可覆盖（修订须升版）

  # ── 要素① 查询提示词（触发语，≥3 条自然语言）──
  question_examples:
    - "我们章程里是怎么规定理事会的"
    - "把内部财务审批制度找出来"
    - "理事会最近一次决议原文在哪"
    - "组织的治理结构和议事规则文档"

  # ── 要素② 数据源（受治理语料，锁定）──
  source_scope:                                  # 约束① 仅受治理语料
    - org/charter                               # 章程
    - org/governance/council                    # 理事会决议
    - org/policies                              # 内部制度/SOP
    - org/structure                             # 治理结构

  # ── 要素③ 知识库/映射表（问题→文档节点，版本化）──
  mapping_table:
    - 章程           → org/charter.md（标注生效版本）
    - 理事会决议     → org/governance/council/<日期>_决议.md
    - 内部制度       → org/policies/<制度名>.md（标注 status）
    - 治理结构       → org/structure/治理架构.md

  # ── 要素④ 查询规范（检索口径，固化）──
  query_spec:
    retrieve_within: source_scope                # 约束② 锁定契约：检索范围不可运行时改
    must_cite: true                             # 约束③ 事实引用必带出处（原文引用）
    prefer_original: true                        # 优先返回制度/决议原文，不返回二手摘要

  # ── 要素⑤ 计算规范 + 报告框架 ──
  compute_and_report:
    method: SAG 语义检索 + 原文定位
    report_framework:
      - 命中制度/决议清单（名称/版本/生效状态/出处）
      - 每项：原文摘录 + 出处链接 + 关联条款
      - 失效/未生效制度显式标注 status，不与现行版混用

  # ── 要素⑥ 输出格式 ──
  output_format:
    - 引用制度/决议原文（带出处链接与条款号）
    - 治理文件清单（标注版本与 status）
    - AI 解读.md（独立文件，标注"AI 分析"，与原文分离）

  # ── 用户运行期可填项（不改检索逻辑）──
  open_params: []                                # 本场景无运行期参数，纯路由

  # ── 约束② 锁定契约（构建期固化，运行期不可改）──
  locked_contract:
    label_synthesis: "AI 分析"                   # 约束③ AI 解读独立标注
    cannot_override_at_runtime: true
    governance_no_rewrite: true                  # 场景红线：章程/决议/制度不得由 AI 改写或"概括"成失真摘要，须原文引用
    doc_status_label: true                       # 场景红线：失效/未生效文件须标 status，不得当作现行有效呈现

  fallback: BLOCKED                              # 约束⑤ 无命中不编造
  status: PUBLISHED                              # 约束⑥ 触发只路由不执行
```

---

## 2. 六要素逐项说明（便于改编）

| 要素 | 本包取值 | 改编时怎么填 |
|------|---------|-------------|
| ① 查询提示词 | `question_examples` 4 条 | 写组织里**真实被高频问到**的口语化问法，≥3 条 |
| ② 数据源 | `source_scope` 4 类 | 对齐你知识库的章程/理事会/制度/结构目录 |
| ③ 知识库/映射表 | `mapping_table` | 问题意图 → 具体文档节点路径，路径要**真实存在** |
| ④ 查询规范 | `query_spec` | 检索范围 + 强制原文引用；属锁定契约 |
| ⑤ 计算规范+报告框架 | `compute_and_report` | SAG 检索 + 原文定位 + 版本/status 标注 |
| ⑥ 输出格式 | `output_format` | 原文摘录/清单/独立 AI 解读，三者分离 |

---

## 3. 填参示例（让样本"可运行"）

- `mapping_table` 解析为：
  - `org/charter.md`（v3 生效版）
  - `org/governance/council/2025-06-15_决议.md`
  - `org/policies/财务审批制度.md`（status: 现行）
  - `org/structure/治理架构.md`
- 命中任一 `question_examples` 语义 → 加载本契约 → 仅在治理类受治理语料内检索 → **返回原文+出处** → 无命中答 BLOCKED。
- 若查到旧版制度（status: 失效）→ 显式标"失效，现行见 vX"，不混入有效呈现。

---

## 4. 验证证据（GDTcreater（未开源，本技能不依赖） 第六件套 · 核对方式）

- **动作**：用 `rag_helper.py --query "理事会决议里怎么定财务审批权限"` 跑一次；
- **预期**：返回结果**全部**落在 `org/charter`、`org/governance/council`、`org/policies`、`org/structure` 路径内，且**带原文摘录与出处**；
- **反例（应被拦截）**：若返回"按惯例应该是理事长批"（无原文依据），说明 `governance_no_rewrite` 红线未生效，须回查契约；
- **人工抽检**：抽 1 份制度，对照真实文件版本与 status，确认契约路径与实际一致、未混入失效版。
- **记录**：验证人与日期写入本包 `status: PUBLISHED` 旁注。

---

## 5. 双模式注解（什么时候用本契约，什么时候不用）

| 用户问法 | 模式 | 反应 |
|---------|------|------|
| "把内部财务审批制度找出来" | **GDT 触发**（命中 `question_examples`）| 加载本契约，受治理检索、原文引用、必带出处、无命中 BLOCKED |
| "咱们决策一般谁拍板呀？"（泛泛了解）| **闲聊/自由** | 不加载契约，SAG 灵活检索、不强制引用原文 |
| "章程说我们能这么干吗"（触及合规依据）| 闲聊中检测到信号 → **主动提示升级** | "这涉及章程依据，我按受治理契约给你原文+条款，不自行解读，可以吗？"确认后切 GDT 触发 |

> 一句话：本契约**只在 GDT 触发模式加载**；治理文件**必须原文引用、不得由 AI 改写失真**——这是组织合法性与内部信任的基石。

---

*本示范包是 GDT-KB 适配样本集之一；同类场景（项目披露/受益群体/财务/合规/捐赠方/风险/人事）按同 schema 复制即可。*
