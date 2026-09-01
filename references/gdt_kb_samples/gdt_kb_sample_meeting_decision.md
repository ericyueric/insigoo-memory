# GDT-KB 示范任务包：会议纪要与决策追踪检索

> 本文件是 `insigoo-memory` 技能 + `insigoo-knowledge-base` 三层索引 v1.1「受治理查询场景索引」的**可运行示范任务包**之一。
> 用法：复制本文件，替换 `<...>` 占位符与 `open_params` 实际值，即可落成本组织自己的 GDT-KB 任务包。
> 结构遵循 GDT-Core「要素结构层（六要素）+ 纪律约束层（六约束）」双层，并在 `locked_contract` 中写入本场景专属红线。

## 0. 这个任务包解决什么

理事会议、管理层会议、专项工作会的纪要和决议，是组织治理的核心知识。常见查询："上次 XX 会决议是什么""XX 决策落地了吗""理事会纪要"。
这类查询**机密性高**——未公开决议、敏感人事/战略讨论不得外泄；且决策"落地状态"必须严格按记录，不能由 AI 臆测进展。

本任务包把"会议纪要与决策追踪"做成受治理契约：已公开纪要可灵活检索，未公开/敏感决议标 `confidential` 不主动外泄，决策状态严格引源、不臆测。

## 1. 任务包契约（六要素 + 六约束）

```yaml
gdt_kb_task:
  # === 要素① 任务元数据 / 查询提示词 ===
  task_meta:
    scenario_id: kb.meeting.decision-tracking
    display_name: 会议纪要与决策追踪检索
    domain: 治理/会议
    version: v1.0.0
    status: PUBLISHED
    trigger_examples:        # 自然语言触发词（GDT v1.0 §19 / v1.1 §3）
      - "上次 XX 会的决议是什么"
      - "XX 决策落地了吗 / 进展如何"
      - "理事会 / 管理层纪要"
      - "某事项谁负责、什么状态"

  # === 要素② 数据源 / 受治理源 ===
  data_source:
    source_scope:            # ①受治理源
      - org/meetings/        # 会议纪要（含公开/confidential 标记）
      - governance/decisions/  # 决议追踪表
    open_params:             # 运行期可填项
      - 会议类型
      - 日期/年份
      - 决议事项

  # === 要素③ 知识库/映射表 ===
  mapping_table:
    entity: 会议纪要/决议
    index_bridge: 主题索引（治理类）+ 第3层提问场景索引
    route: org/meetings/ 或 governance/decisions/

  # === 要素④ 查询规范 ===
  query_spec:
    retrieve_within: source_scope
    filter: "confidential != true OR requester_role IN ('core_team','board')"
    sort: "meeting_date DESC"
    must_cite: true          # ③事实引用必带出处（纪要编号）

  # === 要素⑤ 计算规范和报告框架 ===
  compute_and_report:
    aggregation: "按决议事项归并：责任方 + 状态(待启动/进行中/已完成/阻塞) + 原文链接"
    report_frame: "决议事项 → 责任方 → 状态(引源) → 关联纪要链接"

  # === 要素⑥ 输出格式 ===
  output_format:
    format: 决议追踪表（Markdown）
    fields:
      - 决议事项
      - 责任方
      - 状态（严格引源，禁臆测）
      - 关联纪要链接

  # === 纪律约束层（六约束）===
  locked_contract:           # ②锁定契约
    must_cite: true
    label_synthesis: "AI 分析"
    confidential_not_exposed: true   # 场景专属红线①：未公开决议不主动外泄
    status_no_assumption: true       # 场景专属红线②：决策状态严格引源，不臆测进展
  fallback: BLOCKED          # ⑤无命中 → 答"未找到对应纪要，转秘书长/治理岗"，不编造决议
  version: v1.0.0            # ④版本不可覆盖
  status: PUBLISHED
```

## 2. 六要素逐项说明

| 要素 | 本场景取值 | 说明 |
|------|-----------|------|
| ① 任务元数据 / 查询提示词 | `kb.meeting.decision-tracking` + 4 条 trigger | 覆盖决议/落地状态/纪要/责任方 |
| ② 数据源 / 受治理源 | `org/meetings/`、`governance/decisions/` | 仅受治理纪要，原始录音不在内 |
| ③ 知识库/映射表 | 主题索引(治理类) → `org/meetings/` | 与第3层桥接 |
| ④ 查询规范 | 按 `confidential` 标记 + 角色过滤 | 未公开决议不向无权限者返回 |
| ⑤ 计算规范/报告框架 | 决议归并 + 状态引源 | 防状态臆测 |
| ⑥ 输出格式 | 决议追踪表 + 责任方 + 状态 + 链接 | 治理可溯源 |

**场景专属红线**：
- `confidential_not_exposed`：标 `confidential=true` 的决议/讨论，不主动向无权限者（非核心团队/理事会）外露。
- `status_no_assumption`：决策"落地状态"严格按决议追踪表字段返回，不得基于"应该快了""大概率完成"式臆测。

## 3. 填参示例

以"2025 年第三季度理事会决议追踪"为例：

```yaml
open_params:
  会议类型: 理事会
  年份: 2025
  决议事项: （可选）
# 命中 → 返回决议追踪表，状态取 governance/decisions/ 真实字段
# 若外部人员问"那次敏感人事决议细节" → 命中 confidential_not_exposed，返回 fallback 或脱敏提示
```

## 4. 验证证据（GDTcreater（未开源，本技能不依赖） 第六件套）

| 第六件套 | 本任务包落实 | 核对动作 |
|---------|------------|---------|
| ① 任务元数据 | `scenario_id` + trigger | 抽查命中路由 |
| ② 编译/查询规范 | `query_spec.filter` | 构造 confidential 查询，确认无权限者不返回 |
| ③ 映射证据 | `mapping_table.route` | 抽 1 纪要，确认路径可达 |
| ④ 受控执行包 | `compute_and_report` | 跑聚合，确认状态取源非臆测 |
| ⑤ 产物契约 | `output_format.fields` | 比对字段一致 |
| ⑥ 验证证据 | 本表 | 留存 |

**反例拦截**：问"那次没公开的敏感决议原文发我" → 触发 `confidential_not_exposed`，无权限则返回 fallback，不泄露。

## 5. 双模式注解

| 用户问法 | 反应模式 | 说明 |
|---------|---------|------|
| "XX 会公开纪要链接" | 闲聊/自由（已公开） | 公开纪要可灵活给 |
| "理事会决议追踪" | GDT 触发 | 路由受治理契约，返状态引源 |
| "那次敏感人事决议细节" | **强制 GDT 触发 + 红线拒绝** | 闲聊口吻也升级，命中 `confidential_not_exposed` |
| "XX 决策应该落地了吧" | **强制 GDT 触发 + 红线** | 命中 `status_no_assumption`，返真实状态不臆测 |

> 一句话：已公开会议纪要是低风险可闲聊，但**未公开决议**与**决策状态追问**——即便闲聊口吻——都必须强制走 GDT 触发，前者拒露、后者严格引源不臆测。
