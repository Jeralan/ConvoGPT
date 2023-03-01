import openai
import sys, getopt, os

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
        convo = f"{username} is talking to {botrole}\n{username}: "
    print(convo.split("\n")[-2])
    userIn = input(convo.split("\n")[-1])
    model_engine = "text-davinci-003"
    temperature = 0.5
    maxTokens = 250
    while not ("\exit" in userIn):
        convo += userIn+f"\n{botname}: "
        response = openai.Completion.create(engine=model_engine,
                                            prompt=convo,
                                            temperature=temperature,
                                            max_tokens=maxTokens)
        response = response.choices[0].text.strip()
        convo += response+f"\n{username}: "
        print(f"{botname}: {response}")
        userIn = input(convo.split("\n")[-1])
    f = open(filename, "w")
    f.write(convo)
    f.close()

if __name__ == "__main__":
    out = main(sys.argv[1:])