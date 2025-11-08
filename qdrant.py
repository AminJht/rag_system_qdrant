from typing import Optional, List
import uuid

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore as LCQdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


def make_id() -> str:
    """UUID معتبر برای Qdrant."""
    return str(uuid.uuid4())


class SimpleQdrant:
    """
    - اتصال به Qdrant
    - ساخت کالکشن COSINE با سایز 768
    - لود یک‌باره‌ی E5-base با کش ./models
    - افزودن متن + متادیتا (doc_id, keywords) با point_id = UUID
    - جستجو با boost اختیاری روی keywords (should)
    """
    _emb = None  # یک‌بار لود شود

    def __init__(self, collection: str = "docs_e5_base", url: str = "http://127.0.0.1:6333"):
        self.url = url
        self.collection = collection

        # 1) اتصال (هشدار نسخه را خاموش کن)
        self.client = QdrantClient(url=self.url, check_compatibility=False, timeout=60)

        # 2) تضمین کالکشن (768 برای e5-base، COSINE)
        try:
            self.client.get_collection(self.collection)
        except Exception:
            self.client.recreate_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )

        # 3) امبدینگ E5-base (normalize + cache)
        if SimpleQdrant._emb is None:
            SimpleQdrant._emb = HuggingFaceEmbeddings(
                model_name="intfloat/multilingual-e5-base",
                cache_folder="./models",
                encode_kwargs={"normalize_embeddings": True},
            )
        self.emb = SimpleQdrant._emb

        # 4) VectorStore (دقت کن: embedding نه embeddings)
        self.vs = LCQdrant(
            client=self.client,
            collection_name=self.collection,
            embedding=self.emb,
        )

    def add_item(self, *, text: str, doc_id: str, keywords: List[str]):
        """
        متن و متادیتا را ذخیره می‌کند.
        - text: متن اصلی چانک
        - doc_id: شناسه سند (str)
        - keywords: لیست کلمات کلیدی
        """
        chunk_id = make_id()  # UUID
        t = f"passage: {text}"  # پیشوند E5 برای اسناد
        meta = {"doc_id": doc_id, "chunk_id": chunk_id, "keywords": keywords}

        point_id = chunk_id  # فقط UUID → مورد تایید Qdrant
        self.vs.add_texts(texts=[t], metadatas=[meta], ids=[point_id])

    def search_db(
        self,
        query: str,
        k: int = 3,
        boost_keywords: Optional[List[str]] = None,
    ):
        """
        جستجو با E5 (پیشوند "query: ") + boost اختیاری روی متادیتای 'keywords'
        - boost_keywords: اگر لیستی از کلیدواژه بدهی، با فیلتر 'should' امتیاز نتایج دارای این کلمات ↑ می‌شود
          (نتایج دیگر حذف نمی‌شوند).
        """
        q = f"query: {query}"

        filter_arg = None
        if boost_keywords:
            should = [{"key": "keywords", "match": {"value": kw}} for kw in boost_keywords]
            filter_arg = {"should": should}

        return self.vs.similarity_search(query=q, k=k, filter=filter_arg)


def main():
    db=SimpleQdrant()
    res = db.search_db("حق و حقوق کارکنان", k=3, boost_keywords=["ویندوز"])
    print(type(res), len(res))
    print([type(x) for x in res])
    print(res[0].__dict__)

if __name__ == "__main__":
    main()

