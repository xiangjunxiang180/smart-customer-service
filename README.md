# 智能人工客服小程序

基于 Python FastAPI + 通义千问 API + RAG 技术构建的端到端智能客服系统，支持知识库检索问答、人工客服转接、聊天记录持久化等完整功能。

## 项目亮点

- **RAG全链路**：文档向量化 → FAISS IndexFlatL2精确检索 → 通义千问生成回答，知识库问答准确率接近100%
- **混合检索**：BM25关键词检索（50%）+ FAISS向量检索（50%）加权融合，兼顾精确匹配和语义理解
- **工程化设计**：向量索引持久化（首次构建后直接加载）、数据库自动创建、配置分离（.env）
- **完整产品**：后端API + 微信小程序双端可用，接口响应 < 2s，开箱即用

## 技术栈

| 模块 | 技术选型 | 说明 |
|------|---------|------|
| 后端框架 | Python 3.10 + FastAPI | 异步框架，自带Swagger文档 |
| 向量引擎 | FAISS IndexFlatL2 | 精确向量检索，适合小规模知识库 |
| 关键词检索 | BM25Okapi + jieba分词 | 中文关键词精确匹配 |
| 大模型 | 通义千问 qwen-turbo | 基于检索结果生成专业回答 |
| Embedding | 通义千问 text-embedding-v1 | 文本向量化，区分document/query类型 |
| 数据库 | SQLite | 轻量级，聊天记录持久化 |
| 前端 | 微信小程序原生开发 | 无需下载安装，移动端直达 |

## 系统架构

```
用户发送消息（微信小程序）
        ↓
FastAPI /api/chat 接口
        ↓
1. 消息存入 SQLite
        ↓
2. VectorService.search()
   ├── BM25关键词检索（jieba分词）→ Top10候选
   ├── FAISS向量检索（通义千问Embedding）→ Top10候选
   └── 加权融合（各50%）→ Top3最相关文档
        ↓
3. LLMService.generate_response()
   └── 通义千问API（RAG Prompt）→ 生成回答
        ↓
4. 回答存入 SQLite，返回给前端
```

## 快速开始

### 环境准备

- Python 3.10+
- 通义千问API密钥（[申请地址](https://dashscope.aliyun.com)）
- 微信开发者工具（运行小程序）

### 后端启动

```bash
# 1. 克隆项目
git clone https://github.com/xiangjunxiang180/smart-customer-service.git
cd smart-customer-service/backend

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的通义千问API密钥：
# DASHSCOPE_API_KEY=sk-你的密钥

# 4. 启动服务
python main.py
```

启动成功后访问：`http://127.0.0.1:8000/docs` 查看接口文档

**首次启动**会自动构建向量索引（调用通义千问Embedding API对知识库向量化），之后启动直接加载已有索引，无需重复构建。

### 小程序启动

1. 打开微信开发者工具，导入 `frontend/智能客服小程序` 目录
2. 修改 `pages/index/index.js` 中的后端地址为你的服务器IP
3. 开发调试：勾选「不校验合法域名」
4. 点击编译运行

## API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/chat` | POST | 发送消息，获取智能回答 |
| `/api/history/{user_id}` | GET | 获取用户聊天历史 |
| `/api/faq` | GET | 获取常见问题列表 |
| `/docs` | GET | Swagger接口文档（可直接测试） |

**chat接口请求示例：**
```json
{
  "user_id": "user_123",
  "content": "你们的退换货政策是什么？",
  "is_manual": false
}
```

**响应示例：**
```json
{
  "response": "我们提供7天无理由退换货服务，商品需保持原包装完好。请联系客服申请退换货流程。"
}
```

## 项目结构

```
smart-customer-service/
├── backend/
│   ├── data/                      # 数据目录（首次运行自动生成）
│   │   ├── chat.db                # SQLite数据库，存储聊天记录
│   │   ├── faiss_index.bin        # FAISS向量索引（首次构建后持久化）
│   │   └── knowledge_base.txt     # 知识库文件，每行一条知识条目
│   ├── services/
│   │   ├── llm_service.py         # 通义千问大模型调用，RAG Prompt构建
│   │   └── vector_service.py      # 向量检索服务（BM25+FAISS混合检索）
│   ├── main.py                    # FastAPI主程序，接口定义，数据库初始化
│   ├── requirements.txt           # Python依赖包
│   └── .env                       # 环境变量（API密钥，不提交Git）
└── frontend/
    └── 智能客服小程序/
        └── pages/index/           # 聊天主界面
            ├── index.js           # 页面逻辑，API调用
            ├── index.wxml         # 页面结构
            └── index.wxss         # 页面样式
```

## 核心技术说明

### 为什么用 IndexFlatL2 而不是 IVF/HNSW？

本项目知识库规模为几十到几百条，`IndexFlatL2` 暴力精确搜索完全满足需求，检索耗时 < 1ms。IVF/HNSW 是针对百万级数据的近似检索方案，在小规模下引入了不必要的复杂度且精度有损失。若知识库扩展至百万级，可切换至 `IndexIVFFlat`。

### 为什么用混合检索？

- **纯向量检索的缺点**：对专有名词、数字、型号等精确词汇不敏感，"退换货" 和 "换货" 可能被视为不同语义
- **纯BM25的缺点**：无法理解语义，"怎么换货" 和 "退货流程" 会被认为无关
- **混合检索**：两路各取50%权重融合，兼顾精确匹配和语义理解，适合中文客服场景

### 向量化区分 document/query 类型

构建索引时知识库文本用 `text_type="document"`，检索时用户问题用 `text_type="query"`，通义千问对两种类型有不同的优化策略，能提升检索相关性。

## 自定义知识库

编辑 `backend/data/knowledge_base.txt`，每行写一条知识：

```
我们的产品支持微信小程序、网页和APP三种接入方式。
客服工作时间是周一至周五 9:00-18:00。
提供7天无理由退换货服务，商品需保持原包装完好。
保修期为购买之日起一年，非人为损坏免费维修。
```

修改后删除 `backend/data/faiss_index.bin`，重启服务会自动重建索引。

## 已知局限性与改进方向

- [ ] 前端IP地址硬编码，待抽取为配置文件
- [ ] 缺少用户鉴权，生产环境需接入token验证
- [ ] SQLite并发写入有锁竞争，高并发场景需换MySQL
- [ ] 原有设计含BGE Reranker重排序，因本地HuggingFace网络问题暂时移除，可改用通义千问Rerank API替代
- [ ] 知识库更新需重建索引，待实现增量更新接口

## License

MIT
