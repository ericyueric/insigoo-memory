# GDT-KB 示范任务包 · 某捐赠方全部项目披露检索

> **用途**：GDT-KB 适配示范样本之一，用「受治理查询场景索引」六要素 schema 落地「某捐赠方参与的所有项目/资助披露检索」高频场景。
> **创建纪律**：遵循 `GDTcreater（未开源，本技能不依赖）` 六件套引擎，按 GDT-KB 语义映射落盘（见 `insigoo-sag-architect` 2.5.4）。
> **对应标准**：`three_layer_index.md` v1.1 第 3 层 schema；`insigoo-sag-architect` 2.4 契约。
> **双模式**：本任务包是**受治理（GDT 触发）**场景；闲聊/自由查询不加载本契约（见末尾双模式注解）。

---

## 0. 怎么用（给知识库管理员）

1. 复制下方 `contract` 块到 `knowledge_index.md` 第 3 层；
2. 把 `open_params`（捐赠方名称）替换成实际值；
3. 把 `mapping_table` 的占位路径换成你知识库里的真实项目/资助节点；
4. 跑一次「验证证据」里的核对动作，确认命中正确，再把 `status` 置 `PUBLISHED`。

---

## 1. 受治理查询契约（契约本体 · 六要素 + 六约束）

```yaml
- scenario_id: kb.donor.projects                # 命名：kb.<领域>.<动作>
  display_name: 某捐赠方全部项目披露检索
  version: v1.0.0                                 # 约束④ 版本不可覆盖（修订须升版）

  # ── 要素① 查询提示词（触发语，≥3 条自然语言）──
  question_examples:
    - "XX 基金会投了我们哪些项目"
    - "把 A 企业捐赠方相关的所有项目披露找出来"
    - "查一下某资助方这几年的合作项目清单"
    - "给我们的捐赠人 B 出一份项目参与汇总"

  # ── 要素② 数据源（受治理语料，锁定）──
  source_scope:                                  # 约束① 仅受治理语料
    - projects                                   # 项目主档（带 donor 标签）
    - finance/grants                             # 资助/拨款记录
    - reports/donor                             # 对捐赠方披露报告
    - contracts/grant                            # 资助协议

  # ── 要素③ 知识库/映射表（问题→文档节点，版本化）──
  mapping_table:
    - 项目主档       → projects/<项目名>/README.md（筛 donor=<捐赠方>）
    - 资助协议       → contracts/grant/<捐赠方>_<年份>_协议.md
    - 拨款记录       → finance/grants/<捐赠方>_拨款流水.md
    - 对捐赠方报告   → reports/donor/<捐赠方>_年度披露.md

  # ── 要素④ 查询规范（检索口径，固化）──
  query_spec:
    retrieve_within: source_scope                # 约束② 锁定契约：检索范围不可运行时改
    must_cite: true                              # 约束③ 事实引用必带出处
    filter: "donor = open_params.捐赠方"         # 仅检索该捐赠方关联项
    sort_by: 时间降序

  # ── 要素⑤ 计算规范 + 报告框架 ──
  compute_and_report:
    method: SAG 语义检索 + 按 donor 过滤 + 编译
    report_framework:
      - 捐赠方项目清单（项目名/周期/状态/资助额）
      - 每项：出处文档 + 原文摘要 + 关联链接
      - 跨项目仅做汇总，不强行横比成效

  # ── 要素⑥ 输出格式 ──
  output_format:
    - 引用文档原文（带出处链接）
    - 捐赠方项目清单（表格/卡片）
    - AI 解读.md（独立文件，标注"AI 分析"，与事实分离）

  # ── 用户运行期可填项（不改检索逻辑）──
  open_params:
    - 捐赠方名称

  # ── 约束② 锁定契约（构建期固化，运行期不可改）──
  locked_contract:
    label_synthesis: "AI 分析"                   # 约束③ AI 解读独立标注
    cannot_override_at_runtime: true
    donor_sensitive_no_overexpose: true          # 场景红线：捐赠方商业敏感信息（如未公开联系方式/内部评级）不超范围暴露
    cross_project_no_compare: true               # 场景红线：跨项目仅汇总，不强行横比成效（口径不同）

  fallback: BLOCKED                              # 约束⑤ 无命中不编造
  status: PUBLISHED                              # 约束⑥ 触发只路由不执行
```

