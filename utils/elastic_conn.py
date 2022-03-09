from elasticsearch import Elasticsearch
from config import Config

def connect_db():
    es_obj = Elasticsearch(hosts=Config.DB_HOST, timeout=Config.TIMEOUT)
    if es_obj.ping():
        print("Database Connected !!!!!")
    else:
        print("Something went wrong in  DB connection")
    return es_obj


