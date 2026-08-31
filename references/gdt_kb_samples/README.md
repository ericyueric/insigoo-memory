# GDT-KB 示范任务包集索引

> 版本：v1.0 ｜ 归属：insigoo-memory（GDT-KB 适配）× insigoo-knowledge-base（组织知识库通用标准 v1.1）
> 作用：本目录含 **15 个严格同 schema** 的可运行示范任务包（GDT-KB），供公益组织直接对标改编，把"受治理查询场景索引"从方法论变成可抄样本。

## 一、这是什么

GDT-KB 是 **GDT-Core（通用治理内核）** 在"知识管理场景"的适配。每个示范包用同一套 **六要素 yaml 契约 + 六约束纪律** 描述一个高频知识查询场景，并演示如何在 `locked_contract` 中加"场景专属红线"。

- **六要素**：① 查询提示词 ② 数据源 ③ 知识库/映射表 ④ 查询规范 ⑤ 计算规范+报告框架 ⑥ 输出格式
- **六约束**：① 受治理源 ② 锁定契约 ③ 事实解读分离 ④ 版本不可覆盖 ⑤ 不猜测 ⑥ 触发只路由不执行
- **双模式**：闲聊/自由 ↔ GDT 触发（受治理），判定逻辑见本技能 `references/three_layer_index.md` §3.1

每个样本文件结构统一（7 段）：0 怎么用 → 1 六要素 yaml 契约 → 2 六要素逐项说明 → 3 填参示例 → 4 验证证据（GDTcreater 第六件套）→ 5 双模式注解。

## 二、敏感度分级与双模式反应

| 等级 | 含义 | 典型场景 | 双模式反应 |
|------|------|---------|-----------|
| **L1 低** | 公开披露基线 | 项目全周期披露 | 闲聊可灵活；触及敏感信号（合规/财务/PII）主动升级 |
| **L2 中** | 一般敏感（关系/密钥/章程/敏感信息范围） | 受益群体/捐赠方/治理/合作伙伴/政策/内部SOP | 建议走 GDT 触发；闲聊敏感信号升级 |
| **L3 高** | 数字/金额/合规结论 | 财务/合规年检/资产台账/培训/会议纪要 | **强制 GDT 触发**（即便闲聊口吻问也升级） |
| **L4 极高** | 未公开信息/PII/对外口径审批 | 风险舆情/人事志愿者/传播对外口径 | **强制 GDT 触发** + 严格 `fallback: BLOCKED` |

## 三、索引表（15 个样本）

| # | 场景 | 文件 | 场景专属红线（locked_contract） | 敏感度 | 双模式 |
|---|------|------|-------------------------------|--------|--------|
| 1 | 项目全周期披露文档检索 | `gdt_kb_sample_project_full_disclosure.md` | 基线样本，无额外红线 | L1 | 可闲聊 |
| 2 | 某受益群体全部评估记录检索 | `gdt_kb_sample_beneficiary_evaluation.md` | 禁止跨群体横比（基线/口径不同，强行合并失真） | L2 | 建议触发 |
| 3 | 某年度财务披露汇总检索 | `gdt_kb_sample_finance_year_disclosure.md` | 财务数字禁推断/估算，必须引源 | L3 | 强制触发 |
| 4 | 年度合规/年检材料检索 | `gdt_kb_sample_compliance_year.md` | 合规结论禁自判；未公开材料标 confidential | L3 | 强制触发 |
| 5 | 某捐赠方全部项目披露检索 | `gdt_kb_sample_donor_projects.md` | 捐赠方商业敏感信息不超范围暴露 | L2 | 建议触发 |
| 6 | 治理与内部制度文件检索 | `gdt_kb_sample_governance.md` | 章程/决议禁 AI 改写，须原文引用 | L2 | 建议触发 |
| 7 | 风险/投诉/舆情记录检索 | `gdt_kb_sample_risk_complaint.md` | 未公开记录禁外泄 + PII 脱敏 | L4 | 强制触发 |
| 8 | 人事与志愿者档案检索 | `gdt_kb_sample_hr_volunteer.md` | PII 禁外泄 + 权限校验 | L4 | 强制触发 |
| 9 | 合作伙伴与 MOU 检索 | `gdt_kb_sample_partner_mou.md` | 未公开条款不外露 + 合作关系不夸大 | L2 | 建议触发 |
| 10 | 政策法规模应与本组织映射检索 | `gdt_kb_sample_policy_mapping.md` | 法规须引源 + AI 不下合规结论 | L2 | 建议触发 |
| 11 | 传播素材与对外口径检索 | `gdt_kb_sample_communication.md` | 对外必须走审批版 | L4 | 强制触发 |
| 12 | 内部工具/SOP 知识检索 | `gdt_kb_sample_internal_sop.md` | 敏感权限/密钥不外露 + 未审批手册不外发 | L2 | 建议触发 |
| 13 | 物资/资产/票据台账检索 | `gdt_kb_sample_asset_ledger.md` | 数量金额禁推断（同财务高危） | L3 | 强制触发 |
| 14 | 培训/能力建设项目记录检索 | `gdt_kb_sample_training.md` | 学员 PII 脱敏 + 个人成绩禁外泄 | L3 | 强制触发 |
| 15 | 会议纪要与决策追踪检索 | `gdt_kb_sample_meeting_decision.md` | 未公开决议不外露 + 状态不臆测 | L3 | 强制触发 |

## 四、怎么用（复制改编流程）

1. **选模板**：按上表"场景"找最接近的样本（优先参考同类敏感度）。
2. **复制文件**：把 `gdt_kb_sample_xxx.md` 复制到本组织知识库 `references/gdt_kb/`（或同级目录）。
3. **填参**：保留 yaml 契约结构，改 `open_params`（组织名/项目名/年份等）、`source_scope`（本组织实际节点路径）、`mapping_table`（本组织实际映射）。
4. **加红线**：在 `locked_contract` 增删场景专属约束（参考索引表"场景专属红线"列）。
5. **验证**：按文件末尾"验证证据（GDTcreater 第六件套）"逐项核对，确认 `fallback: BLOCKED` 与 `status: PUBLISHED`。
6. **登记索引**：把该契约登记进组织知识库第 3 层"受治理查询场景索引"（见 `three_layer_index.md`）。

## 五、关联文档

- GDT-Core 双层建模与通用化设计：本技能 `references/gdt_design.md`
- 组织知识库三层索引标准（v1.1，含双模式 §3.1）：本技能 `references/three_layer_index.md`
- 知识库维护指南（含 4.5 双模式检索规范）：本技能 `references/maintenance_guide.md`
- 六件套向导引擎（数据任务）：`GDTcreater` 技能
- 知识诊断武器：`insigoo-sia` 技能
