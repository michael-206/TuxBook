import os
import queue
import threading

import requests
from dotenv import load_dotenv
from guizero import PushButton, Text, TextBox

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")


def ask_chatgpt(prompt):
    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-5.6-luna",
            "input": prompt,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["output"][0]["content"][0]["text"]


def build(parent, **kwargs):
    Text(parent, text="ChatGPT", size=24)
    entry = TextBox(parent, width=45, height=4, multiline=True)
    message = Text(parent, text="", size=14, width="fill")
    result_queue = queue.Queue()

    def poll_for_response():
        try:
            result, error = result_queue.get_nowait()
        except queue.Empty:
            parent.after(100, poll_for_response)
            return

        message.value = error or result
        submit_button.enabled = True

    def request_response(prompt):
        try:
            result_queue.put((ask_chatgpt(prompt), None))
        except requests.RequestException as error:
            result_queue.put((None, f"Request failed: {error}"))
        except (KeyError, IndexError, TypeError, ValueError) as error:
            result_queue.put((None, f"Unexpected response format: {error}"))

    def submit():
        prompt = entry.value.strip()
        if not prompt:
            message.value = "Enter a prompt before submitting."
            return
        if not API_KEY:
            message.value = "Set OPENAI_API_KEY to use ChatGPT."
            return

        message.value = "Thinking..."
        submit_button.enabled = False
        threading.Thread(
            target=request_response,
            args=(prompt,),
            daemon=True,
        ).start()
        parent.after(100, poll_for_response)

    submit_button = PushButton(parent, text="Submit", command=submit)
