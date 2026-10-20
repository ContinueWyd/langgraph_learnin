import requests

res = requests.post(
    "http://127.0.0.1:8000/chat",
    json={"message": "北京天气怎么样？", "thread_id": "user-123"}
)
print(res.status_code)
print(res.json())
