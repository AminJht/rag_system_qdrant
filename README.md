تأیید می‌کنم ✅ — کل متن را یک‌جا و بدون کم‌وکاست در **قالب Markdown** قرار می‌دهم و تکه‌تکه نمی‌کنم.

````markdown
<div dir="rtl" align="right" style="text-align: right;">

# RAG + Qdrant — README

این راهنما، مراحل اجرای پروژه را به‌صورت کوتاه و دقیق توضیح می‌دهد: ساخت محیط پایتون، نصب وابستگی‌ها، بالا آوردن Qdrant با Docker، و اجرای اسکریپت پایش PDF.

---

## پیش‌نیازها

* **Python 3.10**
* **Docker** و **Docker Compose**
* دسترسی ترمینال (PowerShell / CMD در ویندوز، یا شِل در لینوکس/مک)

---

## 1) کلون/کپی پروژه

پروژه را در یک مسیر کاری مناسب قرار دهید (نمونه):

```bash
C:\Projects\rag_qdrant\
````

---

## 2) ساخت و فعال‌سازی Virtual Environment

### ویندوز (PowerShell/CMD)

```bash
python3.10 -m venv .venv
.\.venv\Scripts\activate
```

### لینوکس/مک

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

> اگر قبلاً از نام دیگری برای venv استفاده کرده‌اید (مثل `Urenv`)، کافی است همان نام را جایگزین `.venv` کنید. مهم فعال‌بودن محیط مجازی هنگام نصب و اجراست.

---

## 3) نصب وابستگی‌ها

فایل **requirements.txt** را نصب کنید (اگر نام فایل شما «requironment.txt» است، همان را استفاده کنید؛ پیشنهاد می‌شود به **requirements.txt** تغییر نام دهید):

```bash
pip install -r requirements.txt
```

---

## 4) بالا آوردن Qdrant با Docker

داخل پوشه‌ی `./qdrant`، فایل `docker-compose.yml` باید قرار داشته باشد.

### ویندوز (PowerShell) / لینوکس / مک

```bash
cd qdrant
docker compose up -d
```

پس از اتمام، وضعیت سرویس را بررسی کنید:

* مرورگر را باز کنید و آدرس زیر را بزنید:

  ```
  http://localhost:6333/readyz
  ```

  در صورت راه‌اندازی صحیح، متنی مبنی بر آماده‌بودن Qdrant نمایش داده می‌شود.

> پورت‌های پیش‌فرض: **6333** (HTTP)، **6334** (gRPC)

---

## 5) اجرای پایش PDF و ورود به دیتابیس برداری

به ریشه‌ی پروژه برگردید و (با **venv فعال**) اسکریپت پایش را اجرا کنید. این اسکریپت پوشه‌ی `./PDF_keeper` را تحت‌نظر می‌گیرد؛ هر فایل **PDF** جدید را می‌خوانَد، چانک‌بندی می‌کند، متادیتا و کلیدواژه (BERT-based) استخراج می‌کند، امبدینگ را با **`intfloat/multilingual-e5-base`** تولید می‌کند و در **Qdrant** ذخیره می‌کند.

```bash
cd ..
python whatchdog.py
```

> **نکته:** اگر نام فایل شما «watchdog.py» است، همان را اجرا کنید. در بعضی ریپوها «whatchdog.py» نوشته شده؛ نام واقعی فایل اسکریپت خودتان را اجرا کنید.

* پوشه‌ی ورودی PDF: `./PDF_keeper/`
* کتابخانه‌های اصلی پردازش: **PyMuPDF** برای خواندن PDF، splitterهای LangChain برای چانک‌بندی (MarkdownHeaderTextSplitter + RecursiveCharacterTextSplitter با حدود **۳۵۰ توکن** و **۱۰۰ توکن همپوشانی**)، استخراج کلیدواژه‌ی BERT-based (مانند KeyBERT/e5-based)، و ذخیره در **Qdrant**.

---

## ساختار پیشنهادی پوشه‌ها (نمونه)

```
project-root/
│  README.md
│  requirements.txt
│  whatchdog.py
│
├─ qdrant/
│   └─ docker-compose.yml
│
└─ PDF_keeper/
    └─ (قرار دادن PDFهای جدید در این پوشه)
```

---

## عیب‌یابی سریع (Quick Troubleshooting)

* **venv فعال نیست** → قبل از نصب/اجرا، دستور `activate` را اجرا کنید.
* **پورت 6333 اشغال است** → سرویس‌های دیگر را متوقف کنید یا پورت docker-compose را تغییر دهید.
* **عدم اتصال به Qdrant** → `docker compose ps` را بررسی کنید؛ لاگ‌ها: `docker compose logs -f`. آدرس `http://localhost:6333/readyz` باید آماده باشد.
* **خطا در نصب وابستگی‌ها** → `pip install -U pip` و سپس نصب مجدد. از Python 3.10 مطمئن شوید.

---

6. اجرای چت‌بات وب (Chat UI / API)
   6.1 پیکربندی کلید OpenRouter

از سایت OpenRouter یک API Key بگیرید.

در ریشهٔ پروژه، فایل config_key.py را باز/ایجاد کنید و مقدار کلید را قرار دهید:

```python
# config_key.py
OPENROUTER_API_KEY = "sk-or-xxxxxxxxxxxxxxxx"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"  # در صورت نیاز
MODEL_NAME = "anthropic/claude-3.5-sonnet"            # یک مدل قوی پیشنهاد می‌شود
```

می‌توانید به‌جای فایل، از متغیر محیطی هم استفاده کنید:
ویندوز (PowerShell):

```powershell
setx OPENROUTER_API_KEY "sk-or-..."
```

لینوکس/مک (bash):

```bash
export OPENROUTER_API_KEY="sk-or-..."
```

هشدار درباره مدل رایگان: مدل پیش‌فرض رایگان deepseek/deepseek-chat-v3.1:free دقت پایینی دارد و ممکن است پاسخ‌های نادرست بدهد. برای کیفیت بهتر، یک مدل قوی‌تر انتخاب کنید (مثلاً anthropic/claude-3.5-sonnet یا مشابه).

---

6.2 اجرای سرویس چت‌بات

در محیط مجازی فعال، دستور زیر را اجرا کنید:

```bash
python chatbot_api.py
```

پس از اجرا، در لاگ برنامه، آدرس سرویس نمایش داده می‌شود (http://127.0.0.1:8002) یا پورتی که در کد تعیین کرده‌اید).

مرورگر را باز کنید و همان آدرس را بزنید تا رابط وب تست را ببینید و پیام دهید.

به احتمال بسیار خودش اتوماتیک باز خواهد شد

---

6.3 نکات عیب‌یابی

کلید تنظیم نشده: اگر OPENROUTER_API_KEY موجود نباشد، درخواست‌ها خطا می‌دهند. مقدار را در config_key.py یا متغیر محیطی ست کنید.

خطای شبکه/مدل: مدل انتخابی را بررسی کنید؛ برخی مدل‌ها نیاز به دسترسی/اعتبار خاص دارند.

CORS/پورت اشغال: پورت دیگری انتخاب کنید یا سرویس‌های متداخل را متوقف کنید.

---

## پشتیبانی

برای سوال یا مشکل، ایمیل بزنید: **[amin.jahantigh.727@gmail.com](mailto:amin.jahantigh.727@gmail.com)**

</div>
