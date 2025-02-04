import cv2
import os
from PIL import Image
import google.generativeai as genai
from groq import Groq
import json
import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values('.env')
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Set up file paths (cross-platform compatibility)
DATA_DIR = os.path.join(os.getcwd(), "Data")
CHAT_LOG_PATH = os.path.join(DATA_DIR, "ChatLog.json")
IMAGE_PATH = os.path.join(DATA_DIR, "webcam.jpg")

# Initialize webcam
web_cam = cv2.VideoCapture(0)

# Initialize AI client
client = Groq(api_key=GroqAPIKey)
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

genai.configure(api_key=os.getenv("google_api"))
model = genai.GenerativeModel(
    "gemini-1.5-flash-latest",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

# System prompt
System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname} with real-time internet capabilities.
*** Do not tell time unless I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
*** You will be getting a description from the webcam, meaning it will act as your eyes, so answer as if you are actually seeing it. ***
"""

SystemChatBot = [{"role": "system", "content": System}]

# Load or create chat log
def load_chat_log():
    if not os.path.exists(CHAT_LOG_PATH):
        with open(CHAT_LOG_PATH, "w") as f:
            json.dump([], f)
    with open(CHAT_LOG_PATH, "r") as f:
        return json.load(f)

def save_chat_log(messages):
    with open(CHAT_LOG_PATH, "w") as f:
        json.dump(messages, f, indent=4)

# Capture image from webcam
def web_cam_capture():
    if not web_cam.isOpened():
        print("Error: Camera did not open successfully")
        return None
    
    success, frame = web_cam.read()
    if success:
        cv2.imwrite(IMAGE_PATH, frame)
        return IMAGE_PATH
    else:
        print("Error: Could not capture image from webcam.")
        return None

# Get real-time information
def RealtimeInformation():
    current_time = datetime.datetime.now()
    return (
        f"Please use this real-time information if needed:\n"
        f"Day: {current_time.strftime('%A')}\n"
        f"Date: {current_time.strftime('%d')} {current_time.strftime('%B')} {current_time.strftime('%Y')}\n"
        f"Time: {current_time.strftime('%H')}:{current_time.strftime('%M')}:{current_time.strftime('%S')}.\n"
    )

# Generate vision-based prompt response
def vision_prompt(prompt, photo_path):
    if not photo_path:
        return "No visual data available due to webcam error."

    img = Image.open(photo_path)
    prompt_text = (
        "You are the vision analysis AI that extracts semantic meaning from images. "
        "Your goal is to analyze the given image and provide relevant information "
        "for an AI assistant to respond accurately to the user.\n"
        f"USER PROMPT: {prompt}"
    )
    response = model.generate_content([prompt_text, img])
    return response.text if response else "No visual insights available."

# Clean up AI responses
def AnswerModifier(Answer):
    return "\n".join(filter(str.strip, Answer.splitlines()))

# Main chatbot function
def ImageChatBog(Query, retry_count=3):
    if retry_count == 0:
        return "Error: Unable to process request after multiple attempts."

    try:
        image_path = web_cam_capture()  # Capture image from webcam
        messages = load_chat_log()  # Load chat history

        messages.append({"role": "user", "content": Query})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=(
                SystemChatBot
                + [{"role": "system", "content": RealtimeInformation()}]
                + messages
                + [{"role": "system", "content": f"Visual data: {vision_prompt(Query, image_path)}"}]
            ),
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None,
        )

        # Extract response
        Answer = "".join(chunk.choices[0].delta.content for chunk in completion if chunk.choices[0].delta.content)
        Answer = Answer.replace("</s>", "")

        messages.append({"role": "assistant", "content": Answer})
        save_chat_log(messages)  # Save updated chat history

        return AnswerModifier(Answer)
    except Exception as e:
        print(f"Error: {e}")
        return ImageChatBog(Query, retry_count - 1)

# Run chatbot in a loop
if __name__ == "__main__":
    while True:
        Query = input(">>> ")
        if Query.lower() == "exit":
            break
        print(ImageChatBog(Query))
