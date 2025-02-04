from frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath as TempDictonaryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)

from Backend.Model import FirstLayerDMM as FirstLayerDW4
from Backend.RealTimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecogniton as SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.ImageDescriber import ImageChatBog
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

# For notifications
from plyer import notification

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}! How are you?
{Assistantname} : Hello {Username} I'm doing well, how can I help you today?
'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    with open(r"Data\ChatLog.json", "r", encoding="utf-8") as File:
        if len(File.read()) < 5:
            with open(TempDictonaryPath("Database.data"), "w", encoding="utf-8") as file:
                file.write("")
            with open(TempDictonaryPath("Responses.data"), "w", encoding="utf-8") as file:
                file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r"Data\ChatLog.json", "r", encoding="utf-8") as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""

    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"

    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDictonaryPath("Database.data"), "w", encoding="utf-8") as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    with open(TempDictonaryPath("Database.data"), "r", encoding="utf-8") as File:
        Data = File.read()
    if len(str(Data)) > 0:
        lines = Data.split("\n")
        result = '\n'.join(lines)
        with open(TempDictonaryPath("Responses.data"), "w", encoding="utf-8") as File:
            File.write(result)

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDW4(Query)

    print("")
    print(f"Decision: {Decision}")
    print("")

    # Check for general and realtime commands
    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])
    # Merge the queries from general and realtime if available
    Merged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    # Check if any decision includes image generation
    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    # Check if any decision requires task automation
    for queries in Decision:
        if not TaskExecution:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True

    # Handle image generation tasks
    if ImageExecution:
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")
        try:
            p1 = subprocess.Popen(["python", r"Backend\ImageGeneration.py"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdin=subprocess.PIPE, shell=False)
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error Generating Image: {e}")

    # Check if the decision includes a realtime query
    if (G and R) or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True
    else:
        # Process each decision command individually
        for Queries in Decision:
            if "general " in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general ", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "realtime" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "webcam" in Queries:
                # New branch for handling webcam queries using ImageChatBog
                SetAssistantStatus("Capturing image...")
                QueryFinal = Queries.replace("webcam ", "")
                Answer = ImageChatBog(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                os._exit(1)

def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available...")

def SecondThread():
    GraphicalUserInterface()

def ReminderNotificationThread():
    """Background thread to send a notification every 30 minutes reminding you to take a break."""
    while True:
        sleep(60*2)# Sleep for 30 minutes (1800 seconds)
        notification.notify(
            title="Reminder",
            message="Go drink some water and stand up for a break!",
            app_name=Assistantname,
            timeout=10  # Duration in seconds for which the notification stays visible
        )

if __name__ == "__main__":
    # Start the background thread for reminders
    reminder_thread = threading.Thread(target=ReminderNotificationThread, daemon=True)
    reminder_thread.start()

    # Start the main threads for the assistant
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
