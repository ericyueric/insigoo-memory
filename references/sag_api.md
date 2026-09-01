# SAG 语义检索 API 调用参考（insigoo-memory 自带）

> 本文件内联 SAG 知识库引擎的核心 API 调用契约。使用者**不安装可选依赖 `insigoo-sag` 也能照此调通语义检索**——这是本技能「自包含」承诺的一部分。完整部署/运维脚本（WSL PostgreSQL 初始化、向量库迁移、满月 Lint（知识库质量巡检，insigoo 内部代号，可替换））仍见可选依赖。

## 1. 服务与默认地址

| 服务 | 默认地址 | 作用 |
|------|---------|------|
| SAG API | `http://127.0.0.1:4173` | 语义检索 / 文档入库 HTTP 服务 |
| Ollama | `http://127.0.0.1:11434` | 跑嵌入模型 `nomic-embed-text`（768 维）与 LLM `qwen2.5:7b` |
| PostgreSQL + pgvector | `127.0.0.1:5432` / 库 `sag_lite` | 存文档向量与元数据 |

> 地址/端口可在部署环境中调整；以下示例用默认地址。

## 2. 启动前提（三件套）

```bash
# ① 启动 Ollama（含嵌入模型）
ollama serve
# 验证：curl http://127.0.0.1:11434/api/tags → 返回含 nomic-embed-text 的模型列表

# ② 启动 PostgreSQL + pgvector（库 sag_lite，向量维度 768）
#    Postgres 侧：pgvector 扩展 + sag_lite 库已建（建库脚本见可选依赖 insigoo-sag）

# ③ 启动 SAG API 服务（源码部署位置依环境而定，以下为默认本地路径示例）
cd <sag 项目目录>
npx tsx src/index.ts
# 验证：curl http://127.0.0.1:4173/health → {"ok":true,"service":"sag"}
```

## 3. 四个核心端点

### 3.1 健康检查
`GET /health` → `{"ok":true,"service":"sag"}`

### 3.2 查文档源
`GET /api/sources` → 返回已注册文档源列表（含 `sourceId`），入库与检索按 `sourceId` 指定范围。

### 3.3 语义检索
`POST /search`

请求体：
```json
{
  "query": "某项目的全部披露文档",
  "sourceIds": ["governance", "proposal", "finance"],
  "strategy": "semantic"
}
```
- `query`：自然语言问题（SAG 自动用 `nomic-embed-text` 做嵌入，调用方无需自己嵌）
- `sourceIds`：受限检索的文档源（对应 2.1 七类索引区），不传则全库
- `strategy`：检索策略，`semantic` 为向量语义召回
- 响应：匹配文档列表（含相似度与出处/路径），具体字段以服务实际返回为准

> 这正是 2.4 受治理查询场景索引的运行时落点：`source_scope` → `sourceIds`，`question_examples` 对应的自然语言即 `query`。

### 3.4 文档入库
`POST /ingest`

请求体：
```json
{
  "title": "X 项目 2023 终期评估",
  "content": "（LLM Wiki 格式的文档全文）",
  "sourceId": "evaluation",
  "extract": true
}
```
- `title` / `content`：文档标题与正文
- `sourceId`：归入 2.1 七类之一
- `extract`：是否自动切分 / 建索引
- 批量入库对应 SKILL.md 1.3 的 `batch_ingest` 步骤：遍历 `wiki/` 下各 markdown，逐篇 `POST /ingest`

## 4. 典型调用流程（建库后跑通语义检索）

```
1. 启动 Ollama + PostgreSQL(pgvector) + SAG API（见 §2）
2. 把 wiki/ 下文档逐篇 POST /ingest（按 sourceId 归入七类）→ 向量入库
3. 对高频查询场景，POST /search（query + sourceIds）→ 召回带出处的文档
4. 验收：自然语言提问能正确召回（与 knowledge_index.md 三层索引一致）
```

## 5. 关键配置（.env 参考）

```
DATABASE_URL=postgres://sag:sag@127.0.0.1:5432/sag_lite
EMBEDDING_DIMENSIONS=768
EMBEDDING_MODEL=nomic-embed-text:latest
LLM_MODEL=qwen2.5:7b
LLM_BASE_URL=http://127.0.0.1:11434/v1
```

## 6. 边界说明

- 本文件给出**调用契约**（端点 + 请求体 + 流程），让客户能对接任意符合该契约的 SAG 部署；
- 源码构建、WSL PG 初始化、向量库迁移、满月 Lint（知识库质量巡检，insigoo 内部代号，可替换） 巡检等**部署级运维**见可选依赖 `insigoo-sag`；
- 若客户已有自建 SAG/向量检索服务，只要暴露等价 `/search`、`/ingest` 契约即可复用本技能的方法论。

---

*insigoo 因思阁 · 让每一个社会组织都有自己的、说得清也管得住的 SAG 知识库*
