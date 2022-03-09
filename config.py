class Config:
    DEBUG = True
    DB_HOST = 'http://localhost:9200/'
    DB_INDEX = 'index_student'
    TIMEOUT = 15
    SERVER_HOST = '0.0.0.0'
    SCHEDULER_API = 'http://localhost:5000/insert_data'