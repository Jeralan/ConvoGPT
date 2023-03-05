### STRING CONSTANTS ###
HELP = '''/exit - exit and save conversation
/c <text> - replace last bot response with text'''
SYSTEM_SUMMARY = "Summarize chats in the minimum token count so that a language model can continue that chat as "
START = "(/h to view all available commands)"
MODEL_COST = {
    "davinci":0.02/1000,
    "curie":0.002/1000,
    "babbage":0.0005/1000,
    "ada":0.0004/1000,
    "gpt-3.5-turbo":0.002/1000
}