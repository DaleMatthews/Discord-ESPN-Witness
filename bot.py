import logging
import asyncio
import configparser
import discord
from witness import Witness

logging.basicConfig(level=logging.INFO)

client = discord.Client()

@client.event
async def on_message(message):
    if message.content.startswith('$start'):
        url = message.content.replace('$start ', '')
        await client.send_message(message.channel, 'Starting game from ' + url)
        game = Witness(client, url, message.channel)
        await game.start()

    '''elif message.content.startswith('$score'):
        scoreboard = get_scoreboard()
        if scoreboard is not None:
            msg = scoreboard[0][0] + ': ' + scoreboard[1][0]
            msg += '\n' + scoreboard[0][1] + ': ' + scoreboard[1][1]
            await client.send_message(message.channel, msg)'''

config = configparser.RawConfigParser()
config.read('bot.cfg')
client.run(config.get('discord', 'token'))
