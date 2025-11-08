from hazm import Normalizer
from transformers import AutoTokenizer
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
import json , os , re
from typing import List,Optional
from keywords import KeyExtractor
from qdrant import SimpleQdrant


_MD_HEADERS = [("#", "h1"), ("##", "h2"), ("###", "h3"), ("####", "h4")]
TARGET    = 360    # اندازه هدف
MIN       = 120    # حداقل قابل‌قبول
SOFT_MAX  = 420    # بهتر است از این بالاتر نرویم
HARD_MAX  = 512    # هرگز از این بیشتر نشود  

keys=KeyExtractor()
_tok = AutoTokenizer.from_pretrained("intfloat/multilingual-e5-base",cache_dir="./models")
_norm = Normalizer()
_md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=_MD_HEADERS)

SEPARATORS = [
    "\n\n",           # paragraphs
    "\n- ", "\n* ", "\n• ",  # lists
    ". ", "؟ ", "? ", "! ",  # sentence-ish enders (fa/en)
    "\n", " ", ""     # fallbacks
]

#baraye shomaresh token
def _ntoks(s: str) -> int:
    return len(_tok.encode(s, add_special_tokens=False))

def normalize_text(text: str) -> str:
    
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = _norm.normalize(text)
    return text.strip()

def split_markdown_sections(text: str) -> Optional[List[dict]]:
    try:
        sections = _md_splitter.split_text(text)
    except Exception:
        return None

    if not sections:
        return None

    if len(sections) == 1:
        meta = sections[0].metadata or {} or {}
        has_any_header = any(meta.get(k) for _, k in _MD_HEADERS)
        if not has_any_header:
            return None

    return sections

def micro_chunks(block_text: str) -> List[str]:
    """
    Token-aware splitting with overlap. Also merges tiny tail chunks (< MIN_CHUNK_TOKENS)
    back into the previous chunk.
    """
    splitter = RecursiveCharacterTextSplitter(
        separators=SEPARATORS,
        chunk_size=TARGET,
        length_function=_ntoks,
        add_start_index=False,
    )
    raw_chunks = splitter.split_text(block_text)

    SOFT_MAX_TOKENS = int(TARGET * 1.2)  
    HARD_MAX_TOKENS = 512                     

    fixed: List[str] = []
    temp_chunk: str = ""

    for ch in raw_chunks:
        ch = (ch or "").strip()
        if not ch:
            continue

        # اگر temp خالی است، این چانک را موقت نگه دار
        if not temp_chunk:
            temp_chunk = ch
            continue

        t_temp = _ntoks(temp_chunk)
        t_ch   = _ntoks(ch)

        # اگر temp کوچک است، برای بزرگ‌شدن به آن اضافه کن (تا سقف HARD_MAX)
        if t_temp < MIN:
            if t_temp + t_ch <= HARD_MAX_TOKENS:
                temp_chunk = temp_chunk + ("\n" if not temp_chunk.endswith("\n") else "") + ch
            else:
                # اگر ادغام از سقف سخت عبور می‌کند، temp را نهایی کن و ch را موقت بگذار
                fixed.append(temp_chunk.strip())
                temp_chunk = ch
            continue

        # در اینجا temp به حداقل رسیده است
        # اگر در بازه‌ی هدف/سقف نرم است، نهایی کن و چانک جدید را در temp قرار بده
        if t_temp <= TARGET or (t_temp <= SOFT_MAX_TOKENS and t_ch >= MIN):
            fixed.append(temp_chunk.strip())
            temp_chunk = ch
            continue

        # اگر temp از سقف نرم بزرگ‌تر شد، بدون ادغام نهایی کن و ch را در temp بگذار
        fixed.append(temp_chunk.strip())
        temp_chunk = ch

    # پایان: اگر چیزی در temp مانده، نهایی کن
    if temp_chunk:
        fixed.append(temp_chunk.strip())

    return [c for c in fixed if c]

def _cleanup_keywords(kw: List[str]) -> List[str]:
    """
    Light cleanup:
      - strip
      - collapse inner spaces
      - lowercase for Latin
      - deduplicate while preserving order
      - keep it short (e.g., top 12)
    Assumes Hazm-style normalization already applied upstream for Persian text.
    """
    seen = set()
    cleaned = []
    for k in kw:
        k2 = re.sub(r"\s+", " ", (k or "").strip())
        # lower only for pure Latin tokens (avoid changing Persian)
        if re.fullmatch(r"[A-Za-z0-9 _\-./]+", k2):
            k2 = k2.lower()
        if k2 and k2 not in seen:
            seen.add(k2)
            cleaned.append(k2)
        if len(cleaned) >= 12:
            break
    return cleaned

def chunk_text(
    text: str,
    doc_id: str,
) -> List[dict]:

    text = normalize_text(text)

    # Pass 1: try real Markdown structure; else fall back to plain text
    sections = split_markdown_sections(text)
    blocks: List[str] = []
    if sections:
        for sec in sections:
            content = (sec.get("content") or "").strip()
            if content:
                blocks.append(content)
    else:
        blocks = [text]

    # Pass 2: micro-chunk each block
    chunks: List[str] = []
    for blk in blocks:
        chunks.extend(micro_chunks(blk))

    # Build output items with minimal metadata
    out = []
    for i, ch in enumerate(chunks, start=1):
        kw = keys.key_words(ch) or []
        # Optional post-clean for keywords (lightweight)
        kw = _cleanup_keywords(kw)
        item = {
            "doc_id": doc_id,
            "chunk_id": f"{doc_id}-{i}",
            "text": ch,
            "n_tokens": _ntoks(ch),
            "keywords": kw,
        }
        out.append(item)
    return out

def chunk_file_to_txt(
    input_path: str,
    text: str,
    doc_id: Optional[str] = None,
) -> None:
    
    if doc_id is None:
        base = os.path.basename(input_path)
        doc_id = os.path.splitext(base)[0]

    chunks = chunk_text(text, doc_id=doc_id)

    for item in chunks:
        with open("chunks_and_metadata.txt","w",encoding="utf-8")as writer:
            writer.write(f'{item["text"]}\n{item["text"]}-{item["doc_id"]}-{item["chunk_id"]}-{item["keywords"]}')
        db=SimpleQdrant()

        db.add_item(
        text=item["text"],
        doc_id=item["doc_id"],
        chunk_id=item["chunk_id"],
        keywords=item["keywords"],
    )

if __name__ == "__main__":
    pass


    
