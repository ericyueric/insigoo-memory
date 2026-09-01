# GDT-KB 示范任务包 · 年度合规/年检材料检索

> **用途**：GDT-KB 适配示范样本之一，用「受治理查询场景索引」六要素 schema 落地「某年度合规/年检材料检索」高频场景。
> **创建纪律**：遵循 `GDTcreater（未开源，本技能不依赖）` 六件套引擎，按 GDT-KB 语义映射落盘（见 `insigoo-memory` 2.5.4）。
> **对应标准**：`three_layer_index.md` v1.1 第 3 层 schema；`insigoo-memory` 2.4 契约。
> **双模式**：本任务包是**受治理（GDT 触发）**场景；闲聊/自由查询不加载本契约（见末尾双模式注解）。

---

## 0. 怎么用（给知识库管理员）

1. 复制下方 `contract` 块到 `knowledge_index.md` 第 3 层；
2. 把 `open_params`（年份）替换成实际值；
3. 把 `mapping_table` 的占位路径换成你知识库里的真实合规文档节点；
4. 跑一次「验证证据」里的核对动作，确认命中正确，再把 `status` 置 `PUBLISHED`。

---

## 1. 受治理查询契约（契约本体 · 六要素 + 六约束）

```yaml
- scenario_id: kb.compliance.year               # 命名：kb.<领域>.<动作>
  display_name: 年度合规/年检材料检索
  version: v1.0.0                                 # 约束④ 版本不可覆盖（修订须升版）

  # ── 要素① 查询提示词（触发语，≥3 条自然语言）──
  question_examples:
    - "我们去年的年检材料在哪"
    - "把 2025 年所有合规和审计报告归集一下"
    - "慈善组织年度报告和免税资格认定文件找出来"
    - "查一下今年监管要求的材料齐不齐"

  # ── 要素② 数据源（受治理语料，锁定）──
  source_scope:                                  # 约束① 仅受治理语料
    - governance/compliance                      # 年检/合规申报
    - finance/audit                              # 审计/财报
    - reports/annual                            # 年度报告
    - governance/qualification                  # 免税/认定资格

  # ── 要素③ 知识库/映射表（问题→文档节点，版本化）──
  mapping_table:
    - 年度检查/年报     → reports/annual/<年份>_年度报告.md
    - 财务审计         → finance/audit/<年份>_审计报告.md
    - 慈善年检申报     → governance/compliance/<年份>_年检材料.md
    - 免税资格认定     → governance/qualification/免税资格认定.md
    - 合规自查记录     → governance/compliance/<年份>_合规自查.md

  # ── 要素④ 查询规范（检索口径，固化）──
  query_spec:
    retrieve_within: source_scope                # 约束② 锁定契约：检索范围不可运行时改
    must_cite: true                              # 约束③ 事实引用必带出处
    sort_by: 文档类型                            # 按合规材料类别归集
    number_strict: true                          # 数字（如年检结论、金额）必须引源

  # ── 要素⑤ 计算规范 + 报告框架 ──
  compute_and_report:
    method: SAG 语义检索 + 编译
    report_framework:
      - 合规材料清单（类型/年份/出处/是否已齐）
      - 每项：出处文档 + 原文摘要 + 关联链接
      - 缺失项显式标记（如"未提供年检材料 → 标待补"）

  # ── 要素⑥ 输出格式 ──
  output_format:
    - 引用文档原文（带出处链接）
    - 合规材料清单（表格/卡片）
    - AI 解读.md（独立文件，标注"AI 分析"，与事实分离）

  # ── 用户运行期可填项（不改检索逻辑）──
  open_params:
    - 年份

  # ── 约束② 锁定契约（构建期固化，运行期不可改）──
  locked_contract:
    label_synthesis: "AI 分析"                   # 约束③ AI 解读独立标注
    cannot_override_at_runtime: true
    compliance_no_self_assessment: true          # 场景红线：AI 不自行判定"合规/不合规"结论，仅归集材料并引源
    confidential_material_label: true            # 场景红线：未公开/涉密合规材料须标 confidential，不主动外泄

  fallback: BLOCKED                              # 约束⑤ 无命中不编造
  status: PUBLISHED                              # 约束⑥ 触发只路由不执行
```

---

## 2. 六要素逐项说明（便于改编）

| 要素 | 本包取值 | 改编时怎么填 |
|------|---------|-------------|
| ① 查询提示词 | `question_examples` 4 条 | 写组织里**真实被高频问到**的口语化问法，≥3 条 |
| ② 数据源 | `source_scope` 4 类 | 对齐你知识库的合规/审计/年报/资格目录 |
| ③ 知识库/映射表 | `mapping_table` | 问题意图 → 具体文档节点路径，路径要**真实存在** |
| ④ 查询规范 | `query_spec` | 检索范围 + 强制引用 + 数字引源；属锁定契约 |
| ⑤ 计算规范+报告框架 | `compute_and_report` | SAG 检索方法 + 合规清单结构 |
| ⑥ 输出格式 | `output_format` | 原文/清单/独立 AI 解读，三者分离 |

---

## 3. 填参示例（让样本"可运行"）

把 `open_params` 代入：`年份 = 2025`：

- `mapping_table` 解析为：
  - `reports/annual/2025_年度报告.md`
  - `finance/audit/2025_审计报告.md`
  - `governance/compliance/2025_年检材料.md`
  - `governance/qualification/免税资格认定.md`
  - `governance/compliance/2025_合规自查.md`
- 命中任一 `question_examples` 语义 → 加载本契约 → 仅在上述 4 类受治理语料内检索 → 必带出处 → 无命中答 BLOCKED。
- 若语料缺失（如某年无年检材料）→ 显式标"待补"，不臆造"已通过"。

---

## 4. 验证证据（GDTcreater（未开源，本技能不依赖） 第六件套 · 核对方式）

- **动作**：用 `rag_helper.py --query "2025 年合规和年检材料归集"` 跑一次；
- **预期**：返回结果**全部**落在 `governance/compliance`、`finance/audit`、`reports/annual`、`governance/qualification` 四类路径内，且每条带文件出处；
- **反例（应被拦截）**：若返回"我们去年年检肯定过了"这类**无出处结论**，说明 `compliance_no_self_assessment` 红线未生效，须回查契约；
- **人工抽检**：抽 1 个年度，对照真实合规文件夹，确认契约路径与实际一致、无断链。
- **记录**：验证人与日期写入本包 `status: PUBLISHED` 旁注。

---

## 5. 双模式注解（什么时候用本契约，什么时候不用）

| 用户问法 | 模式 | 反应 |
|---------|------|------|
| "把 2025 年所有合规和审计报告归集一下" | **GDT 触发**（命中 `question_examples`）| 加载本契约，受治理检索、必带出处、无命中 BLOCKED |
| "我们合规情况大概还行吧？"（无具体材料诉求）| **闲聊/自由** | 不加载契约，SAG 灵活检索、不作正式合规结论 |
| "去年年检过了没，对外能说吗"（触及合规结论+对外）| 闲聊中检测到信号 → **主动提示升级** | "这涉及合规结论与对外口径，我按受治理契约保证准确、不自行下结论，可以吗？"确认后切 GDT 触发 |

> 一句话：本契约**只在 GDT 触发模式加载**；合规结论**永远不靠 AI 自判**，只归集并引源——这是公益组织最不能出错的红线之一。

---

*本示范包是 GDT-KB 适配样本集之一；同类场景（项目披露/受益群体/财务/捐赠方/治理/风险/人事）按同 schema 复制即可。*
