import openai
import sys, getopt
from utils import *
from Convo import Convo
from convoConstants import *

def getName(entity: str) -> tuple[str,str]:
    return input(f"{entity} name: ")

def main(argv: list[str]):
    file = "openAIkey.txt"
    opts, args = getopt.getopt(argv,"hk:",["key="])
    for opt, arg in opts:
        if opt == "h":
            print("convoGPT.py -k <OpenAI key file>")
        elif opt in ("k","--key"):
            file = arg
    openai.api_key = readFile(file).strip()
    username = getName("User")
    botname  = getName("Bot")
    #Using full bot name seems to give better responses
    model = "davinci"
    sumModel = "gpt-3.5-turbo"
    convo = Convo(username,botname,model,sumModel)
    userIn = convo.getInput()
    while not ("/exit" in userIn):
        if userIn[:2] == "/c":
            convo.correct(userIn[2:].strip())
        elif userIn[:2] == "/h":
            print(HELP)
        elif userIn[:2] == "/p":
            print(convo)
        else:
            convo.getResponse()
        userIn = convo.getInput()
    convo.close()
    

if __name__ == "__main__":
    out = main(sys.argv[1:])