from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sqlite3
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from services.llm_service import LLMService
from services.vector_service import VectorService

# 加载环境变量
load_dotenv()

# 全局服务变量
llm_service = None
vector_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理（FastAPI最新推荐方式）"""
    global llm_service, vector_service
    
    # 应用启动时执行
    print("正在初始化智能客服系统...")
    
    # 确保data文件夹存在
    os.makedirs("backend/data", exist_ok=True)
    
    # 初始化数据库
    conn = sqlite3.connect(
    "backend/data/chat.db",
    check_same_thread=False
    )
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        content TEXT NOT NULL,
        role TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_manual BOOLEAN DEFAULT FALSE
    )
    """)
    conn.commit()
    conn.close()
    print("数据库初始化完成")
    
    # 初始化服务
    llm_service = LLMService()
    vector_service = VectorService()
    
    # 初始化向量索引（添加错误处理）
    try:
        vector_service.init_index()
        print("向量知识库初始化完成")
    except Exception as e:
        print(f"向量知识库初始化警告：{str(e)}")
        print("系统将继续运行，但智能问答功能可能受限")
    
    print("智能客服系统启动成功！")
    yield
    
    # 应用关闭时执行
    print("正在关闭智能客服系统...")

app = FastAPI(
    title="智能客服API", 
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS（允许跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请替换为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型（定义API接收和返回的数据格式）
class Message(BaseModel):
    user_id: str
    content: str
    is_manual: bool = False

# 数据库连接函数（添加线程安全参数）
def get_db():
    conn = sqlite3.connect(
        "backend/data/chat.db",
        check_same_thread=False  # 允许跨线程使用连接
    )
    try:
        yield conn
    finally:
        conn.close()


# 核心聊天接口
@app.post("/api/chat")
async def chat(message: Message, db=Depends(get_db)):
    """处理用户聊天请求"""
    try:
        # 保存用户发送的消息
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO chat_messages (user_id, content, role) VALUES (?, ?, ?)",
            (message.user_id, message.content, "user")
        )
        db.commit()
        
        if message.is_manual:
            # 人工客服模式，返回等待提示
            response = "已为您转接人工客服，请稍候..."
        else:
            # 智能问答模式：先检索知识库，再调用大模型生成回复
            relevant_docs = vector_service.search(message.content)
            response = llm_service.generate_response(message.content, relevant_docs)
        
        # 保存助手的回复
        cursor.execute(
            "INSERT INTO chat_messages (user_id, content, role, is_manual) VALUES (?, ?, ?, ?)",
            (message.user_id, response, "assistant", message.is_manual)
        )
        db.commit()
        
        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 获取用户聊天历史接口
@app.get("/api/history/{user_id}")
async def get_chat_history(user_id: str, db=Depends(get_db)):
    """获取指定用户的所有聊天记录"""
    cursor = db.cursor()
    cursor.execute(
        "SELECT content, role, timestamp, is_manual FROM chat_messages WHERE user_id = ? ORDER BY timestamp",
        (user_id,)
    )
    messages = cursor.fetchall()
    
    history = []
    for msg in messages:
        history.append({
            "content": msg[0],
            "role": msg[1],
            "timestamp": msg[2],
            "is_manual": msg[3]
        })
    
    return {"history": history}

# 获取常见问题列表接口
@app.get("/api/faq")
async def get_faq():
    """获取预设的常见问题列表"""
    faq_list = [
        {"question": "如何注册账号？", "answer": "点击首页右上角的注册按钮，填写手机号和验证码即可完成注册。"},
        {"question": "忘记密码怎么办？", "answer": "在登录页面点击'忘记密码'，通过手机号验证后重置密码。"},
        {"question": "如何联系人工客服？", "answer": "在聊天界面点击右上角的'转人工'按钮，我们的客服人员会尽快为您服务。"}
    ]
    return {"faq": faq_list}

# 程序入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
