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


@app.get("/loco_light/{loco_id}/{lightness}")
async def loco_get(loco_id: int, lightness: int):
    value = lightness % 256
    print(value)
    if loco_id in loco_data:
        for i in range(loco_data[loco_id]["start"], loco_data[loco_id]["end"] + 1):
            neopixels_data[i]["r"] = value
            neopixels_data[i]["g"] = value
            neopixels_data[i]["b"] = value
    return None


@app.get("/loco_dcc/{loco_id}/{function}/{value}")
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


@app.put("/neopixel/{item_id}")
async def update(item_id: int, pixel: Pixel):
    print(item_id)
    print(pixel)
    neopixels_data[item_id]["r"] = pixel.r
    neopixels_data[item_id]["g"] = pixel.g
    neopixels_data[item_id]["b"] = pixel.b
    return neopixels_data


@app.get("/neopixel")
async def root():
    return neopixels_data


@app.get("/l")
async def root():
    # ba = img.tobytes()
    # w = 296
    # h = 25
    w = 20
    h = 20
    size = (w * h + 7) // 8
    nba = bytearray([0xFF] * w * h / 8)
    for y in range(25):
        for x in range(25):
            p = ba[(y * 22 + 11) * img.width + (x * 22 + 11)]
            nba[y * w + x] = p
    msg = binascii.b2a_base64(nba)
    return {"w": f"{w}", "h": f"{h}", "msg": msg}


@app.get("/")
async def root():
    ba = bytearray()
    v = 1
    for i in range(296):
        ba.append(v)
        v = v << 1
        if v >= 0xFF:
            v = 1
    v = 1
    for i in range(296):
        ba.append(v)
        if v == 0xFF:
            v = 1
        else:
            v = (v << 1) + 1
    msg = binascii.b2a_base64(ba)
    return {"msg": msg}
