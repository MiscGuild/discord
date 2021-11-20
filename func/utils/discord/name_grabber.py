async def name_grabber(author):
    name = author.nick
    if name == None:
        name = author.name
    else:
        name = name.split()[0]
    return name