---

## 2. 六要素逐项说明（便于改编）

| 要素 | 本包取值 | 改编时怎么填 |
|------|---------|-------------|
| ① 查询提示词 | `question_examples` 4 条 | 写组织里**真实被高频问到**的口语化问法，≥3 条 |
| ② 数据源 | `source_scope` 4 类 | 对齐你知识库的项目/资助/协议/披露目录 |
| ③ 知识库/映射表 | `mapping_table` | 问题意图 → 具体文档节点路径，路径要**真实存在** |
| ④ 查询规范 | `query_spec` | 检索范围 + donor 过滤 + 强制引用；属锁定契约 |
| ⑤ 计算规范+报告框架 | `compute_and_report` | SAG 检索 + donor 过滤 + 清单结构 |
| ⑥ 输出格式 | `output_format` | 原文/清单/独立 AI 解读，三者分离 |

---

## 3. 填参示例（让样本"可运行"）

把 `open_params` 代入：`捐赠方名称 = 示例基金会`：

- `query_spec.filter` 解析为 `donor = 示例基金会`；
- `mapping_table` 解析为：
  - `projects/<项目名>/README.md`（筛 donor=示例基金会）
  - `contracts/grant/示例基金会_2025_协议.md`
  - `finance/grants/示例基金会_拨款流水.md`
  - `reports/donor/示例基金会_年度披露.md`
- 命中任一 `question_examples` 语义 → 加载本契约 → 仅在该捐赠方关联受治理语料内检索 → 必带出处 → 无命中答 BLOCKED。

---

## 4. 验证证据（GDTcreater（未开源，本技能不依赖） 第六件套 · 核对方式）

- **动作**：用 SAG 检索 API 验证——`curl -X POST http://127.0.0.1:4173/search -d '{"query":"示例基金会 投了我们哪些项目","top_k":5}'` 跑一次；
- **预期**：返回结果**全部**带 `donor = 示例基金会` 过滤，落在 `projects/finance/grants/reports/donor/contracts/grant` 路径内，且每条带文件出处；
- **反例（应被拦截）**：若返回了**其他捐赠方**的项目，或暴露了未公开的捐赠方联系人/内部评级，说明 `donor_sensitive_no_overexpose` 红线未生效，须回查契约；
- **人工抽检**：抽 1 个捐赠方，对照真实项目主档 donor 标签，确认过滤正确、无串档。
- **记录**：验证人与日期写入本包 `status: PUBLISHED` 旁注。

---

## 5. 双模式注解（什么时候用本契约，什么时候不用）

| 用户问法 | 模式 | 反应 |
|---------|------|------|
| "把示例基金会相关的所有项目披露找出来" | **GDT 触发**（命中 `question_examples`）| 加载本契约，donor 过滤+受治理检索、必带出处、无命中 BLOCKED |
| "我们大概有哪些大资助方？"（泛泛而谈）| **闲聊/自由** | 不加载契约，SAG 灵活检索、不强制引用、不作正式披露 |
| "给某捐赠人出份材料，要写清他们投了啥"（触及对捐赠方披露义务）| 闲聊中检测到信号 → **主动提示升级** | "这涉及对捐赠方披露口径，我按受治理契约保证准确、不超范围暴露敏感信息，可以吗？"确认后切 GDT 触发 |

> 一句话：本契约**只在 GDT 触发模式加载**；捐赠方场景的命门是**敏感信息不超范围暴露**——即便授权查询，也不该把未公开商业信息带进对外产物。

---

*本示范包是 GDT-KB 适配样本集之一；同类场景（项目披露/受益群体/财务/合规/治理/风险/人事）按同 schema 复制即可。*
