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
