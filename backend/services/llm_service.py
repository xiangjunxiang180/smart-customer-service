import os
import dashscope
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        # 初始化通义千问客户端
        dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.model = os.getenv("LLM_MODEL", "qwen-turbo")
    
    def generate_response(self, user_query: str, relevant_docs: list) -> str:
        """根据用户问题和检索到的知识库内容生成专业回复"""
        system_prompt = """你是一个专业、友好、耐心的智能客服助手。
请严格根据提供的相关文档内容回答用户的问题。
如果相关文档中没有找到答案，请如实告知用户，并建议用户转人工客服。
绝对不要编造信息，不要回答与客服无关的问题。
回答要简洁明了，通俗易懂。"""
        
        context = "\n\n".join([f"相关信息{i+1}：{doc}" for i, doc in enumerate(relevant_docs)])
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"用户问题：{user_query}\n\n{context}"}
        ]
        
        try:
            response = dashscope.Generation.call(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            
            if response.status_code == 200:
                return response.output.text.strip()
            else:
                return f"抱歉，我现在遇到了一些问题，请稍后再试或转人工客服。错误代码：{response.status_code}"
        except Exception as e:
            return f"抱歉，我现在遇到了一些问题，请稍后再试或转人工客服。错误信息：{str(e)}"
