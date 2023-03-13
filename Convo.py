import os
from utils import *
import tiktoken 
from convoConstants import *
import openai

class Convo:
    def __init__(self, username, botname, model, sumModel):
        self.username = username
        self.botname = botname
        self.userFirst = username.split(" ")[0]
        self.filename = f"{username}-{botname}"
        if os.path.exists(self.filename):
            self.convo = readFile(self.filename)
        else:
            botrole = input(f"Intro string: Conversation between {username} and ")
            self.convo = f"{username} is talking to {botrole}"
        self.model = model
        self.encoding = tiktoken.encoding_for_model(model)
        self.modelCost = MODEL_COST[model]
        self.sumModel = sumModel
        self.sumEncoding = tiktoken.encoding_for_model(sumModel)
        self.sumCost = MODEL_COST[sumModel]
        self.maxTokens = 76
        self.temperature = 0.5
        self.minConvoLines = 8
        self.sumMaxTokens = 105

    def getInput(self):
        self.userIn = input(f"{self.userFirst}: ")
        return self.userIn
    
    def correct(self, correction):
        splitConvo = self.convo.split("\n")
        self.convo = "\n".join(splitConvo[:-1])
        self.convo += "\n"+correction
        print(correction)

    def removeLastLines(self):
        n = self.minConvoLines
        splitConvo = self.convo.split("\n")
        lastLines = "\n".join(splitConvo[-n:])
        return "\n".join(splitConvo[:-n]),lastLines

    def summarizeTokens(self):
        convo,lastLine = self.removeLastLines()
        tokens = self.sumMaxTokens
        encoding = self.sumEncoding
        tokens += 4+tokenCount(encoding,SYSTEM_SUMMARY+self.botname)
        tokens += 4+tokenCount(encoding,convo)
        tokens += 4+tokenCount(encoding,SUMMARY_PROMPT)
        tokens += 2
        return tokens,lastLine
    
    def summarize(self):
        convo,savedLines = self.removeLastLines()
        response = openai.ChatCompletion.create(
            model=self.sumModel,
            messages = [
            {"role":"system","content":SYSTEM_SUMMARY+self.botname},
            {"role":"user","content":convo},
            {"role":"user","content":SUMMARY_PROMPT}
            ],
            max_tokens=105
        )
        response = response.choices[0]["message"]["content"].split("\n")[0]
        self.convo = SUMMARY_HEADER+response+SUMMARY_TRANSITION+savedLines

    def shouldSummarize(self):
        requestTokens = tokenCount(self.encoding,self.convo)+self.maxTokens
        sumTokens,lastLine = self.summarizeTokens()
        sumReqCost = sumTokens*self.sumCost
        sumReqCost += (self.sumMaxTokens+tokenCount(self.encoding,SUMMARY_HEADER+SUMMARY_TRANSITION+lastLine))*self.modelCost
        sumReqCost += self.maxTokens*self.modelCost
        fullReqCost = requestTokens*self.modelCost
        return sumReqCost < fullReqCost

    def getResponse(self):
        self.convo += f"\n{self.userFirst}: {self.userIn}\n{self.botname}: "
        while self.shouldSummarize(): 
            self.summarize()
        response = openai.Completion.create(engine=self.model,
                                                    prompt=self.convo,
                                                    temperature=self.temperature,
                                                    max_tokens=self.maxTokens)
        response = response.choices[0].text.strip()
        response = response.split(":")[0].split("\n")[0].strip()
        self.convo += response
        print(f"{self.botname}: {response}")

    def close(self):
        f = open(self.filename, "w")
        f.write(self.convo)
        f.close()
    
    def __str__(self):
        return self.convo
