# GDT-KB 示范任务包 · 某受益群体全部评估记录检索

> **用途**：`insigoo-memory`（GDT-KB 适配）的第二个**可运行示范任务包**，展示如何把"按受益群体维系的评估资料"用「受治理查询场景索引」六要素 schema 固化成一个可复用查询契约。
> **创建纪律**：遵循 `GDTcreater（未开源，本技能不依赖）` 六件套引擎（任务元数据→查询规范→映射证据→受控执行包→产物契约→验证证据），按 GDT-KB 语义映射落盘（见 `insigoo-memory` 2.5.4）。
> **对应标准**：`three_layer_index.md` v1.1 第 3 层 schema；`insigoo-memory` 2.4 契约。
> **双模式**：本任务包是**受治理（GDT 触发）**场景；闲聊/自由查询不加载本契约（见末尾双模式注解）。
> **系列位置**：与 `gdt_kb_sample_project_full_disclosure.md`（项目全周期披露）、`gdt_kb_sample_finance_year_disclosure.md`（年度财务披露）同属 GDT-KB 示范包集。

---

## 0. 怎么用（给知识库管理员）

1. 复制下方 `contract` 块到 `knowledge_index.md` 第 3 层；
2. 把 `open_params`（受益群体 / 评估周期）替换成实际值；
3. 把 `mapping_table` 的占位路径换成你知识库里的真实文档节点；
4. 跑一次「验证证据」里的核对动作，确认命中正确，再把 `status` 置 `PUBLISHED`。

---

## 1. 受治理查询契约（契约本体 · 六要素 + 六约束）

```yaml
- scenario_id: kb.beneficiary.evaluation-record   # 命名：kb.<领域>.<动作>
  display_name: 某受益群体全部评估记录检索
  version: v1.0.0                                  # 约束④ 版本不可覆盖（修订须升版）

  # ── 要素① 查询提示词（触发语，≥3 条自然语言）──
  question_examples:
    - "把 XX 受益群体做过的所有评估都调出来"
    - "我们针对留守儿童的测评和回访记录有哪些"
    - "XX 群体的基线、中期、终期评估都在哪"
    - "我想看某社区老人的满意度反馈汇总"

  # ── 要素② 数据源（受治理语料，锁定）──
  source_scope:                                   # 约束① 仅受治理语料
    - beneficiary_profile   # 受益群体画像/建档
    - baseline_survey       # 基线调查
    - mid_eval              # 中期评估
    - final_eval            # 终期评估
    - satisfaction          # 满意度/反馈回访

  # ── 要素③ 知识库/映射表（问题→文档节点，版本化）──
  mapping_table:
    - 群体画像建档   → beneficiary/<群体>/画像建档.md
    - 基线调查数据   → baseline_survey/<群体>/<周期>_基线.md
    - 中期评估       → evaluation/<群体>/中期评估.md
    - 终期评估       → evaluation/<群体>/终期评估.md
    - 满意度反馈     → satisfaction/<群体>/<周期>_满意度.md

  # ── 要素④ 查询规范（检索口径，固化）──
  query_spec:
    retrieve_within: source_scope                 # 约束② 锁定契约：检索范围不可运行时改
    must_cite: true                               # 约束③ 事实引用必带出处
    sort_by: 评估阶段升序                          # 基线→中期→终期→满意度，按项目周期线呈现

  # ── 要素⑤ 计算规范 + 报告框架 ──
  compute_and_report:
    method: SAG 语义检索 + 编译                    # 不自由改写口径
    report_framework:                             # 知识卡片结构
      - 群体概览（群体类别/覆盖人数/建档时间）
      - 评估时间线（基线→中期→终期→满意度）
      - 每节点：出处文档 + 原文摘要 + 关键指标 + 关联链接
      - 指标口径标注（如"满意度"定义与样本量，避免跨群体误比）
      - 缺失节点标记（如某群体无终期评估 → 显式标"未提供"）

  # ── 要素⑥ 输出格式 ──
  output_format:
    - 引用评估文档原文（带出处链接）
    - 知识卡片（标题/出处/摘要/关键指标/关联）
    - AI 解读.md（独立文件，标注"AI 分析"，与事实分离）

  # ── 用户运行期可填项（不改检索逻辑）──
  open_params:
    - 受益群体
    - 评估周期

  # ── 约束② 锁定契约（构建期固化，运行期不可改）──
  locked_contract:
    label_synthesis: "AI 分析"                    # 约束③ AI 解读独立标注
    cannot_override_at_runtime: true
    cross_group_compare_forbidden: true           # 附加锁定：禁止跨不同群体直接横向比较（口径不同）

  fallback: BLOCKED                               # 约束⑤ 无命中不编造，答"未找到，转人工/建议补充"
  status: PUBLISHED                               # 约束⑥ 触发只路由不执行（索引层只定位，检索走本契约）
```

