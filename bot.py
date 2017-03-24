import logging
import asyncio
import configparser
import discord
from witness import Witness
from espn_scraper import Scraper

logging.basicConfig(level=logging.INFO)

client = discord.Client()
scraper = Scraper()

@client.event
async def on_message(message):
    if message.content.startswith('$list'):
        live_games = scraper.get_live_games()
        msg = ''
        for i in range(len(live_games)):
            msg += str(i+1) + ': ' + live_games[i]['title'] + '\n'
        await client.send_message(message.channel, msg)

    elif message.content.startswith('$start'):
        try:
            game_num = int(message.content.replace('$start ', ''))
            game = scraper.get_live_games()[game_num-1]
            game_id = game['id']

            msg = 'Starting game: ' + game['title']
            await client.send_message(message.channel, msg)

            game = Witness(scraper, game_id, client, message.channel)
            await game.start()

        except Exception as e:
            print(str(e))
            await client.send_message(message.channel, 'Error. Use the following syntax:\n$list\n$start <game_number>')

    '''elif message.content.startswith('$score'):
        scoreboard = get_scoreboard()
        if scoreboard is not None:
            msg = scoreboard[0][0] + ': ' + scoreboard[1][0]
            msg += '\n' + scoreboard[0][1] + ': ' + scoreboard[1][1]
            await client.send_message(message.channel, msg)'''

config = configparser.RawConfigParser()
config.read('bot.cfg')
client.run(config.get('discord', 'token'))
