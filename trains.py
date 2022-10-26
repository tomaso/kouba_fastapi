from typing import Union
import binascii
from fastapi import FastAPI, Path
from pydantic import BaseModel
from PIL import Image
from pprint import pprint
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://172.17.0.12:3000",
    "http://172.17.0.16:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Pixel(BaseModel):
    r: int
    g: int
    b: int


neopixels_data = {
    0: {"r": 0, "g": 0, "b": 0},
    1: {"r": 0, "g": 0, "b": 0},
    2: {"r": 0, "g": 0, "b": 0},
    3: {"r": 0, "g": 0, "b": 0},
    4: {"r": 0, "g": 0, "b": 0},
    5: {"r": 0, "g": 0, "b": 0},
    6: {"r": 0, "g": 0, "b": 0},
    7: {"r": 0, "g": 0, "b": 0},
    8: {"r": 0, "g": 0, "b": 0},
    9: {"r": 0, "g": 0, "b": 0},
    10: {"r": 0, "g": 0, "b": 0},
    11: {"r": 0, "g": 0, "b": 0},
    12: {"r": 0, "g": 0, "b": 0},
    13: {"r": 0, "g": 0, "b": 0},
    14: {"r": 0, "g": 0, "b": 0},
    15: {"r": 0, "g": 0, "b": 0},
    16: {"r": 0, "g": 0, "b": 0},
    17: {"r": 0, "g": 0, "b": 0},
    18: {"r": 0, "g": 0, "b": 0},
    19: {"r": 0, "g": 0, "b": 0},
    20: {"r": 0, "g": 0, "b": 0},
    21: {"r": 0, "g": 0, "b": 0},
    22: {"r": 0, "g": 0, "b": 0},
}

loco_data = {3: {"start": 16, "end": 22}, 4: {"start": 1, "end": 8}}


class EchoClientProtocol(asyncio.Protocol):
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        transport.write(self.message.encode())
        print("Data sent: {!r}".format(self.message))

    def data_received(self, data):
        print("Data received: {!r}".format(data.decode()))

    def connection_lost(self, exc):
        print("The server closed the connection")
        self.on_con_lost.set_result(True)


@app.get("/trains/light/{loco_id}/{lightness}")
async def loco_get(loco_id: int, lightness: int):
    value = lightness % 256
    print(value)
    if loco_id in loco_data:
        for i in range(loco_data[loco_id]["start"], loco_data[loco_id]["end"] + 1):
            neopixels_data[i]["r"] = value
            neopixels_data[i]["g"] = value
            neopixels_data[i]["b"] = value
    return None


@app.get("/trains/dcc/{loco_id}/{function}/{value}")
async def loco_get(loco_id: int, function: int, value: int):
    loop = asyncio.get_running_loop()
    on_con_lost = loop.create_future()
    transport, protocol = await loop.create_connection(
        lambda: EchoClientProtocol(
            f"<F {loco_id} {function} {value}>\n", on_con_lost
        ),
        "172.17.0.104",
        2560,
    )
    transport.close()
    try:
        await on_con_lost
    finally:
        transport.close()
    return None
