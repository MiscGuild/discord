async def name_grabber(author):
    if author.nick == None:
        return author.name
    return author.nick.split()[0]
