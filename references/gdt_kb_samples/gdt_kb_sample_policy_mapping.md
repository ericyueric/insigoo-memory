# GDT-KB 示范任务包 · 政策法规模应与本组织映射检索

> **用途**：GDT-KB 适配示范样本之一，用「受治理查询场景索引」六要素 schema 落地「某法规/政策对本组织的要求与制度映射」高频场景。
> **创建纪律**：遵循 `GDTcreater（未开源，本技能不依赖）` 六件套引擎，按 GDT-KB 语义映射落盘（见 `insigoo-memory` 2.5.4）。
> **对应标准**：`three_layer_index.md` v1.1 第 3 层 schema；`insigoo-memory` 2.4 契约。
> **双模式**：本任务包是**受治理（GDT 触发）**场景；闲聊/自由查询不加载本契约（见末尾双模式注解）。

---

## 0. 怎么用（给知识库管理员）

1. 复制下方 `contract` 块到 `knowledge_index.md` 第 3 层；
2. 把 `open_params`（法规/政策名称）替换成实际值；
3. 把 `mapping_table` 的占位路径换成你知识库里的真实法规台账/制度/映射节点；
4. 跑一次「验证证据」里的核对动作，确认命中正确，再把 `status` 置 `PUBLISHED`。

---

## 1. 受治理查询契约（契约本体 · 六要素 + 六约束）

```yaml
- scenario_id: kb.policy.mapping               # 命名：kb.<领域>.<动作>
  display_name: 政策法规模应与本组织映射检索
  version: v1.0.0                                 # 约束④ 版本不可覆盖（修订须升版）

  # ── 要素① 查询提示词（触发语，≥3 条自然语言）──
  question_examples:
    - "新出的 XX 法规对我们机构有什么影响"
    - "慈善法修订后我们要改哪些内部制度"
    - "查一下某政策对本组织的要求清单"
    - "XX 规定我们合规上要做到什么"

  # ── 要素② 数据源（受治理语料，锁定）──
  source_scope:                                  # 约束① 仅受治理语料
    - policy/registry                            # 法规台账
    - governance/policies                       # 本组织内部制度
    - compliance/mapping                        # 法规-制度映射
    - legal/opinion                             # 法律/合规意见

  # ── 要素③ 知识库/映射表（问题→文档节点，版本化）──
  mapping_table:
    - 法规台账       → policy/registry/<法规名>.md
    - 本组织制度     → governance/policies/<制度名>.md
    - 合规映射       → compliance/mapping/<法规名>_映射.md
    - 法律意见       → legal/opinion/<事项>.md

  # ── 要素④ 查询规范（检索口径，固化）──
  query_spec:
    retrieve_within: source_scope                # 约束② 锁定契约：检索范围不可运行时改
    must_cite: true                              # 约束③ 事实引用必带出处
    filter: "policy = open_params.法规"          # 仅检索该法规关联项
    sort_by: 相关度

  # ── 要素⑤ 计算规范 + 报告框架 ──
  compute_and_report:
    method: SAG 语义检索 + 法规与本组织制度映射 + 编译
    report_framework:
      - 法规要点（逐条，引源）
      - 对本组织要求清单（逐条：要求/对应现有制度/缺口）
      - 引用原文 + 关联链接
      - 末尾固定声明"非法律意见"

  # ── 要素⑥ 输出格式 ──
  output_format:
    - 法规原文引用（带出处链接）
    - 要求清单（表格：要求/对应制度/缺口）
    - AI 解读.md（独立文件，标注"AI 分析" + 声明"非法律意见"）

  # ── 用户运行期可填项（不改检索逻辑）──
  open_params:
    - 法规/政策名称

  # ── 约束② 锁定契约（构建期固化，运行期不可改）──
  locked_contract:
    label_synthesis: "AI 分析"                   # 约束③ AI 解读独立标注
    cannot_override_at_runtime: true
    regulation_cite_required: true              # 场景红线：法规解读须引源，不自行编纂/改写法条
    no_self_compliance_conclusion: true          # 场景红线：不自行下"合规/不合规"结论，仅呈现要求与现有制度对照
    ai_disclaimer: "本分析非法律意见"            # 场景红线：AI 解读须声明非法律意见

  fallback: BLOCKED                              # 约束⑤ 无命中不编造
  status: PUBLISHED                              # 约束⑥ 触发只路由不执行
```

