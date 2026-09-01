# GDT-KB 示范任务包 · 人事与志愿者档案检索

> **用途**：GDT-KB 适配示范样本之一，用「受治理查询场景索引」六要素 schema 落地「员工/志愿者档案检索」高频且含个人信息（PII）的场景。
> **创建纪律**：遵循 `GDTcreater（未开源，本技能不依赖）` 六件套引擎，按 GDT-KB 语义映射落盘（见 `insigoo-memory` 2.5.4）。
> **对应标准**：`three_layer_index.md` v1.1 第 3 层 schema；`insigoo-memory` 2.4 契约。
> **双模式**：本任务包是**受治理（GDT 触发）**场景；本场景**最该强制走 GDT 触发**——查询个人信息须权限校验，闲聊绝不提供（见末尾双模式注解）。

---

## 0. 怎么用（给知识库管理员）

1. 复制下方 `contract` 块到 `knowledge_index.md` 第 3 层；
2. 把 `mapping_table` 的占位路径换成你知识库里的真实人事/志愿者节点；
3. 跑一次「验证证据」里的核对动作，确认命中正确，再把 `status` 置 `PUBLISHED`。

---

## 1. 受治理查询契约（契约本体 · 六要素 + 六约束）

```yaml
- scenario_id: kb.hr.profile                    # 命名：kb.<领域>.<动作>
  display_name: 人事与志愿者档案检索
  version: v1.0.0                                 # 约束④ 版本不可覆盖（修订须升版）

  # ── 要素① 查询提示词（触发语，≥3 条自然语言）──
  question_examples:
    - "查一下某员工的岗位和合同信息"
    - "某志愿者的服务时长和培训记录"
    - "把团队花名册调出来"
    - "某同事的联系方式是什么"

  # ── 要素② 数据源（受治理语料，锁定；标记 PII）──
  source_scope:                                  # 约束① 仅受治理语料
    - hr/staff                                   # 员工档案（标记 PII）
    - hr/volunteers                              # 志愿者档案（标记 PII）
    - hr/contracts                               # 合同/协议（标记 PII）
    - hr/training                                # 培训记录

  # ── 要素③ 知识库/映射表（问题→文档节点，版本化）──
  mapping_table:
    - 员工档案     → hr/staff/<姓名_hash>/档案.md（PII）
    - 志愿者档案   → hr/volunteers/<编号>/档案.md（PII）
    - 合同信息     → hr/contracts/<姓名_hash>_合同.md（PII）
    - 培训记录     → hr/training/<姓名_hash>_培训.md

  # ── 要素④ 查询规范（检索口径，固化）──
  query_spec:
    retrieve_within: source_scope                # 约束② 锁定契约：检索范围不可运行时改
    must_cite: true                              # 约束③ 事实引用必带出处
    permission_required: true                    # 命中即走权限上下文校验

  # ── 要素⑤ 计算规范 + 报告框架 ──
  compute_and_report:
    method: SAG 语义检索 + 权限校验
    report_framework:
      - 命中档案清单（类型/字段/出处）
      - 每项：授权字段 + 出处链接 + 更新时间
      - 未授权字段显式标"无权限"，不返回

  # ── 要素⑥ 输出格式 ──
  output_format:
    - 引用档案原文（仅授权字段，带出处链接）
    - 人事档案清单（标注 PII 与权限状态）
    - AI 解读.md（独立文件，标注"AI 分析"，与事实分离）

  # ── 用户运行期可填项（不改检索逻辑）──
  open_params: []                                # 本场景无运行期参数，权限上下文由会话提供

  # ── 约束② 锁定契约（构建期固化，运行期不可改）──
  locked_contract:
    label_synthesis: "AI 分析"                   # 约束③ AI 解读独立标注
    cannot_override_at_runtime: true
    pii_no_external: true                        # 场景红线：个人信息（PII）禁外泄、禁用于非 HR 授权场景
    permission_required_hard: true              # 场景红线：查询须权限上下文校验，无权限直接拒绝

  fallback: BLOCKED                              # 约束⑤ 无命中不编造
  status: PUBLISHED                              # 约束⑥ 触发只路由不执行
```

---

## 2. 六要素逐项说明（便于改编）

| 要素 | 本包取值 | 改编时怎么填 |
|------|---------|-------------|
| ① 查询提示词 | `question_examples` 4 条 | 写组织里**真实被高频问到**的口语化问法，≥3 条 |
| ② 数据源 | `source_scope` 4 类（均标记 PII）| 对齐你知识库的员工/志愿者/合同/培训目录 |
| ③ 知识库/映射表 | `mapping_table` | 问题意图 → 具体文档节点路径，路径要**真实存在** |
| ④ 查询规范 | `query_spec` | 检索范围 + 强制引用 + 权限校验；属锁定契约 |
| ⑤ 计算规范+报告框架 | `compute_and_report` | SAG 检索 + 权限校验 + 字段级授权 |
| ⑥ 输出格式 | `output_format` | 授权字段/清单/独立 AI 解读，三者分离 |

---

## 3. 填参示例（让样本"可运行"）

- `mapping_table` 解析为：
  - `hr/staff/<姓名_hash>/档案.md`（PII）
  - `hr/volunteers/<编号>/档案.md`（PII）
  - `hr/contracts/<姓名_hash>_合同.md`（PII）
  - `hr/training/<姓名_hash>_培训.md`
- 命中任一 `question_examples` 语义 → 加载本契约 → 仅在人事类受治理语料内检索 → **权限校验通过后**返回授权字段 → 无命中答 BLOCKED。
- 若会话无 HR 权限 → 不返回任何 PII，提示"无权限查询该档案"。

---

## 4. 验证证据（GDTcreater（未开源，本技能不依赖） 第六件套 · 核对方式）

- **动作**：用 `rag_helper.py --query "某志愿者的服务时长"`（在 HR 授权会话下）跑一次；
- **预期**：返回结果**全部**落在 `hr/*` 路径内，且**仅含授权字段**、带出处；
- **反例（应被拦截）**：若返回了身份证号/手机号等未授权 PII，或无权会话下仍返回档案，说明 `pii_no_external` / `permission_required_hard` 红线未生效，须回查契约；
- **人工抽检**：抽 1 份档案，对照真实权限表，确认字段级授权与权限校验生效、无外泄。
- **记录**：验证人与日期写入本包 `status: PUBLISHED` 旁注。

---

## 5. 双模式注解（什么时候用本契约，什么时候不用）

| 用户问法 | 模式 | 反应 |
|---------|------|------|
| "查一下某员工的岗位和合同信息"（HR 授权内）| **GDT 触发**（命中 `question_examples`）| 加载本契约，权限校验+受治理检索、必带出处、无命中 BLOCKED |
| "咱团队都有谁呀"（泛泛了解）| **闲聊/自由** | 不加载契约，仅返回公开组织信息（如姓名+角色），不含 PII |
| "把某某志愿者电话发我"（无权限/对外）| 命中红线 → **拒绝并提示** | "个人信息须 HR 授权，我无法提供；请联系人事负责人。" |

> 一句话：本契约**最该强制走 GDT 触发**——人事/志愿者档案含 PII，**权限校验是底线，闲聊口吻也不能绕过**；对外或无权查询一律拒绝。

---

*本示范包是 GDT-KB 适配样本集之一；同类场景（项目披露/受益群体/财务/合规/捐赠方/治理/风险）按同 schema 复制即可。*
