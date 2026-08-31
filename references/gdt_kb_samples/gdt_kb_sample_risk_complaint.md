# GDT-KB 示范任务包 · 风险/投诉/舆情记录检索

> **用途**：GDT-KB 适配示范样本之一，用「受治理查询场景索引」六要素 schema 落地「投诉/危机/负面舆情记录检索」高频且高敏场景。
> **创建纪律**：遵循 `GDTcreater` 六件套引擎，按 GDT-KB 语义映射落盘（见 `insigoo-memory` 2.5.4）。
> **对应标准**：`three_layer_index.md` v1.1 第 3 层 schema；`insigoo-memory` 2.4 契约。
> **双模式**：本任务包是**受治理（GDT 触发）**场景；本场景**最该强制走 GDT 触发**——即便以闲聊口吻问到具体风险/投诉，也必须升级并脱敏（见末尾双模式注解）。

---

## 0. 怎么用（给知识库管理员）

1. 复制下方 `contract` 块到 `knowledge_index.md` 第 3 层；
2. 把 `mapping_table` 的占位路径换成你知识库里的真实风险/投诉节点；
3. 跑一次「验证证据」里的核对动作，确认命中正确，再把 `status` 置 `PUBLISHED`。

---

## 1. 受治理查询契约（契约本体 · 六要素 + 六约束）

```yaml
- scenario_id: kb.risk.record                  # 命名：kb.<领域>.<动作>
  display_name: 风险/投诉/舆情记录检索
  version: v1.0.0                                 # 约束④ 版本不可覆盖（修订须升版）

  # ── 要素① 查询提示词（触发语，≥3 条自然语言）──
  question_examples:
    - "查一下某项目的投诉记录"
    - "上次那个舆情危机的处理文档在哪"
    - "把今年的风险事件台账调出来"
    - "某受益人的投诉处理到哪一步了"

  # ── 要素② 数据源（受治理语料，锁定；标记 confidential）──
  source_scope:                                  # 约束① 仅受治理语料
    - risk/complaints                           # 投诉记录（标记 PII/confidential）
    - risk/crisis                               # 危机事件（标记 confidential）
    - risk/reputation                           # 舆情/声誉（标记 confidential）
    - risk/register                             # 风险台账

  # ── 要素③ 知识库/映射表（问题→文档节点，版本化）──
  mapping_table:
    - 投诉记录     → risk/complaints/<项目>/<日期>_投诉.md（confidential）
    - 危机事件     → risk/crisis/<事件名>_处理.md（confidential）
    - 舆情记录     → risk/reputation/<日期>_舆情.md（confidential）
    - 风险台账     → risk/register/<年份>_风险台账.md

  # ── 要素④ 查询规范（检索口径，固化）──
  query_spec:
    retrieve_within: source_scope                # 约束② 锁定契约：检索范围不可运行时改
    must_cite: true                              # 约束③ 事实引用必带出处
    confidentiality_check: true                  # 命中即走权限/脱敏校验

  # ── 要素⑤ 计算规范 + 报告框架 ──
  compute_and_report:
    method: SAG 语义检索 + 权限/脱敏校验
    report_framework:
      - 命中记录清单（类型/日期/状态/出处）
      - 每项：脱敏后摘要 + 出处链接 + 处理状态
      - 未公开/涉密项显式标 confidential，不得进入对外产物

  # ── 要素⑥ 输出格式 ──
  output_format:
    - 引用记录原文（脱敏后，带出处链接）
    - 风险记录清单（标注 confidential 与处理状态）
    - AI 解读.md（独立文件，标注"AI 分析"，与事实分离）

  # ── 用户运行期可填项（不改检索逻辑）──
  open_params: []                                # 本场景无运行期参数，纯路由（权限上下文由会话提供）

  # ── 约束② 锁定契约（构建期固化，运行期不可改）──
  locked_contract:
    label_synthesis: "AI 分析"                   # 约束③ AI 解读独立标注
    cannot_override_at_runtime: true
    confidential_no_external: true               # 场景红线：未公开/涉密风险记录禁外泄、禁用于非授权场景
    pii_mask: true                               # 场景红线：投诉/舆情中的个人信息（姓名/联系方式）须脱敏

  fallback: BLOCKED                              # 约束⑤ 无命中不编造
  status: PUBLISHED                              # 约束⑥ 触发只路由不执行
```