---

## 2. 六要素逐项说明（便于改编）

| 要素 | 本包取值 | 改编时怎么填 |
|------|---------|-------------|
| ① 查询提示词 | `question_examples` 4 条 | 写组织里**真实被高频问到**的口语化问法，≥3 条 |
| ② 数据源 | `source_scope` 4 类 | 对齐你知识库的法规台账/制度/映射/法律意见目录 |
| ③ 知识库/映射表 | `mapping_table` | 问题意图 → 具体文档节点路径，路径要**真实存在** |
| ④ 查询规范 | `query_spec` | 检索范围 + policy 过滤 + 强制引用；属锁定契约 |
| ⑤ 计算规范+报告框架 | `compute_and_report` | SAG 检索 + 法规-制度映射 + 要求清单结构 |
| ⑥ 输出格式 | `output_format` | 原文引用/要求清单/独立 AI 解读(含免责声明)，三者分离 |

---

## 3. 填参示例（让样本"可运行"）

把 `open_params` 代入：`法规/政策名称 = 慈善法（2023 修订）`：

- `query_spec.filter` 解析为 `policy = 慈善法（2023 修订）`；
- `mapping_table` 解析为：
  - `policy/registry/慈善法（2023 修订）.md`
  - `governance/policies/<相关制度名>.md`
  - `compliance/mapping/慈善法（2023 修订）_映射.md`
  - `legal/opinion/<事项>.md`
- 命中任一 `question_examples` 语义 → 加载本契约 → 仅在受治理语料内检索 → 必带法规出处 → 无命中答 BLOCKED。

---

## 4. 验证证据（GDTcreater（未开源，本技能不依赖） 第六件套 · 核对方式）

- **动作**：用 SAG 检索 API 验证——`curl -X POST http://127.0.0.1:4173/search -d '{"query":"慈善法修订后我们要改哪些内部制度","top_k":5}'` 跑一次；
- **预期**：返回结果**全部**带法规原文出处，且**不出现** AI 自行编纂的法条或对组织合规状态的定性结论；
- **反例（应被拦截）**：若输出出现"你们目前不合规""根据本法第X条（AI 改写版）"等自判/自纂表述，说明 `no_self_compliance_conclusion` / `regulation_cite_required` 红线未生效，须回查契约；
- **人工抽检**：抽 1 部法规，对照真实法条与法律意见，确认要求清单准确、缺口标注到位、免责声明存在。
- **记录**：验证人与日期写入本包 `status: PUBLISHED` 旁注。

---

## 5. 双模式注解（什么时候用本契约，什么时候不用）

| 用户问法 | 模式 | 反应 |
|---------|------|------|
| "慈善法修订后我们要改哪些内部制度" | **GDT 触发**（命中 `question_examples`）| 加载本契约，policy 过滤+受治理检索、必带法规出处、无命中 BLOCKED |
| "最近公益行业监管是不是更严了"（泛泛而谈）| **闲聊/自由** | 不加载契约，SAG 灵活检索、不强制引用、不作合规判断 |
| "我们这样操作合不合规"（触及合规定性）| 闲聊中检测到信号 → **主动提示升级** | "合规定性须由法律/合规负责人出具，我可以按受治理契约整理法规要求与现有制度对照供你参考（非法律意见），可以吗？"确认后切 GDT 触发 |

> 一句话：本契约**只在 GDT 触发模式加载**；政策场景的命门是**法规须引源 + AI 不下合规结论**——AI 只做"要求-制度"对照，定性的合规判断必须转交人。

---

*本示范包是 GDT-KB 适配样本集之一；同类场景（项目披露/受益群体/财务/合规/治理/风险/人事/合作/传播）按同 schema 复制即可。*
