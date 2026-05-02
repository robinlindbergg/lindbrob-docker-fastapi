from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/")
def read_root():
    return {"msg": "Heyooo Robin!!!!!!!!!", "v": "0.1"}


@app.get("/items/{id}")
def read_item(item_id: int, q: str = None):
    return {"id": item_id, "q": q}


@app.get("/api/ip")
def get_ip(request: Request):
    return {"ip": request.client.host}


@app.get("/ip", response_class=HTMLResponse)
def get_ip_html(request: Request):
    ip = request.client.host
    return f"<h1>Din publika IP-adress är {ip}</h1>"

rooms = [
    {"room_number": 101, "type": "single", "price": 80, "available": True},
    {"room_number": 102, "type": "double", "price": 120, "available": True},
    {"room_number": 201, "type": "suite", "price": 220, "available": False},
]


@app.get("/rooms")
def get_rooms():
    return rooms