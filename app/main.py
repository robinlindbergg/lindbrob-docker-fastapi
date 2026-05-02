from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import psycopg2

app = FastAPI()


def get_conn():
    return psycopg2.connect(
        host="host.docker.internal",
        port=5432,
        database="postgres",
        user="postgres",
        password="postgres"
    )


@app.get("/rooms")
def get_rooms():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, room_number, type, price FROM hotel_rooms;")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "room_number": r[1],
            "type": r[2],
            "price": float(r[3])
        }
        for r in rows
    ]


@app.get("/bookings")
def get_bookings():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT b.id, r.room_number, b.datefrom, b.addinfo
        FROM hotel_bookings b
        JOIN hotel_rooms r ON b.room_id = r.id
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "room_number": r[1],
            "date": str(r[2]),
            "info": r[3]
        }
        for r in rows
    ]


@app.post("/bookings")
async def create_booking(request: Request):
    data = await request.json()

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO hotel_bookings (guest_id, room_id, datefrom, dateto, addinfo)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        1,  # enkel guest (för nu)
        data["room_id"],
        data["date"],
        data["date"],
        data["info"]
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def frontend():
    return """
    <h1>Hotel Booking</h1>

    <select id="rooms"></select><br><br>

    <input type="date" id="date"><br><br>

    <input type="text" id="info" placeholder="Extra info"><br><br>

    <button onclick="save()">Book</button>

    <h2>Bookings</h2>
    <ul id="list"></ul>

    <script>
    async function loadRooms() {
        let res = await fetch('/rooms');
        let rooms = await res.json();

        let select = document.getElementById('rooms');
        select.innerHTML = '';

        rooms.forEach(r => {
            let opt = document.createElement('option');
            opt.value = r.id;
            opt.text = r.room_number + " (" + r.type + ")";
            select.appendChild(opt);
        });
    }

    async function loadBookings() {
        let res = await fetch('/bookings');
        let data = await res.json();

        let list = document.getElementById('list');
        list.innerHTML = '';

        data.forEach(b => {
            let li = document.createElement('li');
            li.innerText = "Room " + b.room_number + " - " + b.date + " - " + b.info;
            list.appendChild(li);
        });
    }

    async function save() {
        let room = document.getElementById('rooms').value;
        let date = document.getElementById('date').value;
        let info = document.getElementById('info').value;

        await fetch('/bookings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                room_id: room,
                date: date,
                info: info
            })
        });

        loadBookings();
    }

    loadRooms();
    loadBookings();
    </script>
    """