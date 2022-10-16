with open("conversation.txt") as f:
    txt = f.readlines()
    txt = txt[::-1]
    with open("new_conversations.txt", "w") as outf:
        for x in txt:
            outf.write(x)
