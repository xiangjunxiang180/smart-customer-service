import os
import numpy as np
import faiss
import dashscope
from dotenv import load_dotenv

load_dotenv()

class VectorService:
    def __init__(self):
        # 初始化通义千问客户端
        dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.embedding_model = "text-embedding-v1"
        self.index_path = "backend/data/faiss_index.bin"
        self.docs_path = "backend/data/knowledge_base.txt"
        self.index = None
        self.documents = []
        
        if not dashscope.api_key or dashscope.api_key == "your_api_key_here":
            raise ValueError("请在.env文件中填写正确的通义千问API密钥")
    
    def init_index(self):
        """初始化向量索引"""
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.docs_path, "r", encoding="utf-8") as f:
                    self.documents = [line.strip() for line in f.readlines() if line.strip()]
                print(f"成功加载现有向量索引，包含{len(self.documents)}条知识库条目")
                return
            except Exception as e:
                print(f"加载现有索引失败，将重新创建：{str(e)}")
        
        # 创建示例知识库
        if not os.path.exists(self.docs_path):
            print("未找到知识库文件，正在创建示例知识库...")
            sample_knowledge = [
                "我们的产品是一款智能客服系统，支持自动问答和人工客服转接功能。",
                "系统支持微信小程序、网页和APP等多种接入方式。",
                "我们的客服工作时间是周一至周五的9:00-18:00。",
                "如果您有紧急问题，可以拨打我们的客服热线：400-123-4567。",
                "我们提供7天无理由退换货服务，详情请查看官网的退换货政策。"
            ]
            with open(self.docs_path, "w", encoding="utf-8") as f:
                f.write("\n".join(sample_knowledge))
        
        # 加载知识库
        with open(self.docs_path, "r", encoding="utf-8") as f:
            self.documents = [line.strip() for line in f.readlines() if line.strip()]
        
        if not self.documents:
            raise ValueError("知识库文件为空，请添加至少一条知识条目")
        
        print(f"正在为{len(self.documents)}条知识库条目生成向量...")
        
        # 生成向量
        embeddings = []
        success_count = 0
        
        for i, doc in enumerate(self.documents):
            print(f"正在生成第{i+1}/{len(self.documents)}条向量...")
            try:
                response = dashscope.TextEmbedding.call(
                    model=self.embedding_model,
                    input=doc,
                    text_type="document"
                )
                
                if response.status_code == 200:
                    embeddings.append(response.output["embeddings"][0]["embedding"])
                    success_count += 1
                else:
                    print(f"警告：第{i+1}条生成失败，状态码：{response.status_code}")
            except Exception as e:
                print(f"警告：第{i+1}条生成失败，错误：{str(e)}")
        
        if success_count == 0:
            raise RuntimeError("所有知识库条目生成向量都失败了，请检查API密钥和网络连接")
        
        print(f"向量生成完成，成功{success_count}条，失败{len(self.documents)-success_count}条")
        
        embeddings = np.array(embeddings, dtype=np.float32)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        
        # 保存索引
        faiss.write_index(self.index, self.index_path)
        print(f"向量索引已保存到 {self.index_path}")
    
    def search(self, query: str, top_k: int = 3) -> list:
        """搜索相关知识库条目"""
        if not self.index:
            try:
                self.init_index()
            except Exception as e:
                print(f"搜索时初始化索引失败：{str(e)}")
                return []
        
        try:
            response = dashscope.TextEmbedding.call(
                model=self.embedding_model,
                input=query,
                text_type="query"
            )
            
            if response.status_code != 200:
                print("生成查询向量失败")
                return []
            
            query_vector = np.array([response.output["embeddings"][0]["embedding"]], dtype=np.float32)
            distances, indices = self.index.search(query_vector, top_k)
            
            results = []
            for i in indices[0]:
                if i < len(self.documents):
                    results.append(self.documents[i])
            
            return results
        except Exception as e:
            print(f"搜索时发生异常：{str(e)}")
            return []
