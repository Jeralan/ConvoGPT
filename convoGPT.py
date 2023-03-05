import openai
import tiktoken 
import sys, getopt, os
from convoConstants import *

def tokenCount(encoding,convo):
    return len(encoding.encode(convo))

def removeLastLines(convo):
    splitConvo = convo.split("\n")
    lastLines = "\n".join(splitConvo[-2:])
    return "\n".join(splitConvo[:-1]),lastLines

def summarizeTokens(encoding, convo, botname):
    convo,lastLine = removeLastLines(convo)
    maxTokens = 250
    tokens = maxTokens
    tokens += 4+tokenCount(encoding,SYSTEM_SUMMARY+botname)
    tokens += 4+tokenCount(encoding,convo)
    tokens += 2
    return tokens,lastLine

def summarize(model, encoding, convo, botname):
    tokens,savedLines = summarizeTokens(encoding,convo,botname)
    while tokens > 4096:
        convo,lastLine = removeLastLines(convo)
        savedLines = lastLine+"\n"+savedLines
        tokens -= tokenCount(encoding,lastLine)+1
    response = openai.ChatCompletion.create(
        model=model,
        messages = [
        {"role":"system","content":SYSTEM_SUMMARY+botname},
        {"role":"user","content":convo}
        ]
    )
    #TODO: add transition from summarization to conversation
    #TODO: consider always keeping at least 2 previous messages to 
    ###### establish the conversation format
    return response.choices[0]["message"]["content"]+"\n"+savedLines

def getResponse(convo: str, username: str, botname: str, model: str, sumModel: str, encoding, sumEncoding) -> tuple[str,str]:
    temperature = 0.5
    maxTokens = 250
    requestTokens = tokenCount(encoding,convo)+maxTokens
    sumCost = MODEL_COST[sumModel]
    reqCost = MODEL_COST[model]
    sumTokens,lastLine = summarizeTokens(sumEncoding, convo, botname)
    sumReqCost = sumTokens*sumCost
    sumReqCost += (250+1+tokenCount(encoding,lastLine))*reqCost
    fullReqCost = requestTokens*reqCost
    while requestTokens > 2049 or (sumReqCost < fullReqCost and len(convo.split("\n")) > 3):
        print("summarizing")
        convo = summarize(sumModel, sumEncoding, convo, botname)
        requestTokens = tokenCount(encoding,convo)+maxTokens
        sumTokens,lastLine = summarizeTokens(sumEncoding, convo, botname)
        sumReqCost = sumTokens*sumCost
        sumReqCost += (250+1+tokenCount(encoding,lastLine))*reqCost
        fullReqCost = requestTokens*reqCost
    response = openai.Completion.create(engine=model,
                                                prompt=convo,
                                                temperature=temperature,
                                                max_tokens=maxTokens)
    response = response.choices[0].text.strip()
    response = response.split(":")[0].split("\n")[0].strip()
    convo += response+f"\n{username}: "
    return convo,response

def readFile(filename):
    f = open(filename,"r")
    out = f.read()
    f.close()
    return out

def getName(entity: str) -> tuple[str,str]:
    fullName = input(f"{entity} name: ")
    first = fullName.split(" ")[0]
    return fullName,first

def main(argv: list[str]):
    file = "openAIkey.txt"
    opts, args = getopt.getopt(argv,"hk:",["key="])
    for opt, arg in opts:
        if opt == "h":
            print("convoGPT.py -k <OpenAI key file>")
        elif opt in ("k","--key"):
            file = arg
    openai.api_key = readFile(file).strip()
    username,userFirst = getName("User")
    botname,_ = getName("Bot")
    #Using full bot name seems to give better responses
    filename = f"{username}-{botname}"
    if os.path.exists(filename):
        convo = readFile(filename)
    else:
        #TODO: optimize and add specific instructions for this
        botrole = input(f"Intro string: Conversation between {username} and ")
        convo = f"{username} is talking to {botrole}\n{userFirst}: "
    print(convo)
    print(START)
    userIn = input(convo.split("\n")[-1])
    model = "davinci"
    sumModel = "gpt-3.5-turbo"
    encoding = tiktoken.encoding_for_model(model)
    sumEncoding = tiktoken.encoding_for_model(sumModel)
    while not ("/exit" in userIn):
        if userIn[:2] == "/c":
            splitConvo = convo.split("\n")
            convo = splitConvo[:-2]
            print(f"{botname}: {userIn[2:].strip()}")
            convo += [f"{botname}: {userIn[2:].strip()}"]+splitConvo[-1:]
            convo = "\n".join(convo)
        elif userIn[:2] == "/h":
            print(HELP)
        else:
            convo += userIn+f"\n{botname}: "
            convo,response = getResponse(convo,userFirst,botname,model,sumModel,encoding,sumEncoding)
            print(f"{botname}: {response}")
        userIn = input(convo.split("\n")[-1])
    f = open(filename, "w")
    f.write(convo)
    f.close()

if __name__ == "__main__":
    out = main(sys.argv[1:])