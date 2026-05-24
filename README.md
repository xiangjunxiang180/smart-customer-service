# 智能人工客服小程序

基于Python FastAPI和通义千问API开发的智能客服系统，支持RAG知识库检索、自动问答和人工客服转接功能。

## 功能特点

- ✅ **智能问答**：基于RAG技术，从知识库中检索相关信息生成专业回答
- ✅ **人工客服**：支持一键转接人工客服
- ✅ **聊天历史**：自动保存用户聊天记录，刷新页面不丢失
- ✅ **常见问题**：预设常见问题列表，点击即可快速解答
- ✅ **微信小程序**：原生微信小程序前端界面，无需下载安装
- ✅ **向量检索**：使用FAISS高效向量检索引擎，毫秒级响应
- ✅ **大模型集成**：集成通义千问API，支持多种模型切换
- ✅ **本地部署**：完全本地运行，数据安全可控

## 技术栈

| 模块 | 技术选型 |
|------|----------|
| 后端框架 | Python 3.10+, FastAPI |
| 数据库 | SQLite（轻量级嵌入式数据库） |
| 向量引擎 | FAISS（Facebook AI Similarity Search） |
| 大模型 | 通义千问API (qwen-turbo) |
| 向量模型 | 通义千问文本向量模型 |
| 前端 | 微信小程序原生开发 |

## 快速开始

### 环境准备

1.  安装Python 3.10或更高版本（推荐3.11）
2.  注册阿里云账号并开通通义千问API服务
3.  在阿里云控制台获取你的通义千问API密钥
4.  安装微信开发者工具（用于运行和调试小程序）

### 后端部署
克隆仓库（将下面的用户名替换为你的GitHub用户名）：
    ```bash
    git clone https://github.com/你的GitHub用户名/smart-customer-service.git
    cd smart-customer-service/backend
安装所有依赖包：
pip install -r requirements.txt
# 通义千问API密钥（必填）
DASHSCOPE_API_KEY=你的通义千问API密钥

# 大模型配置（可选，默认使用qwen-turbo）
LLM_MODEL=qwen-turbo
VECTOR_MODEL=text-embedding-v1

# 服务器配置（可选）
HOST=0.0.0.0
PORT=8000

启动后端服务：
python main.py
验证服务是否正常运行：打开浏览器访问 http://localhost:8000/docs
你会看到 FastAPI 自动生成的 API 文档界面。

小程序部署
    打开微信开发者工具
    点击 "导入项目"，选择 frontend/智能客服小程序 目录
    AppID 选择你的测试号或正式小程序 AppID
    点击 "导入" 按钮
    打开 pages/index/index.js 文件，将所有的 http://localhost:8000 替换为你的后端服务地址
        本地开发：使用 http://你的本机IP:8000
        生产环境：使用你的公网域名
    点击右上角的 "编译" 按钮，小程序就会在模拟器中运行

项目结构
smart-customer-service/
├── backend/                     # 后端服务根目录
│   ├── data/                    # 数据目录（首次运行自动生成）
│   │   ├── chat.db              # SQLite数据库，存储所有用户聊天历史
│   │   ├── faiss_index.bin      # FAISS向量索引文件，自动生成
│   │   └── knowledge_base.txt   # 知识库文件，你需要编辑这个添加业务知识
│   ├── services/                # 核心业务服务模块
│   │   ├── llm_service.py       # 通义千问大模型调用服务
│   │   └── vector_service.py    # FAISS向量检索与索引构建服务
│   ├── .env                     # 环境变量配置文件（包含API密钥，不上传GitHub）
│   ├── main.py                  # FastAPI主程序，后端服务入口
│   └── requirements.txt         # Python依赖包列表
└── frontend/                    # 前端小程序根目录
    └── 智能客服小程序/
        ├── pages/               # 小程序页面目录
        │   └── index/           # 唯一页面：聊天主界面
        │       ├── index.js     # 页面逻辑与网络请求
        │       ├── index.wxml   # 页面结构与组件
        │       ├── index.wxss   # 页面样式
        │       └── index.json   # 页面局部配置
        ├── app.js               # 小程序全局入口文件
        ├── app.json             # 小程序全局配置（页面路由、窗口样式等）
        ├── app.wxss             # 小程序全局样式
        ├── project.config.json  # 项目公共配置（团队共享，上传GitHub）
        └── project.private.config.json  # 本地私有配置（个人设置，不上传）

API 接口说明
所有接口都可以在 http://localhost:8000/docs 中查看详细文档并进行测试。

接口地址	请求方法	说明
/api/chat	POST	发送消息，获取智能回答
/api/faq	GET	获取常见问题列表
/api/history/{user_id}	GET	获取指定用户的聊天历史

后续扩展方向：
    支持多轮对话上下文理解
    添加用户评价和满意度调查功能
    实现完整的客服工单系统
    添加后台管理面板和数据分析功能
    支持图片和语音输入
    集成更多大模型（GPT-4o、Claude 3 等）
    部署到云服务器实现公网访问
    支持多客服同时在线
