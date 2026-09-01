# GDT-KB 示范任务包：物资 / 资产 / 票据台账检索

> 本文件是 `insigoo-memory` 技能 + `insigoo-knowledge-base` 三层索引 v1.1「受治理查询场景索引」的**可运行示范任务包**之一。
> 用法：复制本文件，替换 `<...>` 占位符与 `open_params` 实际值，即可落成本组织自己的 GDT-KB 任务包。
> 结构遵循 GDT-Core「要素结构层（六要素）+ 纪律约束层（六约束）」双层，并在 `locked_contract` 中写入本场景专属红线。

## 0. 这个任务包解决什么

公益组织有设备资产、捐赠物资、财务票据等台账。成员/审计常问"XX 设备状态""捐赠物资入库多少""某发票/票据在哪"。
这类查询**涉及具体数字（数量、金额）**，与财务披露同属"数字禁推断"高危区——任何估算、四舍五入后的再加工都可能导致账实不符。

本任务包把"物资/资产/票据台账"做成受治理契约：数字**必须引用源台账字段、不得推断**，处置中资产/票据须标状态，确保审计可溯源。

## 1. 任务包契约（六要素 + 六约束）

```yaml
gdt_kb_task:
  # === 要素① 任务元数据 / 查询提示词 ===
  task_meta:
    scenario_id: kb.asset.ledger-search
    display_name: 物资/资产/票据台账检索
    domain: 资产/物资
    version: v1.0.0
    status: PUBLISHED
    trigger_examples:        # 自然语言触发词（GDT v1.0 §19 / v1.1 §3）
      - "XX 设备在哪、什么状态"
      - "捐赠物资入库台账"
      - "某笔发票 / 票据在哪里"
      - "截至某时点的资产清单"

  # === 要素② 数据源 / 受治理源 ===
  data_source:
    source_scope:            # ①受治理源
      - assets/              # 资产台账
      - finance/invoices/     # 票据台账
      -物资台账（如 org/inventory/）
    open_params:             # 运行期可填项
      - 资产/物资类别
      - 年份或时点

  # === 要素③ 知识库/映射表 ===
  mapping_table:
    entity: 物资/资产/票据
    index_bridge: 主题索引（资产类）+ 第3层提问场景索引
    route: assets/ 或 finance/invoices/

  # === 要素④ 查询规范 ===
  query_spec:
    retrieve_within: source_scope
    filter: "category = <类别> AND (status IN ('in_stock','in_use','disposed') OR doc_type='invoice')"
    sort: "record_date DESC"
    must_cite: true          # ③事实引用必带出处（含台账编号）

  # === 要素⑤ 计算规范和报告框架 ===
  compute_and_report:
    aggregation: "按类别归并台账条目，数量/金额严格取源字段 SUM，不二次估算"
    report_frame: "条目 → 数量/金额(引源) → 状态 → 凭证链接 → 时点"

  # === 要素⑥ 输出格式 ===
  output_format:
    format: 台账表（Markdown 表格）
    fields:
      - 资产/物资/票据编号
      - 名称
      - 数量/金额（引源字段，禁估算）
      - 状态（在库/在用/处置中）
      - 凭证链接
      - 记录时点

  # === 纪律约束层（六约束）===
  locked_contract:           # ②锁定契约
    must_cite: true
    label_synthesis: "AI 分析"
    number_no_inference: true   # 场景专属红线①：数量/金额禁推断、须精确引源
    disposed_asset_status_tag: true  # 场景专属红线②：处置中资产/票据须标 status
  fallback: BLOCKED          # ⑤无命中 → 答"未找到，转资产管理员/财务"，不编造数量
  version: v1.0.0            # ④版本不可覆盖
  status: PUBLISHED
```

## 2. 六要素逐项说明

| 要素 | 本场景取值 | 说明 |
|------|-----------|------|
| ① 任务元数据 / 查询提示词 | `kb.asset.ledger-search` + 4 条 trigger | 覆盖设备/物资/票据/时点清单 |
| ② 数据源 / 受治理源 | `assets/`、`finance/invoices/`、`org/inventory/` | 仅受治理台账，原始采购系统不在内 |
| ③ 知识库/映射表 | 主题索引(资产类) → `assets/` 等 | 与第3层桥接 |
| ④ 查询规范 | 按类别+状态过滤，按记录日期倒序 | 只取台账真实字段 |
| ⑤ 计算规范/报告框架 | 数量/金额严格取源 SUM，不二次估算 | 防账实不符 |
| ⑥ 输出格式 | 台账表 + 编号 + 状态 + 凭证链接 | 审计可溯源 |

**场景专属红线**：
- `number_no_inference`：任何数量、金额**必须引源台账字段**，不得"大约""估算""四舍五入后再加总"式的推断。
- `disposed_asset_status_tag`：处置中/已报废资产、作废票据须明确标 `status`，不得与在用资产混列。

## 3. 填参示例

以"2025 年捐赠物资入库台账"为例：

```yaml
open_params:
  资产/物资类别: 捐赠物资
  年份或时点: 2025
# 命中 → 检索 org/inventory/ ，返回按类别归并的台账，数量取源字段 SUM
# 若问"大概捐了多少件" → 触发 number_no_inference，返回精确台账合计并附凭证，不答"约XXX件"
```

## 4. 验证证据（GDTcreater（未开源，本技能不依赖） 第六件套）

| 第六件套 | 本任务包落实 | 核对动作 |
|---------|------------|---------|
| ① 任务元数据 | `scenario_id` + trigger | 抽查自然语言命中路由 |
| ② 编译/查询规范 | `query_spec.filter` | 构造跨状态查询，确认状态过滤生效 |
| ③ 映射证据 | `mapping_table.route` | 抽 1 条资产编号，确认台账可达 |
| ④ 受控执行包 | `compute_and_report` | 跑聚合，确认数量取源 SUM 非推断 |
| ⑤ 产物契约 | `output_format.fields` | 比对字段一致 |
| ⑥ 验证证据 | 本表 | 留存 |

**反例拦截**：问"物资价值总共多少（估算）" → 触发 `number_no_inference`，返回精确台账合计+凭证，拒绝估算口径。

## 5. 双模式注解

| 用户问法 | 反应模式 | 说明 |
|---------|---------|------|
| "XX 设备在哪" | GDT 触发 | 路由受治理台账契约 |
| "捐赠物资入库多少" | **强制 GDT 触发** | 涉及数字，命中 `number_no_inference` |
| "资产总价值大概多少" | **强制 GDT 触发 + 红线** | 闲聊口吻也升级，拒绝估算，返精确台账 |
| "处置掉的旧电脑清单" | GDT 触发 | 命中 `disposed_asset_status_tag` 标状态 |

> 一句话：资产/物资/票据与财务同属"数字禁推断"高危区，任何涉及数量金额的问法——即便闲聊口吻——都必须强制走 GDT 触发并引源。
