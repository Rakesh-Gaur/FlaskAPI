from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler
from faker import Faker
from random import randint
import random
import requests
import json

from config import Config


def call_post_api():
    faker = Faker()
    data = {"name": str(faker.name()), "roll_no": randint(0,9999999),
                    "nationality": "Indian", 
                "gender": random.choice(['male', 'female'])}
    req = requests.post(url = Config.SCHEDULER_API, json=data, timeout=Config.TIMEOUT)                                            

    print("Sheduler Response", req.status_code)

def schedule_task():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(call_post_api,'interval', minutes=10)
    sched.start()