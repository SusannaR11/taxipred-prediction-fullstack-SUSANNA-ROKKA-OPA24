import requests 
from urllib.parse import urljoin
from datetime import date, time

def read_api_endpoint(endpoint = "/", base_url = "http://127.0.0.1:8000"):
    url = urljoin(base_url, endpoint)
    response = requests.get(url)
    
    return response

def post_api_endpoint(payload, endpoint="/", base_url="http://127.0.0.1:8000"):
    url = urljoin(base_url, endpoint)
    response = requests.post(url=url, json=payload)

    return response

def to_is_weekend(day: date) -> int:
    # Mon=0, ..., Sun=6. Weekend=1, Weekday= 0
    return 1 if day.weekday() >= 5 else 0

def to_day_label(day:date) -> str:
    return "Weekend" if to_is_weekend(day) else "Weekday"

def divide_time_of_day(t:time) -> tuple[str, int]:
    # Returns (label, code):
    # Morning=1 (05:00-11:59)
    # Afternoon=2 (12:00-16:59)
    # Evening=3 (17:00-21:59)
    # Night=4 (22:00-04:59)

    mins = t.hour * 60 + t.minute
    if 5*60 <= mins < 12*60:
        return "Morning", 1
    elif 12*60 <= mins < 17*60:
        return "Afternoon", 2
    elif 17*60 <= mins < 22*60:
        return "Evening", 3
    else:
        return "Night", 4
    
def is_business_hour(t:time) -> int:
    # business hour in this case: morning + afternoon
    return 1 if 5 <= t.hour < 17 else 0
 
