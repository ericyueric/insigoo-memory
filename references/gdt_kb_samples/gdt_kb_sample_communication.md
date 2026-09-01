# GDT-KB 示范任务包 · 传播素材与对外口径检索

> **用途**：GDT-KB 适配示范样本之一，用「受治理查询场景索引」六要素 schema 落地「某主题对外口径/新闻稿/品牌素材检索」高频场景。
> **创建纪律**：遵循 `GDTcreater（未开源，本技能不依赖）` 六件套引擎，按 GDT-KB 语义映射落盘（见 `insigoo-memory` 2.5.4）。
> **对应标准**：`three_layer_index.md` v1.1 第 3 层 schema；`insigoo-memory` 2.4 契约。
> **双模式**：本任务包是**受治理（GDT 触发）**场景；闲聊/自由查询不加载本契约（见末尾双模式注解）。

---

## 0. 怎么用（给知识库管理员）

1. 复制下方 `contract` 块到 `knowledge_index.md` 第 3 层；
2. 把 `open_params`（主题/事项）替换成实际值；
3. 把 `mapping_table` 的占位路径换成你知识库里的真实传播/媒体节点；
4. 跑一次「验证证据」里的核对动作，确认命中正确，再把 `status` 置 `PUBLISHED`。

---

## 1. 受治理查询契约（契约本体 · 六要素 + 六约束）

```yaml
- scenario_id: kb.communication.assets          # 命名：kb.<领域>.<动作>
  display_name: 传播素材与对外口径检索
  version: v1.0.0                                 # 约束④ 版本不可覆盖（修订须升版）

  # ── 要素① 查询提示词（触发语，≥3 条自然语言）──
  question_examples:
    - "我们对外怎么介绍 XX 项目的"
    - "查一下品牌对外说法/口径文档"
    - "某活动的新闻稿模板在哪"
    - "给媒体用的机构简介是哪个版本"

  # ── 要素② 数据源（受治理语料，锁定）──
  source_scope:                                  # 约束① 仅受治理语料
    - communication/press                       # 新闻稿
    - communication/brand                       # 品牌素材
    - communication/approved-statements         # 审批对外口径
    - media/assets                              # 媒体可用素材

  # ── 要素③ 知识库/映射表（问题→文档节点，版本化）──
  mapping_table:
    - 新闻稿       → communication/press/<事项>_新闻稿.md
    - 品牌素材     → communication/brand/<素材名>.md
    - 审批口径     → communication/approved-statements/<主题>_口径.md
    - 媒体素材     → media/assets/<素材名>

  # ── 要素④ 查询规范（检索口径，固化）──
  query_spec:
    retrieve_within: source_scope                # 约束② 锁定契约：检索范围不可运行时改
    must_cite: true                              # 约束③ 事实引用必带出处
    filter: "approved_only = true for external use"  # 对外使用仅取审批版
    sort_by: 时间降序（取最新审批版）

  # ── 要素⑤ 计算规范 + 报告框架 ──
  compute_and_report:
    method: SAG 语义检索 + 仅取审批版 + 编译
    report_framework:
      - 对外口径清单（主题/版本/审批状态）
      - 引用审批版原文 + 关联链接
      - 固定标注"对外发布须用审批版口径"

  # ── 要素⑥ 输出格式 ──
  output_format:
    - 审批版原文引用（带出处链接 + 版本号）
    - 对外口径清单（表格：主题/版本/审批状态）
    - AI 解读.md（独立文件，标注"AI 分析"）

  # ── 用户运行期可填项（不改检索逻辑）──
  open_params:
    - 主题/事项

  # ── 约束② 锁定契约（构建期固化，运行期不可改）──
  locked_contract:
    label_synthesis: "AI 分析"                   # 约束③ AI 解读独立标注
    cannot_override_at_runtime: true
    external_use_approved_only: true             # 场景红线：对外发布/媒体使用必须走审批版口径，未审批草稿不得作为对外口径
    version_latest_approved: true                # 场景红线：取最新审批版，不用过期/被撤销版本

  fallback: BLOCKED                              # 约束⑤ 无命中不编造
  status: PUBLISHED                              # 约束⑥ 触发只路由不执行
```

