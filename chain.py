# chain.py
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from llm_api import Llm
from hazm import Normalizer
from qdrant import SimpleQdrant

_normalizer = Normalizer()
_searcher = SimpleQdrant()
def start(text):
    
    llm = Llm()

    _in_dict=RunnableLambda(lambda i:{"text":i})
    _norm = RunnableLambda(lambda d:{"norm":_normalizer.normalize(d["text"])})
    # _query_biuld=RunnableLambda(lambda d:{"norm":d["norm"],"q_list":llm.query_decomposition(d["norm"])})
    # _emb = RunnableLambda(lambda d:{"norm":d["norm"],"emb":[_embedde.get_embedding(q_list) for q_list in json.loads(d["q_list"][d["q_list"].find("{"): d["q_list"].rfind("}")+1])]})
    # _db = RunnableLambda(lambda d:{"norm":d["norm"],"db":[_chromadb.search_embedding(emb_list) for emb_list in d["emb"]]})
    _db = RunnableLambda(lambda d:{"norm":d["norm"],"db":_searcher.search_db(query=d["norm"])})
    _llm = RunnableLambda(lambda d:llm.generate(d["norm"]," ".join(d["db"])))
    tap = RunnableLambda(lambda v: (v,show_meta(v))[0])
    # _j_extract=RunnableLambda(lambda d:)
    
    _chain = (
        RunnablePassthrough()
        | _in_dict | tap
        | _norm    | tap
        | _db      | tap
        | _llm     | tap
    )
    
    try:
        return _chain.invoke(text)
    except Exception as e:
        # پیغام کوتاه و کاربردی
        return f"[_chain error] {type(e).__name__}: {e}"
    
def show_meta(values):
    for v in values:  # value = لیست Documentها
        print("doc_id:", v.metadata.get("doc_id"))
        print("chunk_id:", v.metadata.get("chunk_id"))
        print("keywords:", v.metadata.get("keywords"))
        print("text:", v.page_content[:80], "...\n")

if __name__=="__main__":
    print(start("وظایف شرکت نفت چیست ؟"))
