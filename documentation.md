<div dir="rtl" align="right" style="text-align: right;">

# گزارش فنیِ مختصر: RAG با Qdrant

## 1) انتخاب پایگاه دادهٔ برداری: Qdrant

**کارایی جستجو و درج:** موتور HNSW با فیلترینگِ متادیتا «داخل دیتابیس»؛ قبل از ANN دامنه کوچک می‌شود ⇒ تأخیر کمتر و دقت بیشتر. درجِ پیوسته با WAL و پایداری دیسکی پایدار است.

**مقیاس‌پذیری و استقرار:** یک سرویس Docker سبک با Snapshot/WAL؛ در رشد داده، Sharding/Replication بومی بدون معماری پیچیده.

**پشتیبانی توسعه:** REST/gRPC، SDKهای پایتون/نود و اتصال مستقیم به LangChain/LlamaIndex؛ مستندات و انجمن فعال.  
**نتیجه:** تعادل عملی بین سرعت، استقرار ساده و تجربهٔ توسعه.

---

## 2) مدل‌سازی و اسکیما

برای هر چانک سه جزء ذخیره می‌شود:

### **Text Document (متن چانک):**  
متنِ تمیز و ساختارمند.

### **Embedding Vector:**  
امبدینگ همان چانک با intfloat/multilingual-e5-base (در صورت نیازِ سرعت، مدل سبک مثل all-MiniLM-L6-v2).

### **Metadata:**  
chunk_id, doc_id, doc_version,  
source{type,path/url,page_start,end},  
structure{title,h1,h2,h3,section_order},  
lang,  
dates{doc_date,ingested_at},  
tags,  
keywords{controlled,extracted},  
hashes{doc,chunk}.

---

## 3) خط لولهٔ ورود داده

- **Watchdog:** رصد پوشه؛ PDFهای جدید وارد می‌شوند.
- **PyMuPDF:** استخراج متن و صفحات.
- **MarkdownHeaderTextSplitter:** جداسازی بر پایهٔ سرفصل‌ها.
- **RecursiveCharacterTextSplitter:** استانداردسازی چانک‌ها روی ۳۵۰ توکن با ۱۰۰ توکن همپوشانی.
- **Keywords (BERT-based/KeyBERT):** تولید controlled و extracted.
- **Embedding** با intfloat/multilingual-e5-base و ثبت در Qdrant (بردار + متن + متادیتا).

---

## 4) منطق بازیابی و اثرات

**فیلترینگ بهتر:** متادیتا (سند/نسخه/فصل/تاریخ/زبان/برچسب/کلیدواژهٔ کنترل‌شده) پیش از ANN دامنه را دقیق کوچک می‌کند.

**سرعت بیشتر:** HNSW روی subset کوچک‌تر ⇒ latency پایین‌تر.

**کیفیت RAG بالاتر:**  
چانک‌های ۳۵۰/۱۰۰ مرز معنا را حفظ می‌کنند؛ سرفصل‌ها و صفحات استناد دقیق می‌دهند؛ ترکیب prefilter (کلیدواژه/برچسب) + شباهت برداری تعادل Precision/Recall را نگه می‌دارد.

</div>
