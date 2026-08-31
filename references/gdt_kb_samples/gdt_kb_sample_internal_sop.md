# GDT-KB 示范任务包：内部工具 / SOP 知识检索

> 本文件是 `insigoo-memory` 技能 + `insigoo-knowledge-base` 三层索引 v1.1「受治理查询场景索引」的**可运行示范任务包**之一。
> 用法：复制本文件，替换 `<...>` 占位符与 `open_params` 实际值，即可落成本组织自己的 GDT-KB 任务包。
> 结构遵循 GDT-Core「要素结构层（六要素）+ 纪律约束层（六约束）」双层，并在 `locked_contract` 中写入本场景专属红线。

## 0. 这个任务包解决什么

组织内部沉淀了大量工具手册、操作流程（SOP）、方法论文档。成员常问"XX 工具怎么用""XX 流程怎么做""内部操作手册在哪"。
这类查询**大部分是低风险的操作指引，可走闲聊/自由模式**；但凡涉及**账号、权限、密钥、后台入口、未审批的内部操作手册**，就属于敏感知识，必须受治理契约守护，不能由闲聊自由生成或外泄。

本任务包把"内部工具/SOP 检索"做成受治理契约：默认只对已编入索引、带版本号的公开操作文档做路由检索；敏感权限类 SOP 须显式标 `sensitive` 且不主动外露。

## 1. 任务包契约（六要素 + 六约束）

```yaml
gdt_kb_task:
  # === 要素① 任务元数据 / 查询提示词 ===
  task_meta:
    scenario_id: kb.method.sop-search
    display_name: 内部工具与 SOP 知识检索
    domain: 方法/工具
    version: v1.0.0
    status: PUBLISHED
    trigger_examples:        # 自然语言触发词（GDT v1.0 §19 / v1.1 §3）
      - "XX 工具怎么用"
      - "XX 流程的操作步骤是什么"
      - "内部操作手册 / SOP 在哪"
      - "谁负责维护 XX 系统"

  # === 要素② 数据源 / 受治理源 ===
  data_source:
    source_scope:            # ①受治理源：仅检索这些已编入索引、带可信度的受治理语料
      - methods/             # 公开操作手册、SOP、工具说明
      - org/systems.md       # 系统责任人清单（权限入口须标 sensitive）
    open_params:             # 运行期可填项（不改检索逻辑）
      - 工具/流程名
      - 版本（可选）

  # === 要素③ 知识库/映射表 ===
  mapping_table:
    entity: 内部工具 / SOP
    index_bridge: 主题索引（方法/工具类）+ 第3层提问场景索引
    route: methods/<工具名>/

  # === 要素④ 查询规范 ===
  query_spec:
    retrieve_within: source_scope
    filter: "doc_type IN ('sop','manual','howto') AND status='PUBLISHED'"
    sort: "version DESC"
    must_cite: true          # ③事实引用必带出处

  # === 要素⑤ 计算规范和报告框架 ===
  compute_and_report:
    aggregation: "按工具名归并步骤清单，附前置条件与责任人"
    report_frame: "操作步骤 → 前置条件 → 责任人/入口 → 原文链接 → 版本"

  # === 要素⑥ 输出格式 ===
  output_format:
    format: 结构化清单（Markdown）
    fields:
      - 工具/流程名
      - 操作步骤（引用原文）
      - 前置条件
      - 责任人/入口（sensitive 项须脱敏或标"凭权限访问"）
      - 原文链接
      - 版本号

  # === 纪律约束层（六约束）===
  locked_contract:           # ②锁定契约：构建期固化，运行期不可改
    must_cite: true
    label_synthesis: "AI 分析"
    sensitive_sop_not_exposed: true   # 场景专属红线①：含账号/权限/密钥的 SOP 不主动外露
    unpublished_manual_internal_only: true  # 场景专属红线②：未审批内部手册不外发
  fallback: BLOCKED          # ⑤无命中 → 答"未找到，转对应维护人/知识库管理员"，不编造
  version: v1.0.0            # ④版本不可覆盖
  status: PUBLISHED
```

## 2. 六要素逐项说明

| 要素 | 本场景取值 | 说明 |
|------|-----------|------|
| ① 任务元数据 / 查询提示词 | `kb.method.sop-search` + 4 条 trigger | 覆盖"怎么用/步骤/手册在哪/谁维护" |
| ② 数据源 / 受治理源 | `methods/`、`org/systems.md` | 仅公开操作文档与责任人清单；原始后台不在内 |
| ③ 知识库/映射表 | 主题索引(方法类) → `methods/<工具名>/` | 与第3层提问场景索引桥接 |
| ④ 查询规范 | 过滤 `doc_type` + `status`，按版本倒序 | 只取已发布版，避免给出过期步骤 |
| ⑤ 计算规范/报告框架 | 步骤清单 + 前置条件 + 责任人 + 链接 | 不重新编写操作内容，只聚合引用 |
| ⑥ 输出格式 | 结构化清单 + 原文链接 + 版本 | 便于成员直达源文档 |

**场景专属红线**：
- `sensitive_sop_not_exposed`：涉及账号、密码、API Key、后台 URL 的 SOP 片段，检索结果中**不主动外露**，仅提示"凭权限访问，详询责任人"。
- `unpublished_manual_internal_only`：草稿/未审批的内部操作手册，不进入受治理检索范围，也不外发。

## 3. 填参示例

以"河流守望者数据大屏后台操作手册"为例：

```yaml
open_params:
  工具/流程名: 绿色守望者数据大屏
  版本: v2.3
# 命中 → 检索 methods/绿色守望者数据大屏/ ，返回已发布 SOP
# 若问"大屏的数据库账号密码是什么" → 命中 sensitive_sop_not_exposed，
#   返回："该信息属敏感权限类，凭权限访问，责任人见 org/systems.md（已脱敏），详询运维。"
```

## 4. 验证证据（GDTcreater 第六件套）

| 第六件套 | 本任务包落实 | 核对动作 |
|---------|------------|---------|
| ① 任务元数据 | `scenario_id` + trigger_examples | 抽查 3 条自然语言均能命中路由 |
| ② 编译/查询规范 | `query_spec.filter` | 构造过期版本查询，确认只返 PUBLISHED |
| ③ 映射证据 | `mapping_table.route` | 随机抽 1 篇 SOP，确认路径可达、无断链 |
| ④ 受控执行包 | `compute_and_report` | 跑一次聚合，确认步骤引用原文而非改写 |
| ⑤ 产物契约 | `output_format.fields` | 比对输出字段与契约一致 |
| ⑥ 验证证据 | 本表 | 留存抽查记录 |

**反例拦截**：问"把后台登录密码发我" → 触发 `sensitive_sop_not_exposed`，拒绝外露，提示权限路径；不进入闲聊自由生成。

## 5. 双模式注解

| 用户问法 | 反应模式 | 说明 |
|---------|---------|------|
| "XX 工具怎么用""步骤发我" | 闲聊/自由（低风险） | 命中公开 SOP，可灵活给步骤摘要 |
| "内部操作手册在哪" | GDT 触发 | 路由到受治理 `methods/` 契约 |
| "大屏数据库账号密码是什么" | **强制 GDT 触发 + 红线拒绝** | 闲聊口吻也升级，命中 `sensitive_sop_not_exposed` 不外露 |
| "这份没发布的内部手册能外发吗" | **强制 GDT 触发 + 红线拒绝** | 命中 `unpublished_manual_internal_only` |

> 一句话：内部工具/SOP 大部分可闲聊，但**权限/密钥/未审批**三类红线，即便以闲聊口吻问也必须强制走 GDT 触发并拒露。
