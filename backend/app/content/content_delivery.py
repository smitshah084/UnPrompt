from datetime import datetime, timezone
from typing import Optional

# Import modules from FastAPI
from fastapi import APIRouter, Depends, HTTPException, status

# Import internal utilities for database access, authorisation, and schemas
from app.utils.db import neo4j_driver
from app.authorisation.auth import get_current_active_user
from app.utils.schema import User, Node, Nodes, Relationship,card,card_batch
from app.utils.environment import Config
# Set the API Router
router = APIRouter()











from neo4j import GraphDatabase
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from string import Template 
from IPython.display import Markdown
import json
import textwrap
import requests

# model = 'Alibaba-NLP/gte-base-en-v1.5' # 130M
model = 'sentence-transformers/paraphrase-MiniLM-L6-v2' # 22M
# model = 'avsolatorio/NoInstruct-small-Embedding-v0' # 33M
# from InstructorEmbedding import INSTRUCTOR

def text_to_embeddings(texts, model_name=model):
    # model = INSTRUCTOR(model_name)
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts)
    return embeddings

class model:

    def __init__(self):
        genai.configure(api_key=Config.GEMINI_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.wrong_answer_count = 0

    def __call__(self,prompt,test=False,card=False):
        response = self.model.generate_content(prompt).text
       
        if card:
            try:
                response = response.strip().strip('```json').strip('```').strip()
                response = json.loads(response)
                keys = list(response.keys()) # content,image_prompt,image_url
                # response[keys[0]] = self.to_markdown(response[keys[0]])        
                response['image_url'] = google_image_search(response[keys[1]])[0]
            except:
                print(response)
                
        return response
        
    def to_markdown(self,text):
      text = text.replace('•', '  *')
      return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

model=model()

def google_image_search(query, num_results=1):
    api_key = Config.IMAGE_KEY
    cx = '325794ae0dbb14a3b'
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'cx': cx,
        'key': api_key,
        'searchType': 'image',
        'num': num_results
    }

    response = requests.get(search_url, params=params)
    response.raise_for_status()
    results = response.json()

    image_urls = []
    if 'items' in results:
        for item in results['items']:
            image_urls.append(item['link'])
    
    return image_urls

