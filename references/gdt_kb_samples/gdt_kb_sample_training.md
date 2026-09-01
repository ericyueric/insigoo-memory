# GDT-KB 示范任务包：培训 / 能力建设项目记录检索

> 本文件是 `insigoo-memory` 技能 + `insigoo-knowledge-base` 三层索引 v1.1「受治理查询场景索引」的**可运行示范任务包**之一。
> 用法：复制本文件，替换 `<...>` 占位符与 `open_params` 实际值，即可落成本组织自己的 GDT-KB 任务包。
> 结构遵循 GDT-Core「要素结构层（六要素）+ 纪律约束层（六约束）」双层，并在 `locked_contract` 中写入本场景专属红线。

## 0. 这个任务包解决什么

组织有内部培训、能力建设工作坊、外部研修等记录。常见查询："XX 培训记录""某员工/志愿者参加了哪些培训""内训覆盖率"。
这类查询**涉及学员个人身份信息（PII）与培训评估结果**，敏感度高——个人成绩、参训表现不得外泄，学员姓名/联系方式须脱敏。

本任务包把"培训/能力建设记录"做成受治理契约：默认只返回**汇总级**培训档案（项目名称、时间、覆盖率），涉及具体个人的记录须权限校验 + PII 脱敏。

## 1. 任务包契约（六要素 + 六约束）

```yaml
gdt_kb_task:
  # === 要素① 任务元数据 / 查询提示词 ===
  task_meta:
    scenario_id: kb.training.record-search
    display_name: 培训与能力建设项目记录检索
    domain: 培训/能力建设
    version: v1.0.0
    status: PUBLISHED
    trigger_examples:        # 自然语言触发词（GDT v1.0 §19 / v1.1 §3）
      - "XX 培训的记录 / 材料在哪"
      - "某员工 / 志愿者参加过哪些培训"
      - "内部培训覆盖率多少"
      - "能力建设工作坊的产出"

  # === 要素② 数据源 / 受治理源 ===
  data_source:
    source_scope:            # ①受治理源
      - training/            # 培训项目档案、汇总记录
      - hr/ (仅参训关联，须权限)  # 人员-培训关联（PII 脱敏）
    open_params:             # 运行期可填项
      - 培训项目名
      - 人员（须权限）
      - 年份

  # === 要素③ 知识库/映射表 ===
  mapping_table:
    entity: 培训/能力建设记录
    index_bridge: 主题索引（培训类）+ 第3层提问场景索引
    route: training/<项目名>/

  # === 要素④ 查询规范 ===
  query_spec:
    retrieve_within: source_scope
    filter: "doc_type IN ('training_record','workshop_output') AND status='PUBLISHED'"
    sort: "date DESC"
    must_cite: true          # ③事实引用必带出处

  # === 要素⑤ 计算规范和报告框架 ===
  compute_and_report:
    aggregation: "汇总级：项目名称/时间/参训人数/覆盖率；个人级须权限+脱敏"
    report_frame: "培训项目 → 时间 → 参训规模 → 产出/证书 → 原文链接"

  # === 要素⑥ 输出格式 ===
  output_format:
    format: 汇总表（Markdown）
    fields:
      - 培训项目名称
      - 时间
      - 参训规模（汇总，禁个人 PII）
      - 产出/证书（原文引用）
      - 原文链接

  # === 纪律约束层（六约束）===
  locked_contract:           # ②锁定契约
    must_cite: true
    label_synthesis: "AI 分析"
    pii_masked: true              # 场景专属红线①：学员姓名/联系方式脱敏
    individual_score_not_exposed: true  # 场景专属红线②：个人培训成绩/评估禁外泄
    permission_check_required: true     # 场景专属红线③：查具体个人须权限校验
  fallback: BLOCKED          # ⑤无命中 → 答"未找到，转培训负责人"，不编造参训名单
  version: v1.0.0            # ④版本不可覆盖
  status: PUBLISHED
```

## 2. 六要素逐项说明

| 要素 | 本场景取值 | 说明 |
|------|-----------|------|
| ① 任务元数据 / 查询提示词 | `kb.training.record-search` + 4 条 trigger | 覆盖项目记录/个人参训/覆盖率/产出 |
| ② 数据源 / 受治理源 | `training/`、`hr/`(关联) | 仅受治理培训档案，原始报名系统不在内 |
| ③ 知识库/映射表 | 主题索引(培训类) → `training/` | 与第3层桥接 |
| ④ 查询规范 | 过滤 `doc_type` + `status` | 只取已发布培训档案 |
| ⑤ 计算规范/报告框架 | 汇总级聚合，个人级须权限+脱敏 | 防 PII 外泄 |
| ⑥ 输出格式 | 汇总表 + 原文链接 | 不输出个人明细 |

**场景专属红线**：
- `pii_masked`：学员姓名、手机、身份证等 PII 在输出中脱敏（如"张*"）。
- `individual_score_not_exposed`：个人培训成绩、评估反馈、表现评级不得外泄。
- `permission_check_required`：查询"某具体人员参训记录"须先校验查询者权限，无权限走 `fallback`。

## 3. 填参示例

以"2025 年志愿者能力建设工作坊"为例：

```yaml
open_params:
  培训项目名: 志愿者能力建设工作坊
  年份: 2025
# 命中 → 返回汇总：时间/参训人数/产出，PII 已脱敏
# 若问"张三这次培训考了多少分" → 命中 individual_score_not_exposed + permission_check_required，
#   无权限则返回 fallback，不泄露个人成绩
```

## 4. 验证证据（GDTcreater（未开源，本技能不依赖） 第六件套）

| 第六件套 | 本任务包落实 | 核对动作 |
|---------|------------|---------|
| ① 任务元数据 | `scenario_id` + trigger | 抽查命中路由 |
| ② 编译/查询规范 | `query_spec.filter` | 构造草稿查询，确认只返 PUBLISHED |
| ③ 映射证据 | `mapping_table.route` | 抽 1 项目，确认路径可达 |
| ④ 受控执行包 | `compute_and_report` | 跑聚合，确认个人级触发权限+脱敏 |
| ⑤ 产物契约 | `output_format.fields` | 比对字段一致（无 PII 字段） |
| ⑥ 验证证据 | 本表 | 留存 |

**反例拦截**：问"把参训志愿者手机号发我" → 触发 `pii_masked` + `permission_check_required`，拒绝，提示无权限/脱敏。

## 5. 双模式注解

| 用户问法 | 反应模式 | 说明 |
|---------|---------|------|
| "XX 培训工作坊产出在哪" | 闲聊/自由（低风险） | 汇总级公开产出，可灵活给 |
| "2025 培训覆盖率" | GDT 触发 | 路由受治理契约，返汇总 |
| "张三参训成绩多少" | **强制 GDT 触发 + 红线拒绝** | 闲聊口吻也升级，命中 PII/成绩红线 |
| "参训志愿者名单和电话" | **强制 GDT 触发 + 红线拒绝** | 命中 `pii_masked` 脱敏或拒露 |

> 一句话：培训记录汇总可闲聊，但**任何涉及具体个人 PII 或成绩**的问法，即便闲聊口吻也必须强制走 GDT 触发、脱敏并校验权限。
