from AppOpener import close , open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser 
import subprocess
import requests
import keyboard
import asyncio
import os

env_vars = dotenv_values('.env')
GroqAPIKey = env_vars.get('GroqAPIKey')

classes = ['zCubwf' , "hgKElc" , "LTKOO sy&ric" , "Z0LcW" , "gsrt vk_bk FzvWsb YwPhnf" , "pclqee" , "tw-Data-text tw-text-small tw-ta" , "IZ6rdc" , "O5uR6d LTKOO" , "vlzY6d" , "webanswers-webanswers_table__webanswers-table", "dDoNo ikb4Bb gsrt" , "sXLaOe" , "LWkfKe" , "VQF4g" , "qv3Wpe" , "kno-rdesc" , "SPZz6b"]

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"



client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else can I help you with.",
    "I'm at your service for any additional questions or support you may need-don't hesitate to ask"
]


messages = []

SystemChatBot = [
    {"role" : "system" , "content" : f"Hello I am {os.environ['Username']} , You're a content writer. You have to write content like letter "}
]



def GoogleSearch(Topic):
    search(Topic)
    return True


def Content(Topic):

    def OpenNotepad(File):
        default_text_editor = "notepad.exe"
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content  # Append instead of overwrite

        Answer = Answer.replace("</s>", "").strip()
        messages.append({"role": "assistant", "content": Answer})
        # print(Answer)
        
        return Answer  # ✅ Ensure it returns a string

       

    Topic : str = Topic.replace("Content" , "")
    ContentByAI = ContentWriterAI(Topic)
    file_path = os.path.join("Data", f"{Topic.lower().replace(' ', '_')}.txt")


    try:
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(ContentByAI)  # ✅ Ensure full content is written
    except Exception as e:
        print(f"Error writing to file: {e}")

    OpenNotepad(file_path)
    return True


def  YoutubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True


def PlayYoutube(query):
    playonyt(query)
    return True



def OpenApp(app, sess=requests.session()):
    try:
        # ✅ Special case for VS Code
        if app.lower() in ["vs code", "vscode", "visual studio code", "code"]:
            subprocess.Popen("code", shell=True)  # ✅ Opens VS Code directly
            return True

        # ✅ Try to use AppOpener
        from AppOpener import open as appopen
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        # ✅ Fallback: Search for an online link
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': "UWckNb"})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": user_agent}
            response = sess.get(url, headers=headers)

            if response.status_code == 200:
                return response.text
            else:
                print("Failed to retrieve search results.")
                return None
        
        html = search_google(app)
        links = extract_links(html)
        # print(repr(html), repr(links))


        if links:  # ✅ Check if links exist
            webbrowser.open(links[0])
        else:
            print(f"No links found for {app}")  # Debugging

        return True
def CloseApp(app):
    if "chrome" in app:
        pass
    else:
        try:
            close(app , match_closest=True , output=True, throw_error=True)
            return True
        except:
            return False
        
def System(command):

    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume mute")

    def volume_up():
        keyboard.press_and_release("volume up")
    
    def volume_down():
        keyboard.press_and_release("volume down")


    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()

    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()


async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        if command.startswith('open '):
            if "open it" in command:
                pass

            if "open file" == command:
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)

        elif command.startswith("general "):
            pass

        elif command.startswith('realtime '):
            pass

        elif command.startswith('close '):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)


        elif command.startswith('play '):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)


        elif command.startswith('content '):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith('google search') :
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith('youtube search'):
            fun = asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith('system '):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)

        else:
            print(f"I don't understand the command: {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        if isinstance(result , str):
            yield result
        else:
            yield result



async def Automation(commands : list[str]):

    async for result in TranslateAndExecute(commands):
        pass
    return True



if __name__ == "__main__":

    # OpenApp("settings")
    CloseApp("settings")

# Content("application for deadline extension")