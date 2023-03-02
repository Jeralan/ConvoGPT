import openai
import sys, getopt, os

helpString = '''/exit - exit and save conversation
/c <text> - replace last bot response with text'''

def getResponse(convo: str, username: str) -> tuple[str,str]:
    model_engine = "text-davinci-003"
    temperature = 0.5
    maxTokens = 250
    response = None
    savedLines = ""
    try:
        response = openai.Completion.create(engine=model_engine,
                                                    prompt=convo,
                                                    temperature=temperature,
                                                    max_tokens=maxTokens)
        response = response.choices[0].text.strip()
        response = response.split(username+":")[0].strip()
    except openai.error.InvalidRequestError:
        splitConvo = convo.split("\n")
        firstHalfConvo = "\n".join(splitConvo[:len(splitConvo)//2])
        secondHalfConvo = "\n".join(splitConvo[len(splitConvo)//2:])
        summaryPrompt = firstHalfConvo+"\n\nSo to describe this conversation in summary:\n"
        summary = openai.Completion.create(engine=model_engine,
                                                    prompt=summaryPrompt,
                                                    temperature=temperature,
                                                    max_tokens=maxTokens)
        summary = summary.choices[0].text.strip()
        convo = "So a summary of the conversation so far is:\n"+summary+"\n\nThe conversation then continued as follows:\n\n"+secondHalfConvo
        response = openai.Completion.create(engine=model_engine,
                                                    prompt=convo,
                                                    temperature=temperature,
                                                    max_tokens=maxTokens)
        response = response.choices[0].text.strip()
        response = response.split(username+":")[0].strip()
    convo += response+f"\n{username}: "
    return convo,response

def main(argv: list[str]):
    file = "openAIkey.txt"
    opts, args = getopt.getopt(argv,"hk:",["key="])
    for opt, arg in opts:
        if opt == "h":
            print("convoGPT.py -k <OpenAI key file>")
        elif opt in ("k","--key"):
            file = arg
    f = open(file,"r")
    openai.api_key = f.read().strip()
    f.close()
    username = input("User name: ")
    botname = input("Bot name: ")
    filename = f"{username}-{botname}"
    if os.path.exists(filename):
        f = open(filename, "r")
        convo = f.read()
        f.close()
    else:
        print("Specify the bot's role")
        botrole = input(f"Conversation between {username} and ")
        convo = f"The following is a text conversation between {username} and {botrole}\n{username}: "
    print(convo.split("\n")[-2])
    print("(/h to view all available commands)")
    userIn = input(convo.split("\n")[-1])
    while not ("/exit" in userIn):
        if userIn[:2] == "/c":
            splitConvo = convo.split("\n")
            print(f"{botname}: {userIn[2:].strip()}")
            convo = "\n".join(splitConvo[:-2]+[f"{botname}: {userIn[2:].strip()}"]+splitConvo[-1:])
        elif userIn[:2] == "/h":
            print(helpString)
        else:
            convo += userIn+f"\n{botname}: "
            convo,response = getResponse(convo,username)
            print(f"{botname}: {response}")
        userIn = input(convo.split("\n")[-1])
    f = open(filename, "w")
    f.write(convo)
    f.close()

if __name__ == "__main__":
    out = main(sys.argv[1:])