---

## 2. 六要素逐项说明（便于改编）

| 要素 | 本包取值 | 改编时怎么填 |
|------|---------|-------------|
| ① 查询提示词 | `question_examples` 4 条 | 写组织里**真实被高频问到**的口语化问法，≥3 条 |
| ② 数据源 | `source_scope` 4 类（均标记 confidential）| 对齐你知识库的风险/投诉/舆情/台账目录 |
| ③ 知识库/映射表 | `mapping_table` | 问题意图 → 具体文档节点路径，路径要**真实存在** |
| ④ 查询规范 | `query_spec` | 检索范围 + 强制引用 + 保密校验；属锁定契约 |
| ⑤ 计算规范+报告框架 | `compute_and_report` | SAG 检索 + 脱敏 + 状态标注 |
| ⑥ 输出格式 | `output_format` | 脱敏摘录/清单/独立 AI 解读，三者分离 |

---

## 3. 填参示例（让样本"可运行"）

- `mapping_table` 解析为：
  - `risk/complaints/河流守望者计划/2025-03-12_投诉.md`（confidential）
  - `risk/crisis/2024_舆情事件_处理.md`（confidential）
  - `risk/reputation/2025-01-20_舆情.md`（confidential）
  - `risk/register/2025_风险台账.md`
- 命中任一 `question_examples` 语义 → 加载本契约 → 仅在上述受治理语料内检索 → **脱敏后**呈现 → 无命中答 BLOCKED。
- 若命中未公开记录且会话无权限 → 不返回内容，提示"该记录受限，请联系风险负责人"。

---

## 4. 验证证据（GDTcreater 第六件套 · 核对方式）

- **动作**：用 `rag_helper.py --query "河流守望者计划 投诉记录"` 跑一次；
- **预期**：返回结果**全部**落在 `risk/*` 路径内，且**个人信息已脱敏**、带 confidential 标注与出处；
- **反例（应被拦截）**：若返回了投诉人真实姓名/电话，或把涉密危机记录直接进了对外摘要，说明 `pii_mask` / `confidential_no_external` 红线未生效，须回查契约；
- **人工抽检**：抽 1 条投诉记录，对照真实文件，确认脱敏与权限校验生效、无外泄。
- **记录**：验证人与日期写入本包 `status: PUBLISHED` 旁注。

---

## 5. 双模式注解（什么时候用本契约，什么时候不用）

| 用户问法 | 模式 | 反应 |
|---------|------|------|
| "把今年的风险事件台账调出来"（授权内）| **GDT 触发**（命中 `question_examples`）| 加载本契约，受治理检索、脱敏、必带出处、无命中 BLOCKED |
| "咱上次那事儿后来咋样了"（闲聊口吻问具体风险）| **检测到敏感信号 → 强制升级** | 即便闲聊口吻，也切 GDT 触发 + 脱敏，不按自由模式随意答 |
| "把那个投诉人的电话发我"（无权限/对外）| 命中红线 → **拒绝并提示** | "该记录涉密且含个人信息，我无法提供；请联系风险负责人。" |

> 一句话：本契约**最该强制走 GDT 触发**——风险/投诉/舆情天然高敏，闲聊兜底不适用；**脱敏与权限校验是硬底线，闲聊口吻也不能绕过**。

---

*本示范包是 GDT-KB 适配样本集之一；同类场景（项目披露/受益群体/财务/合规/捐赠方/治理/人事）按同 schema 复制即可。*
