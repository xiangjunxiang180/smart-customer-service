# 智能人工客服小程序

基于Python FastAPI和通义千问API开发的智能客服系统，支持RAG知识库检索、自动问答和人工客服转接功能。

## 功能特点

- ✅ **智能问答**：基于RAG技术，从知识库中检索相关信息生成专业回答
- ✅ **人工客服**：支持一键转接人工客服
- ✅ **聊天历史**：自动保存用户聊天记录
- ✅ **常见问题**：预设常见问题列表，快速解答用户疑问
- ✅ **微信小程序**：原生微信小程序前端界面
- ✅ **向量检索**：使用FAISS高效向量检索引擎
- ✅ **大模型集成**：集成通义千问API，支持多种模型

## 技术栈

- **后端**：Python 3.10+, FastAPI, SQLite, FAISS
- **前端**：微信小程序原生开发
- **大模型**：通义千问API (qwen-turbo)
- **向量模型**：通义千问文本向量模型

## 快速开始

### 环境准备

1.  安装Python 3.10或更高版本
2.  注册阿里云账号并开通通义千问API服务
3.  获取通义千问API密钥
（注：个人练习时Python版本3.8以上即可，API可以使用OPENAI,KIMI等有效API即可）

### 后端部署

1.  克隆仓库：
    ```bash
    git clone https://github.com/你的用户名/smart-customer-service.git
    cd smart-customer-service/backend
2. 安装依赖：
    ```bash
    pip install -r requirements.txt
3. 配置环境变量：
    在 backend 目录下创建 .env 文件，填写你的通义千问 API 密钥：
    DASHSCOPE_API_KEY=你的通义千问API密钥
    LLM_MODEL=qwen-turbo
4. 启动服务：
    python main.py
5. 访问 API 文档：http://localhost:8000/docs


项目结构
plaintext

├── backend/                     # 后端服务
│   ├── data/                    # 数据目录（自动生成）
│   ├── services/                # 服务模块
│   │   ├── llm_service.py       # 大模型服务
│   │   └── vector_service.py    # 向量检索服务
│   ├── .env                     # 环境变量配置（不上传）
│   ├── main.py                  # FastAPI主程序
│   └── requirements.txt         # 依赖包列表
└── frontend/                    # 前端小程序
    └── 智能客服小程序/
        ├── pages/               # 页面文件
        │   └── index/
        │       ├── index.js
        │       ├── index.wxml
        │       └── index.wxss
        ├── app.js               # 小程序入口
        ├── app.json             # 全局配置
        └── app.wxss             # 全局样式
