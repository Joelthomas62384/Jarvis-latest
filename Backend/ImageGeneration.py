import asyncio
import os
import re
from random import randint
from time import sleep

import httpx
from dotenv import get_key
from PIL import Image
from rich import print

API_KEY = get_key(".env", "HuggingFaceAPIKey")

FILENAME_MAX_LENGTH = 50


def truncate_prompt(prompt: str, max_length: int) -> str:
    return (prompt[:max_length] + "...") if len(prompt) > max_length else prompt


def open_images(prompt: str):
    folder_path = r"Data\images"
    truncated_prompt = truncate_prompt(
        re.sub(r"[^a-zA-Z0-9_]", "_", prompt), FILENAME_MAX_LENGTH
    )
    Files = [f"{truncated_prompt}{i}.png" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)

        if os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                print(f"Opening image: [green]{image_path}[green]")
                img.show()

            except IOError:
                print(f"Unable to open; Image Path: [red]{image_path}[red]")
        else:
            print(f"Image not found: [yellow]{image_path}[yellow]")


API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {API_KEY}"}


async def query(payload):
    print("Query")
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, headers=headers, json=payload)
        print(f"Status code: {response}")
        if response.status_code == 200:
            return response.content
        else:
            return None


async def generate_images(prompt: str):
    tasks = []
    truncated_prompt = truncate_prompt(
        re.sub(r"[^a-zA-Z0-9_]", "_", prompt), FILENAME_MAX_LENGTH
    )

    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, High Resolution, seed = {randint(0, 1000000)}"
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    os.makedirs(r"Data\images", exist_ok=True)
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            with open(rf"Data\images\{truncated_prompt}{i + 1}.png", "wb") as f:
                f.write(image_bytes)


def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)


while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data: str = f.read()

        Prompt, Status = Data.split(",")

        if Status == "True":
            print(f'Generating Images for "{Prompt}..."')
            GenerateImages(prompt=Prompt)
            Status = ""

            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False,False")
                break

        else:
            sleep(1)

    except Exception as e:
        print(f"An error occurred: {e}")