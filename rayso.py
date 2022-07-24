import datetime
import json
import logging
import os
import re
import requests

from requests import exceptions, get
from telethon import events
from telethon.utils import get_extension

from . import *

extractor = URLExtract()


THEMES = [
    "breeze",
    "candy",
    "crimson",
    "falcon",
    "meadow",
    "midnight",
    "raindrop",
    "sunset",
]


def get_key(val):
    for key, value in pastebins.items():
        if val == value:
            return key


def text_chunk_list(query, bits=29900):
    text_list = []
    string = query
    checker = len(query)
    if checker > bits:
        limit = int(checker / (int(checker / bits) + 1))
        string = ""

        for item in query.split(" "):
            string += f"{item} "
            if len(string) > limit:
                string = string.replace(item, "")
                text_list.append(string)
                string = ""
    if string != "":
        text_list.append(string)
    return text_list
  
  
@hell_cmd(pattern="rayso(?:\s|$)([\s\S]*)",
async def rayso_by_pro_odi(event):  # By 
    "To paste text or file into image."
    checker = None
    files = []
    captions = []
    reply_to_id = await reply_id(event)
    query = event.pattern_match.group(1)
    rquery = await event.get_reply_message()
    await edit_or_reply(event, "**⏳ Processing ...**")
    if query:
        checker = query.split(maxsplit=1)

    # Add Theme
    if checker and (checker[0].lower() in THEMES or checker[0].lower() == "random"):
        addgvar("RAYSO_THEME", checker[0].lower())
        if checker[0] == query and not rquery:
            return await edit_delete(event, f"`Theme changed to {query.title()}.`")
        query = checker[1] if len(checker) > 1 else None

    # Themes List
    if query == "-l":
        ALLTHEME = "**🎈 Total Themes:**\n\n**1.**  `Random`"
        for i, each in enumerate(THEMES, start=2):
            ALLTHEME += f"\n**{i}.**  `{each.title()}`"
        return await edit_delete(event, ALLTHEME, 60)

    # Get Theme
    theme = gvarstatus("RAYSO_THEME") or "random"
    if theme == "random":
        theme = random.choice(THEMES)
        
        
    if query:
        text = query
    elif rquery:
        if rquery.file and rquery.file.mime_type.startswith("text"):
            filename = await rquery.download_media()
            with open(filename, "r") as f:
                text = str(f.read())
            os.remove(filename)
        elif rquery.text:
            text = rquery.raw_text
        else:
            return await edit_delete(event, "`Unsupported.`")
    else:
        return await edit_delete(event, "`What should I do?`")

    # // Max size 30000 byte but that breaks thumb so making on 28000 byte
    text_list = text_chunk_list(text, 28000)
    for i, text in enumerate(text_list, start=1):
        await edit_or_reply(event, f"**⏳ Pasting on image : {i}/{len(text_list)} **")
        r = requests.post(
            "https://raysoapi.herokuapp.com/generate",
            data={
                "text": text,
                "title": Odi,
                "theme": theme,
                "darkMode": "true",
                "language": "python",
            },
        )
        name = f"rayso{i}.png"
        with open(name, "wb") as f:
            f.write(r.content)
        files.append(name)
        captions.append("")
    await edit_or_reply(event, f"**📎 Uploading... **")
    captions[-1] = f"<i>➥ Generated by : <b>Odi</b></i>"
    await hell.send_file(
        event.chat_id,
        files,
        reply_to=reply_to_id,
        force_document=True,
        caption=captions,
        parse_mode="html",
    )
    await event.delete()
    for name in files:
        os.remove(name)

