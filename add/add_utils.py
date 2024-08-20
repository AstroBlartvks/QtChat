
def formate_text(text):
    return "\n".join(list([x.rstrip() for x in text.split("\n") if x != "" and x != " " and not(x.count(" ") == len(x))]))
