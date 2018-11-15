import discord
import random
import r6s_stats as r6s 

client = discord.Client()

def preparing_stats(username, userdata):
    stats = "**[%s  %s]**\n" % (str(username), userdata["trophy"])
    stats += "[1st] %s (%s)\n" % (userdata["operator"][0][0], userdata["operator"][0][5])
    stats += "[2nd] %s (%s)\n" % (userdata["operator"][1][0], userdata["operator"][1][5])
    stats += "[3rd] %s (%s)\n" % (userdata["operator"][2][0], userdata["operator"][2][5])
    stats += "```\n"
    stats += "-------------------------------\n"
    stats += "|       |   rank   | casual   |\n"
    stats += "|-------|----------|----------|\n"
    stats += "| win   |%s|%s|\n" % (str(userdata["rank"].won).center(10), str(userdata["casual"].won).center(10))
    stats += "|-------|----------|----------|\n"
    stats += "| lose  |%s|%s|\n" % (str(userdata["rank"].lost).center(10), str(userdata["casual"].lost).center(10))
    stats += "|-------|----------|----------|\n"
    stats += "| kill  |%s|%s|\n" % (str(userdata["rank"].kills).center(10), str(userdata["casual"].kills).center(10))
    stats += "|-------|----------|----------|\n"
    stats += "| death |%s|%s|\n" % (str(userdata["rank"].deaths).center(10), str(userdata["casual"].deaths).center(10))
    stats += "-------------------------------"
    stats += "```\n"
    return stats

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
        msg = """
---- :cowboy: ----
{0}
        
---- :hugging: ----
{1}
        """.format(teamA, teamB)
        await client.send_message(message.channel, msg)

    if message.content.startswith('/stats'):
        info = message.content.split(" ")[:2]
        if len(info) < 2:
            msg = "だれくぽ？"
            await client.send_message(message.channel, msg)
        else:
            userdata = await r6s.get_userdata(info[1])
            msg = preparing_stats(info[1], userdata)
            await client.send_message(message.channel, msg)

if __name__=="__main__":
    TOKEN = "TOKEEEEEEEN"
    client.run(TOKEN)
