import discord
from PIL import Image
import pyocr
import sys
import subprocess
import random
import r6s_stats as r6s 
import time

client = discord.Client()

def preparing_stats(username, userdata, by_short=None):
    if by_short is None:
        by_short = False

    stats = "**[%s  %s]**\n" % (str(username), userdata["trophy"])
    stats += "[1st] %s (%s)\n" % (userdata["operator"][0][0], userdata["operator"][0][5])
    stats += "[2nd] %s (%s)\n" % (userdata["operator"][1][0], userdata["operator"][1][5])
    stats += "[3rd] %s (%s)\n" % (userdata["operator"][2][0], userdata["operator"][2][5])
    stats += "```\n"
    if by_short:
        stats += "-------------------------------\n"
        stats += "|       |   rank   | casual   |\n"
        stats += "|-------|----------|----------|\n"
        stats += "| w/l   |%s|%s|\n" % (str(round(userdata["rank"].won / max(1, userdata["rank"].lost), 4)).center(10), str(round(userdata["casual"].won / max(1, userdata["casual"].lost), 4)).center(10))
        stats += "|-------|----------|----------|\n"
        stats += "| k/d   |%s|%s|\n" % (str(round(userdata["rank"].kills / max(1, userdata["rank"].deaths), 4)).center(10), str(round(userdata["casual"].kills / max(1, userdata["casual"].deaths), 4)).center(10))
        stats += "-------------------------------"
    
    if not by_short:
        stats += "-------------------------------\n"
        stats += "|       |   rank   | casual   |\n"
        stats += "|-------|----------|----------|\n"
        stats += "| win   |%s|%s|\n" % (str(userdata["rank"].won).center(10), str(userdata["casual"].won).center(10))
        stats += "|-------|----------|----------|\n"
        stats += "| lose  |%s|%s|\n" % (str(userdata["rank"].lost).center(10), str(userdata["casual"].lost).center(10))
        stats += "|-------|----------|----------|\n"
        stats += "| w/l   |%s|%s|\n" % (str(round(userdata["rank"].won / max(1, userdata["rank"].lost), 4)).center(10), str(round(userdata["casual"].won / max(1, userdata["casual"].lost), 4)).center(10))
        stats += "|-------|----------|----------|\n"
        stats += "| kill  |%s|%s|\n" % (str(userdata["rank"].kills).center(10), str(userdata["casual"].kills).center(10))
        stats += "|-------|----------|----------|\n"
        stats += "| death |%s|%s|\n" % (str(userdata["rank"].deaths).center(10), str(userdata["casual"].deaths).center(10))
        stats += "|-------|----------|----------|\n"
        stats += "| k/d   |%s|%s|\n" % (str(round(userdata["rank"].kills / max(1, userdata["rank"].deaths), 4)).center(10), str(round(userdata["casual"].kills / max(1, userdata["casual"].deaths), 4)).center(10))
        stats += "-------------------------------"
    stats += "```\n"
    return stats

def execute_cmd(cmd):
    subprocess.call(cmd.split())

def get_txt(filename):
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)
    
    tool = tools[0]
    
    txt = tool.image_to_string(
        Image.open(filename),
        lang='eng',
        builder=pyocr.builders.TextBuilder()
    )
    return txt

def image_detection(filename, url):
    cmd = "wget -O /tmp/%s %s" % (filename, url)
    execute_cmd(cmd)
    cmd = "convert -threshold 61500 %s %s" % ("/tmp/"+filename, "/tmp/g_"+filename)
    execute_cmd(cmd)
    cmd = "convert -resize 195%x100% {0} {1}".format("/tmp/g_"+filename, "/tmp/gw_"+filename)
    execute_cmd(cmd)
    cmd = "convert -blur 10 {0} {1}".format("/tmp/gw_"+filename, "/tmp/gwb_"+filename)
    execute_cmd(cmd)
    return get_txt("/tmp/gwb_" + filename)
            

@client.event
async def on_ready():
    print("Logged in!")

@client.event
async def on_message(message):
    if message.content.startswith('/team -ch'):
        info = message.content.split(" ")[:5]
        voice_channel = discord.utils.get(
                message.server.channels, 
                name=info[2], 
                type=discord.ChannelType.voice)

        member = [mem.name for mem in voice_channel.voice_members]
        random.shuffle(member)
        teamA = ", ".join(member[:int(len(member)/2)])
        teamB = ", ".join(member[int(len(member)/2):])
        msg =  "---- :cowboy: ----"
        msg += "{0}"
        msg += "---- :hugging: ----"
        msg += "{1}"
        msg = msg.format(teamA, teamB)
        await client.send_message(message.channel, msg)

    if message.content.startswith('/stats'):
        info = message.content.split(" ")[:3]
        if info[1] == "-name":
            if len(info) < 3:
                msg = "だれくぽ？"
                await client.send_message(message.channel, msg)
            else:
                userdata = await r6s.get_userdata(info[2])
                if userdata == -1:
                    return
                msg = preparing_stats(info[2], userdata)
                await client.send_message(message.channel, msg)
        
        if info[1] == "-names":
            if len(info) < 3:
                msg = "だれくぽ？"
                await client.send_message(message.channel, msg)
            else:
                userdata = await r6s.get_userdata(info[2])
                if userdata == -1:
                    msg = "制限なう＼(^o^)／"
                    await client.send_message(message.channel, msg)
                    return
                msg = preparing_stats(info[2], userdata, by_short=True)
                await client.send_message(message.channel, msg)
        
        if info[1] == "-img":
            attachment = message.attachments[:1]
            if 0 == len(attachment):
                msg = "がぞうは？"
                await client.send_message(message.channel, msg)
            else:
                url = attachment[0]["url"]
                filename = url.split("/")[-1]
                
                players_str = image_detection(filename, url)
                players = arrange_players(players_str)
                    
                for player in players:
                    msg = "/stats -names %s" % player 
                    await client.send_message(message.channel, msg)
                    time.sleep(5)

def arrange_players(players_str):
    real_players = []
    for player in players_str.split("\n"):
        if len(player) < 3 or 15 < len(player):
            continue
        real_players.append(player.strip())
    return real_players
        

if __name__=="__main__":
    TOKEN = "TOKEN"
    client.run(TOKEN)
