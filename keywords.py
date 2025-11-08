from keybert import KeyBERT
from hazm import Normalizer, stopwords_list
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
import time

class KeyExtractor:
    def __init__(self):
        self.normalizer = Normalizer()
        self.fa_stop = stopwords_list()
        embed = SentenceTransformer("intfloat/multilingual-e5-base",cache_folder="./models")
        self.model = KeyBERT(embed)
    
    def key_words(self,text:str):
        text = self.normalizer.normalize(text)

        vectorizer = CountVectorizer(
            ngram_range=(1,2),
            stop_words=self.fa_stop,
            token_pattern=r"(?u)\b[\w‌]+\b",
            lowercase=False
        )
        s = time.time()
        keywords = self.model.extract_keywords(
            text,
            vectorizer=vectorizer,
            use_mmr=True,
            diversity=0.4,
            top_n=12
        )
        e = time.time()
        _time = e - s
        print(f"{_time}")
        print(keywords)
        return [w for (w, _) in keywords]

def main():
    text = """چند برچسب موضوعی کنترل‌شده برای هر چانک ثبت می‌شود.
این برچسب‌ها امکان پیش‌فیلتر هدفمند و همچنین تقویت نتایج مرتبط را فراهم می‌کنند،
مخصوصا در پرسش‌های کوتاه. خروجی سریع‌تر به نقطه درست می‌رسد و کیفیت رتبه‌بندی بهتر می‌شود."""
    keys = KeyExtractor()
    print(keys.key_words(text=text))

if __name__=="__main__":
    main()