class Neo4jManager:
    
    def __init__(self,URI,AUTH):
        self.driver = GraphDatabase.driver(URI, auth=AUTH)
        self.model = model
        self.init_faiss()
        
    def init_faiss(self):
        session = self.driver.session()
        q = '''match (n:Topic) return elementId(n) as nodeId,n.emb as emb,n.title as title'''
        nodes = session.run(q).to_df()
        session.close()
        
        nodes['emb'] = nodes['emb'].apply(lambda l : np.array(l))
        self.nodes = nodes.copy()
        
        nodes_arr = nodes['emb'][0]
        for i in nodes['emb'][1:]:
            nodes_arr = np.vstack((nodes_arr,i))

        norms = np.linalg.norm(nodes_arr, axis=1)
        nodes_arr = nodes_arr / norms[:,None]
        
        self.index = faiss.IndexFlatIP(nodes_arr.shape[1])
        self.index.add(nodes_arr)
        self.nodes_arr = nodes_arr.copy()

    def __call__(self,q):
        session = self.driver.session()
        q = session.run(q).data()
        session.close()
        return q
        
    def close(self):
        self.driver.close()

    def create_user(self, name ,intrests):
        def _create_user(tx, name):
            tx.run("CREATE (a:user {username: $name})", name=name)
        
        with self.driver.session() as session:
            session.execute_write(_create_user, name)

        if len(intrests)>0:
            self.seed_intrest(name,intrests)


    def find_user(self, name):
        def _find_person(tx, name):
            result = tx.run("MATCH (a:user {username: $name}) RETURN a", name=name).data()
            return result
        
        with self.driver.session() as session:
            return session.read_transaction(_find_person, name)

    def seed_intrest(self,username,intrests):
        def fun(tx,username,intrests):
            query = f"""
                MATCH (a:User {{ username: '{username}' }})
                WITH a
                UNWIND $intrests AS intrest
                MATCH (b:Topic {{title: intrest}})
                CREATE (a)-[r:intrested]->(b)
                """
            tx.run(query, intrests=intrests)

        if type(intrests) != type([]):
            intrests = [intrests]
            
        with self.driver.session() as session:
            return session.execute_write(fun,username,intrests)

    def topic_row(self,topic):        
        def fun(top):
            return self.nodes.index[self.nodes['title'] == top][0]
        
        if type(topic) != type([]):
            return fun(topic)
        else:
            return [fun(i) for i in topic]

    def row_topic(self,idx):
        def fun(tidx):
            return self.nodes['title'][tidx]

        if type(idx) != type([]):
            return fun(idx)
        else:
            return [fun(i) for i in idx]
    
    def similar_topics(self,topic,k):
        try:
            ix = self.topic_row(topic)
            emb = self.nodes_arr[ix][None,:]
        except:
            emb = text_to_embeddings(topic)[None,:]
            
        D, I = self.index.search(emb, k)
        index = D>0.9
        sim_tops = list(self.row_topic(I[index]))
        return sim_tops

    def sub_topics(self,topic):
        q = f'''
        MATCH (Topic {{title: '{topic}'}})-[:sub_topic]-(connectedNode)
        RETURN connectedNode.title
        '''
        session = self.driver.session()
        q = session.run(q)
        r = []
        for qr in q:
            r.append(qr['connectedNode.title'])
        return r

    def gen_cards(self,user,k=3):
        r = self.recommend_topics(user)
        l = list(r)[:k]
        res_dic = {}
        for i in l:
            res_dic[i[1]] = self.model(card_prompt.substitute({'field':i[0],'topic':i[1]}),card=True)
        return res_dic

    def recommend_topics(self,user):
        q = f'''
        MATCH (a:User {{username: '{user}' }})-[:intrested]->(b:Topic)
        with b
        MATCH (b)-[:sub_topics]->(c:Topic)
        RETURN b.title as from, c.title as to
        '''
        session = self.driver.session()
        r = session.run(q).data()
        session.close()
        r = set((x['from'],x['to']) for x in r)
        return r

    def init_topic_recommendation(self,k=10):
        init_topic_recommendations = '''
        MATCH (n)
        RETURN n, SIZE([(n)-[:sub_topics]-() | 1]) AS relationship_count
        ORDER BY relationship_count DESC
        LIMIT $k
        '''
        session = self.driver.session()
        r = session.run(init_topic_recommendations,k=k).data()
        session.close()
        l = [i['n']['title'] for i in r]
        return l

    def user_consumed(self,username,consumed_topics):
        def fun(tx,username,consumed_topics):
            query = f"""
                MATCH (a:User {{ username: '{username}' }})
                WITH a
                UNWIND $consumed_topics AS consumed_topic
                MATCH (b:Topic {{title: consumed_topic}})
                CREATE (a)-[r:consumed]->(b)
                """
            tx.run(query, consumed_topics=consumed_topics)

        if type(consumed_topics) != type([]):
            consumed_topics = [consumed_topics]
            
        with self.driver.session() as session:
            return session.execute_write(fun,username,consumed_topics)

    # def query(self,q):
    #     session = self.driver.session()
        

        
AUTH = (Config.NEO4J_USERNAME,Config.NEO4J_PASSWORD)


neo = Neo4jManager(Config.NEO4J_URI,AUTH)

init_topic_recommendations = '''
        MATCH (n)
        RETURN n, SIZE([(n)-[:sub_topics]-() | 1]) AS relationship_count
        ORDER BY relationship_count DESC
        LIMIT $k
        '''

card_prompt = Template('''
You are personalised educational content generater. generate the content by strictly following the below instructions.

Instructions:
0. ALWAYS FINISH THE OUTPUT. Never send partial responses.
1. your task is to generate content on topic '$topic' which is sub-topic of '$field'.
2. write an image search engine prompt to get the relavent image which can aid in user's ease of learning.
3. generate the content and prompt in the given format
4. Generate the output in the given JSON format:
    {
        "content": content on the given topic,
        "image_prompt": prompt relavent to content
    }
''')





















@router.post('/get_cards', response_model=card_batch)
async def get_cards(current_user: User = Depends(get_current_active_user)):

    dic_cards = neo.gen_cards(current_user.username)
    list_cards = []
    for title in list(dic_cards.keys()):

        singel_dic_card = dic_cards[title]

        content,image_prompt,image_url = list(singel_dic_card.keys())

        c = card(title=title,
                 content=singel_dic_card[content],
                 image_caption=singel_dic_card[image_prompt],
                 image_link=singel_dic_card[image_url])
        
        list_cards.append(c)

    return card_batch(cards=list_cards)


    # return str_model(username =current_user.username)