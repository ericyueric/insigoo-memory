# insigoo-memory — 社会组织 SAG 知识库架构师（开源版 v2.0.0 · MIT）

帮社会组织把散落的历史资料，变成"建得起来、查得到、管得住、说得清"的专属 SAG 知识库。

三件事：**建库（SAG）× 编译（公益项目-披露标准 + GDT-Core 要素+纪律）× 诊断（SIA）**。

---

## 一、自包含度（重点）

✅ **本技能已自带全部必要资源**，安装即可独立运行，无需任何其他 insigoo 私有技能：

- `references/wiki_structure.md` — 知识库目录骨架
- `references/llm_wiki_standard.md` — LLM Wiki 五大编写原则
- `references/three_layer_index.md` — 三层索引标准（含受治理查询场景索引 v1.1）
- `references/knowledge_index_template.md` — 主索引模板
- `references/maintenance_guide.md` — 编译与维护规范（含双模式检索）
- `references/gdt_kb_samples/` — **15 个示范任务包**（六要素+六约束+双模式，覆盖 15 类高频场景）
- `references/gdt_design.md` — GDT-Core 通用治理内核设计（要素结构层 + 纪律约束层 + 双模式）
- `references/sia_core.md` — SIA 逻辑自洽体检核心检查点（L1：7 原则 + 三A三力四维 + 三模式 + 10 项快检 + 成熟度；对齐 insigoo-sia v1.2.0 / MIT）
- `references/sag_api.md` — SAG 语义检索 API 调用契约（/health、/api/sources、/search、/ingest 端点 + 启动 + 配置）

⚙️ **可选增强依赖**（安装后部分能力增强，不安装也能完整跑通三件事）：

| 依赖 | 增强内容 | 获取方式 |
|------|---------|---------|
| `insigoo-sag` | SAG 引擎完整部署脚本 + 满月 Lint（能力一技术底座） | 开源 `github.com/ericyueric/insigoo-sag` |
| `insigoo-knowledge-base` | LLM Wiki 与三层索引扩展标准（本技能已内联核心） | 开源 `github.com/ericyueric/insigoo-knowledge-base` |
| `insigoo-sia` | SIA 完整 L1/L2/L3 框架（本技能 `sia_core.md` 已内联 L1 核心；指标量化 L2 / 价值核算 L3 以该开源技能为准） | 开源 `github.com/ericyueric/insigoo-sia` |
| `GDTcreater` | GDT-DB 六件套向导（本技能 2.5.4 已含 KB 映射卡，可手动建包） | ⚠️ 未开源（insigoo 内部技能），本技能不依赖 |


---

## 二、安装

1. 将本目录（`insigoo-memory/`）整体放入 WorkBuddy 技能目录：
   - 用户级：`~/.workbuddy/skills/insigoo-memory/`
   - 或项目级：`<项目>/.workbuddy/skills/insigoo-memory/`
2. 重启 WorkBuddy 或刷新技能索引。
3. （可选）如需增强能力，另行安装上述可选依赖技能。
4. 在对话中说出触发词（如"帮我搭知识库""做 SAG 知识库""按披露标准整理资料""SIA 诊断"）即加载本技能。

---

## 三、三大能力速览

| # | 能力 | 关键产出 | 是否依赖外部技能 |
|---|------|---------|----------------|
| 能力一 | 搭建组织 SAG 知识库 | LLM Wiki + 三层索引 + 维护规范 | 否（SAG 部署指引内联；完整脚本来自可选依赖） |
| 能力二 | 按公益披露标准编译历史资料 | 7 类索引 + 受治理查询场景索引（GDT-KB 六要素+六约束）+ 编译标准 | 否（15 样本与 GDT 设计自带） |
| 能力三 | 基于 SIA 诊断组织知识 | 知识健康度卡片 + 优化建议（P0/P1/P2） | 否（SIA 核心检查点自带） |

---

## 四、最小使用流程

```
1. [建库]  按 references/wiki_structure.md 建 wiki/ 骨架 → 套 llm_wiki_standard.md 规范
2. [编译]  资产盘点（7 类）→ 逐类重写为 LLM Wiki → 填 three_layer_index.md（第 3 层用 GDT-KB 契约）
3. [索引]  高频查询场景抄 references/gdt_kb_samples/ 模板，写受治理查询契约
4. [诊断]  抽代表项目 → 按 sia_core.md 跑 L1 逻辑自洽体检 → 出知识健康度卡片与整改清单
5. [验收]  自然语言提问能正确召回；披露缺口与知识盲区可见、可整改
```

---

## 五、目录结构

```
insigoo-memory/
├── SKILL.md                      # 技能主文件（能力一/二/三 + GDT 双层 + 双模式 + 硬约束）
├── LICENSE                       # MIT 开源许可
├── README.md                     # 本文件
└── references/
    ├── wiki_structure.md
    ├── llm_wiki_standard.md
    ├── three_layer_index.md
    ├── knowledge_index_template.md
    ├── maintenance_guide.md
    ├── gdt_design.md              # GDT-Core 设计说明（自带，替代外部设计稿）
    ├── sia_core.md                # SIA 核心检查点（自带，替代外部技能硬依赖）
    └── gdt_kb_samples/            # 15 示范任务包 + README 索引表
```

---

## 六、授权

免费开源技能，采用 **MIT 许可**：可自由使用、修改、分发与商用，须保留版权与许可声明。SIA 内联仅 L1 层，L2/L3 以开源 `insigoo-sia`（MIT）为准。

*insigoo 因思阁 · 让每一个社会组织都有自己的、说得清也管得住的 SAG 知识库*

## 相关开源仓库

- [insigoo-knowledge-architect](https://github.com/ericyueric/insigoo-knowledge-architect) — 基于本方法论的「知识库架构师」通用 dsh agent 角色（开源 MIT，可适配任意行业组织）。
- [insigoo-agents](https://github.com/ericyueric/insigoo-agents) — insigoo OS 标准 agent 角色配置（开源 MIT）：总编排 / 数据分析师 / SIA 诊断 / 课程开发 四件套 + dsh preset 生成器。