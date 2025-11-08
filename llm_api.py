from openai import OpenAI
from config_key import OPENROUTER_API,MODEL_NAME
from typing import List
# import json

from prompt_system import system1,user1,system2,user2

class Llm():
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API
        )
    def call(self,massages:List[dict]):
        
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=massages,
            temperature=0.0,
            top_p=1.0,
        )
        # print(response.choices[0].message.content)
        return response.choices[0].message.content
    
    def generate(self,text:str , ret:str):
        con = [{"role":"system","content":system1},{"role":"user","content":user1.format(user_question=text,retrieved_text=ret)}]
        print(con)
        return self.call(con)
    
    def query_decomposition(self,text:str):
        query = [{"role":"system","content":system2},{"role":"user","content":user2.format(user_question=text)}]
        # print(self.call(query))
        return self.call(query)
    
if __name__=="__main__":
    llm=Llm()
    aas=llm.query_decomposition("چگونه میتونم در وظارت نفت استخدام شم و حق و حقوقم چطوری خواهد بود؟")
    print(aas)
    with open("test.txt","w",encoding="utf-8")as writer:
        writer.write(aas)
