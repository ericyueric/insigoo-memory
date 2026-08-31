# GDT-KB 示范任务包 · 合作伙伴与 MOU 检索

> **用途**：GDT-KB 适配示范样本之一，用「受治理查询场景索引」六要素 schema 落地「某合作机构/备忘录(MOU)/合作协议检索」高频场景。
> **创建纪律**：遵循 `GDTcreater` 六件套引擎，按 GDT-KB 语义映射落盘（见 `insigoo-memory` 2.5.4）。
> **对应标准**：`three_layer_index.md` v1.1 第 3 层 schema；`insigoo-memory` 2.4 契约。
> **双模式**：本任务包是**受治理（GDT 触发）**场景；闲聊/自由查询不加载本契约（见末尾双模式注解）。

---

## 0. 怎么用（给知识库管理员）

1. 复制下方 `contract` 块到 `knowledge_index.md` 第 3 层；
2. 把 `open_params`（合作方名称）替换成实际值；
3. 把 `mapping_table` 的占位路径换成你知识库里的真实合作机构/协议节点；
4. 跑一次「验证证据」里的核对动作，确认命中正确，再把 `status` 置 `PUBLISHED`。

---

## 1. 受治理查询契约（契约本体 · 六要素 + 六约束）

```yaml
- scenario_id: kb.partner.mou                  # 命名：kb.<领域>.<动作>
  display_name: 合作伙伴与MOU检索
  version: v1.0.0                                 # 约束④ 版本不可覆盖（修订须升版）

  # ── 要素① 查询提示词（触发语，≥3 条自然语言）──
  question_examples:
    - "我们和 XX 机构是什么合作关系"
    - "查一下跟 A 组织的备忘录/MOU 内容"
    - "某合作方的权责边界在哪份文件里"
    - "跟 B 基金会签过什么合作协议"

  # ── 要素② 数据源（受治理语料，锁定）──
  source_scope:                                  # 约束① 仅受治理语料
    - partners                                   # 合作机构主档
    - contracts/mou                              # 备忘录/MOU
    - contracts/cooperation                      # 合作协议
    - governance/authority                      # 授权与权责边界

  # ── 要素③ 知识库/映射表（问题→文档节点，版本化）──
  mapping_table:
    - 合作机构主档   → partners/<机构名>/README.md
    - MOU/备忘录     → contracts/mou/<机构名>_MOU.md
    - 合作协议       → contracts/cooperation/<机构名>_协议.md
    - 权责边界       → governance/authority/<机构名>_授权.md

  # ── 要素④ 查询规范（检索口径，固化）──
  query_spec:
    retrieve_within: source_scope                # 约束② 锁定契约：检索范围不可运行时改
    must_cite: true                              # 约束③ 事实引用必带出处
    filter: "partner = open_params.合作方"        # 仅检索该合作方关联项
    sort_by: 时间降序

  # ── 要素⑤ 计算规范 + 报告框架 ──
  compute_and_report:
    method: SAG 语义检索 + 按 partner 过滤 + 编译
    report_framework:
      - 合作方清单（机构/合作类型/周期/状态）
      - 每项：出处文档 + 原文摘要 + 关联链接
      - 权责边界单独列示，不并入泛泛简介

  # ── 要素⑥ 输出格式 ──
  output_format:
    - 引用文档原文（带出处链接）
    - 合作方清单（表格/卡片）
    - AI 解读.md（独立文件，标注"AI 分析"，与事实分离）

  # ── 用户运行期可填项（不改检索逻辑）──
  open_params:
    - 合作方名称

  # ── 约束② 锁定契约（构建期固化，运行期不可改）──
  locked_contract:
    label_synthesis: "AI 分析"                   # 约束③ AI 解读独立标注
    cannot_override_at_runtime: true
    confidential_clause_no_overexpose: true      # 场景红线：未公开条款/商业条件/内部评级不外露
    partner_bound_no_overstate: true             # 场景红线：合作关系表述不夸大、不超授权范围描述

  fallback: BLOCKED                              # 约束⑤ 无命中不编造
  status: PUBLISHED                              # 约束⑥ 触发只路由不执行
```

---

## 2. 六要素逐项说明（便于改编）

| 要素 | 本包取值 | 改编时怎么填 |
|------|---------|-------------|
| ① 查询提示词 | `question_examples` 4 条 | 写组织里**真实被高频问到**的口语化问法，≥3 条 |
| ② 数据源 | `source_scope` 4 类 | 对齐你知识库的合作机构/MOU/协议/授权目录 |
| ③ 知识库/映射表 | `mapping_table` | 问题意图 → 具体文档节点路径，路径要**真实存在** |
| ④ 查询规范 | `query_spec` | 检索范围 + partner 过滤 + 强制引用；属锁定契约 |
| ⑤ 计算规范+报告框架 | `compute_and_report` | SAG 检索 + partner 过滤 + 清单结构 |
| ⑥ 输出格式 | `output_format` | 原文/清单/独立 AI 解读，三者分离 |

---

## 3. 填参示例（让样本"可运行"）

把 `open_params` 代入：`合作方名称 = 河流守望者联盟`：

- `query_spec.filter` 解析为 `partner = 河流守望者联盟`；
- `mapping_table` 解析为：
  - `partners/河流守望者联盟/README.md`
  - `contracts/mou/河流守望者联盟_MOU.md`
  - `contracts/cooperation/河流守望者联盟_协议.md`
  - `governance/authority/河流守望者联盟_授权.md`
- 命中任一 `question_examples` 语义 → 加载本契约 → 仅在该合作方关联受治理语料内检索 → 必带出处 → 无命中答 BLOCKED。

---

## 4. 验证证据（GDTcreater 第六件套 · 核对方式）

- **动作**：用 `rag_helper.py --query "我们和河流守望者联盟是什么合作关系"` 跑一次；
- **预期**：返回结果**全部**带 `partner = 河流守望者联盟` 过滤，落在 `partners/contracts/governance` 路径内，且每条带文件出处；
- **反例（应被拦截）**：若返回了**非**该合作方的协议，或暴露了未公开的条款/商业条件/内部评级，说明 `confidential_clause_no_overexpose` 红线未生效，须回查契约；
- **人工抽检**：抽 1 个合作方，对照真实 MOU/协议，确认合作关系描述未夸大、权责边界未超授权范围。
- **记录**：验证人与日期写入本包 `status: PUBLISHED` 旁注。

---

## 5. 双模式注解（什么时候用本契约，什么时候不用）

| 用户问法 | 模式 | 反应 |
|---------|------|------|
| "查一下跟河流守望者联盟的备忘录内容" | **GDT 触发**（命中 `question_examples`）| 加载本契约，partner 过滤+受治理检索、必带出处、无命中 BLOCKED |
| "我们大概跟哪些机构有合作？"（泛泛而谈）| **闲聊/自由** | 不加载契约，SAG 灵活检索、不强制引用、不作正式披露 |
| "跟某机构合作到什么程度了，对外能怎么讲"（触及对外表述/未公开条款）| 闲聊中检测到信号 → **主动提示升级** | "这涉及合作条款与对外表述边界，我按受治理契约保证不外露未公开内容、不夸大合作关系，可以吗？"确认后切 GDT 触发 |

> 一句话：本契约**只在 GDT 触发模式加载**；合作方场景的命门是**未公开条款不外露 + 合作关系不夸大**——即便授权查询，也不该把商业条件带进对外产物。

---

*本示范包是 GDT-KB 适配样本集之一；同类场景（项目披露/受益群体/财务/合规/治理/风险/人事/政策/传播）按同 schema 复制即可。*
