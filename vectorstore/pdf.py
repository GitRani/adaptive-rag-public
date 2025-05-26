from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Annotated
from langchain_community.vectorstores import FAISS
from langchain_anthropic import ChatAnthropic
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PDFRetrievalChain():
    def __init__(self, search_num, source_uris: Annotated[List[str], "Source URI List"]):
        self.source_uris = source_uris
        self.search_num = search_num


# PDF 파일을 열어서 각 페이지나 블록을 '문서 단위 객체'로 만들어 반환해요.
    def load_documents(self, source_uris: List[str]):
        docs = []
        for source_uri in source_uris:
            loader = PDFPlumberLoader(source_uri)
            #  Document(page_content="1페이지의 텍스트입니다", metadata={...}), 
            # 그 결과를 docs 리스트에 **누적해서 확장(extend)**하는 거예요.
            docs.extend(loader.load())

        return docs
    

    def create_text_splitter(self):
        return RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    
    
    def split_documents(self, docs, text_splitter):
        """text splitter를 사용하여 문서를 분할합니다."""
        # split_documents는 부모 TextSplitter의 메소드다.
        return text_splitter.split_documents(docs)

    def create_embedding(self):
        # return OpenAIEmbeddings(model="text-embedding-3-small")
        embed = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
        logger.info(f"[DEBUG] embedding 객체 타입: {type(embed)}")
        # AttributeError: 'SentenceTransformer' object has no attribute 'embed_documents' 에러 때문에.. HuggingFaceEmbedding
        return embed
    

    def create_vectorstore(self, split_docs):
        # from_documents()가 FAISS, Milvus, Weaviate 등 거의 모든 벡터DB에 있습니다.
        # 바로 document 객체 때려박아도 됨.
        return FAISS.from_documents(
            documents=split_docs, embedding=self.create_embedding()
        )

    def create_retriever(self, vectorstore):
        # MMR을 사용하여 검색을 수행하는 retriever를 생성합니다.
        dense_retriever = vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": self.search_num}
        )
        return dense_retriever
    

    def create_model(self):
        # return ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
        # 현재 파일 (base.py) 기준으로 .env 로드
        load_dotenv(dotenv_path=Path(__file__).parent / ".env")
        # ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

        return ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)
    

    def create_chain(self):
        docs = self.load_documents(self.source_uris)
        # 여기까지 오면 split_docs에는 쪼개진 텍스트가 리스트 형태로 저장이 된다. 
        # Document 객체의 리스트로 저장됨.
        split_docs = self.split_documents(docs, self.create_text_splitter())
        # 벡터 설정값들을 넣어 준비시킴 (유사도, 10개 검색..)
        return self.create_retriever(self.create_vectorstore(split_docs))