---

## 2. 六要素逐项说明（便于改编）

| 要素 | 本包取值 | 改编时怎么填 |
|------|---------|-------------|
| ① 查询提示词 | `question_examples` 4 条 | 写组织里**真实被高频问到**的口语化问法，≥3 条；突出"群体 + 评估"组合 |
| ② 数据源 | `source_scope` 5 类 | 对齐你知识库里"按群体维度"真实归类的评估资料（画像/基线/中终期/满意度）|
| ③ 知识库/映射表 | `mapping_table` | 群体意图 → 具体文档节点路径，路径要**真实存在**；注意群体命名一致性 |
| ④ 查询规范 | `query_spec` | 检索范围 + 是否强制引用 + 排序（按评估阶段）；属锁定契约 |
| ⑤ 计算规范+报告框架 | `compute_and_report` | SAG 检索方法 + 报告该长什么样（卡片结构 + 指标口径标注）|
| ⑥ 输出格式 | `output_format` | 产物形态：原文/卡片/独立 AI 解读，三者分离 |

> **特别守护**：受益群体评估常涉及**跨群体横向比较**（"哪个群体成效更好"）。本包在 `locked_contract` 显式加 `cross_group_compare_forbidden: true`——因为不同群体基线、样本量、指标定义不同，强行合并比较会失真。这是 GDT 约束②（锁定契约）在知识场景的具体化。

---

## 3. 填参示例（让样本"可运行"）

把 `open_params` 代入：`受益群体 = 留守儿童`，`评估周期 = 2024-2025`：

- `mapping_table` 解析为：
  - `beneficiary/留守儿童/画像建档.md`
  - `baseline_survey/留守儿童/2024-2025_基线.md`
  - `evaluation/留守儿童/中期评估.md`
  - `evaluation/留守儿童/终期评估.md`
  - `satisfaction/留守儿童/2024-2025_满意度.md`
- 命中任一 `question_examples` 语义 → 加载本契约 → 仅在上述 5 类受治理语料内检索 → 必带出处 → 无命中答 BLOCKED。
- 若用户追问"留守儿童和随迁子女哪个改善更大" → 触发 `cross_group_compare_forbidden`，agent 应回复"两类群体基线/口径不同，无法直接横比，建议分别出具评估报告"。

---

## 4. 验证证据（GDTcreater（未开源，本技能不依赖） 第六件套 · 核对方式）

- **动作**：用 SAG 检索 API 验证——`curl -X POST http://127.0.0.1:4173/search -d '{"query":"留守儿童 从基线到终期的所有评估记录","top_k":5}'` 跑一次；
- **预期**：返回结果**全部**落在 `beneficiary_profile/baseline_survey/evaluation/satisfaction` 四类路径内，且每条带文件出处；
- **反例（应被拦截）**：若返回了 `org/内部讨论.md` 或未编入索引的草稿，说明 `source_scope` 未生效，需回查契约；
- **口径核对**：抽检 1 个群体，确认"满意度"指标的定义、样本量在原文中有据，且 AI 解读未把不同群体的满意度直接横向排名；
- **人工抽检**：随机抽 1 个群体，对照其真实文件夹，确认契约 `mapping_table` 路径与实际一致、无断链。
- **记录**：验证人与日期写入本包 `status: PUBLISHED` 旁注。

---

## 5. 双模式注解（什么时候用本契约，什么时候不用）

| 用户问法 | 模式 | 反应 |
|---------|------|------|
| "把留守儿童做过的所有评估都调出来" | **GDT 触发**（命中 `question_examples`）| 加载本契约，`source_scope` 受治理检索、必带出处、无命中 BLOCKED |
| "你觉得我们项目对孩子们帮助大吗？随便聊聊" | **闲聊/自由** | 不加载契约，SAG 灵活检索、可综合、不强制引用，不当作正式评估结论 |
| "这两个群体的成效能不能比一下？"（触及跨群体比较）| 闲聊中检测到信号 → **主动提示升级** | "不同群体基线/口径不同，我按受治理契约分群体出具报告、不做直接横比，可以吗？"确认后切 GDT 触发 |

> 一句话：本契约**只在 GDT 触发模式加载**；闲聊靠 SAG 兜底事实、靠 agent 灵活应变。两者共用 SAG，差异只在"是否加载 `locked_contract`"；本包额外在 `locked_contract` 中锁定"禁止跨群体横比"这一知识场景专属红线。

---

*本示范包是 GDT-KB 适配的第二个样本；与"项目全周期披露""年度财务披露"同属示范包集，按同 schema 复制改编即可。*