---

## 2. 六要素逐项说明（便于改编）

| 要素 | 本包取值 | 改编时怎么填 |
|------|---------|-------------|
| ① 查询提示词 | `question_examples` 4 条 | 写组织里**真实被高频问到**的口语化问法，≥3 条 |
| ② 数据源 | `source_scope` 4 类 | 对齐你知识库的新闻稿/品牌/审批口径/媒体素材目录 |
| ③ 知识库/映射表 | `mapping_table` | 问题意图 → 具体文档节点路径，路径要**真实存在** |
| ④ 查询规范 | `query_spec` | 检索范围 + 审批版过滤 + 强制引用；属锁定契约 |
| ⑤ 计算规范+报告框架 | `compute_and_report` | SAG 检索 + 审批版过滤 + 口径清单结构 |
| ⑥ 输出格式 | `output_format` | 审批版原文/口径清单/独立 AI 解读，三者分离 |

---

## 3. 填参示例（让样本"可运行"）

把 `open_params` 代入：`主题/事项 = 示例项目`：

- `query_spec.filter` 解析为 `approved_only = true`（对外使用仅取审批版）；
- `mapping_table` 解析为：
  - `communication/press/示例项目_新闻稿.md`
  - `communication/brand/示例项目_品牌素材.md`
  - `communication/approved-statements/示例项目_口径.md`
  - `media/assets/示例项目_素材`
- 命中任一 `question_examples` 语义 → 加载本契约 → 仅取审批版受治理语料 → 必带版本出处 → 无命中答 BLOCKED。

---

## 4. 验证证据（GDTcreater（未开源，本技能不依赖） 第六件套 · 核对方式）

- **动作**：用 SAG 检索 API 验证——`curl -X POST http://127.0.0.1:4173/search -d '{"query":"我们对外怎么介绍示例项目的","top_k":5}'` 跑一次；
- **预期**：返回结果**全部**为审批版（`approved_only = true`），带版本号与出处，且**不出现**未审批草稿内容；
- **反例（应被拦截）**：若返回了草稿/过期版/被撤销版本的口径，或对外口径与审批版不一致，说明 `external_use_approved_only` / `version_latest_approved` 红线未生效，须回查契约；
- **人工抽检**：抽 1 个主题，对照审批记录，确认引用的是最新审批版、无过期口径混入。
- **记录**：验证人与日期写入本包 `status: PUBLISHED` 旁注。

---

## 5. 双模式注解（什么时候用本契约，什么时候不用）

| 用户问法 | 模式 | 反应 |
|---------|------|------|
| "查一下示例项目对外口径文档" | **GDT 触发**（命中 `question_examples`）| 加载本契约，审批版过滤+受治理检索、必带版本出处、无命中 BLOCKED |
| "我们项目一般怎么对外讲的"（内部探讨）| **闲聊/自由** | 不加载契约，SAG 灵活检索、不强制引用、不作对外口径 |
| "帮我把这个写成对外发的稿子"（触及对外发布）| 闲聊中检测到信号 → **主动提示升级** | "对外发布须用审批版口径，我按受治理契约只取审批版、不用草稿，可以吗？"确认后切 GDT 触发 |

> 一句话：本契约**只在 GDT 触发模式加载**；传播场景的命门是**对外必须走审批版**——未审批草稿、过期版、被撤销版都不得作为对外口径，即便以闲聊口吻问起草稿也须主动升级。

---

*本示范包是 GDT-KB 适配样本集之一；同类场景（项目披露/受益群体/财务/合规/治理/风险/人事/政策/合作）按同 schema 复制即可。*
