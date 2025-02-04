import cohere
from rich import print
from dotenv import dotenv_values


env_vars = dotenv_values('.env')

CohereAPIKey = env_vars.get('CohereAPIKey')

co = cohere.Client(api_key=CohereAPIKey)


funcs = [
    'exit','general', 'realtime','open','close','play','generate image',
    'system','content','google search', 'youtube','reminder', "webcam"
]



messages = []
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open Facebook, Instagram', 'can you write an application and open it in notepad'.

*** Do not answer any query, just decide what kind of query is given to you. ***

-> Respond with 'general (query)' if a query can be answered by a language model (conversational AI chatbot) and does not require real-time data. 
   Example:  
   - Query: "Who was Akbar?" → Response: 'general who was Akbar?'
   - Query: "How can I study more effectively?" → Response: 'general how can I study more effectively?'
   - Query: "What is Python programming language?" → Response: 'general what is Python programming language?'
   - Query: "Tell me about him." → Response: 'general tell me about him.'  
   - Query: "What is the time?" → Response: 'general what is the time?'

-> Respond with 'realtime (query)' if a query requires **up-to-date information** that a standard AI model cannot provide.  
   Example:  
   - Query: "Who is the Indian Prime Minister?" → Response: 'realtime who is the Indian Prime Minister?'  
   - Query: "Tell me about Facebook's recent update." → Response: 'realtime tell me about Facebook's recent update.'  
   - Query: "What is today's news?" → Response: 'realtime what is today's news?'

-> Respond with 'webcam (query)' if a query requires **real-time vision analysis using a webcam**.  
   Example:  
   - Query: "What is in front of me?" → Response: 'webcam what is in front of me?'  
   - Query: "Describe my surroundings." → Response: 'webcam describe my surroundings.'  
   - Query: "Can you see what I am holding?" → Response: 'webcam can you see what I am holding?'  
   - Query: "Tell me what is on my desk." → Response: 'webcam tell me what is on my desk.'
   - Query: "Tell me how I look" → Response: 'webcam tell me what is on my desk.'  


-> Respond with 'open (application name or website name)' if a query is asking to open an application.  
   Example:  
   - Query: "Open Facebook." → Response: 'open Facebook'  
   - Query: "Open Telegram and YouTube." → Response: 'open Telegram, open YouTube'  

-> Respond with 'close (application name)' if a query is asking to close an application.  
   Example:  
   - Query: "Close Notepad." → Response: 'close Notepad'  
   - Query: "Close Facebook and WhatsApp." → Response: 'close Facebook, close WhatsApp'  

-> Respond with 'play (song name)' if a query is asking to play a song.  
   Example:  
   - Query: "Play Let Her Go." → Response: 'play Let Her Go'  

-> Respond with 'generate image (image prompt)' if a query requests an AI-generated image.  
   Example:  
   - Query: "Generate an image of a lion." → Response: 'generate image of a lion'  

-> Respond with 'reminder (datetime with message)' if a query asks to set a reminder.  
   Example:  
   - Query: "Set a reminder for my meeting at 9:00 PM on June 25." → Response: 'reminder 9:00 PM 25th June business meeting'  

-> Respond with 'system (task name)' for system actions like mute, unmute, volume up, etc.  

-> Respond with 'content (topic)' if a query requests written content (e.g., emails, applications, code).  

-> Respond with 'google search (topic)' or 'youtube search (topic)' for search queries.  

-> If multiple tasks are requested, respond with each task separately.  
   Example:  
   - Query: "Open Facebook, close Telegram, and set a reminder for my meeting."  
     → Response: 'open Facebook, close Telegram, reminder meeting'  

-> Respond with 'exit' if the user says goodbye or wants to end the conversation.  

-> If a query is unclear or does not fit any category, respond with 'general (query)'.  
"""


ChatHistory = [
  {
      "role":"User",
      "message" : "How are you?"
  },
  {
      "role":"Chatbot",
      "message" : "general how are you?"
  },
  {
      'role' : "User",
      "message" : "Do you like pizza?"
  },
  {
      "role":"Chatbot",
      "message" : "general do you like pizza?"
  },
  {"role" : "User" , "message" : "open chrome and tell me about mahatma gandhi."},
  {"role" : "Chatbot" , "message" : "open chrome , general tell me about mahatma gandhi"},
  {"role" : "User" , "message" : "open chrome and firefox"},
  {"role" : "Chatbot" , "message" : "open chrome , open firefox"},
  {"role" : "User" , "message" : "what is today's date and by the way remind me that I have a dancing performance on 5th aug at 11pm"},
  {"role" : "Chatbot" , "message" : "general what is today's date , reminder 11:00 aug dancing performance"},
  {"role" : "User" , "message" :  "chat with me"},
  {"role" : "Chatbot" , "message" : "general chat with me"}
   
]


def FirstLayerDMM(prompt:str = "test"):
    messages.append({"role" : "user" , "content" : f"{prompt}"})

    stream = co.chat_stream(
        model = 'command-r-plus',
        message = prompt,
        temperature=0.7,
        chat_history=ChatHistory,
        prompt_truncation='OFF',
        connectors=[],
        preamble=preamble 
    )
    response = ""
    for event in stream:
        if event.event_type == "text-generation":
             response += event.text
    
    response = response.replace("\n" , "")
    response = response.split(",")

    response = [l.strip() for l in response]


    temp  = []

    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)
    response = temp

    if "(query)" in response:
        newresponse = FirstLayerDMM(prompt=prompt)
        return newresponse
    else:
        return response

if __name__ == "__main__":
    while True:
        print(FirstLayerDMM(input(">>> ")))
             
