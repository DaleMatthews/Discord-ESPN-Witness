import logging
import asyncio
import json
import discord
from witness import Witness
from espn_scraper import Scraper

logging.basicConfig(level=logging.INFO)

client = discord.Client()
scraper = Scraper()
config = json.load(open('config.json'))

@client.event
async def on_message(message):
    if message.content.startswith('$list'):
        live_games = scraper.get_live_games()

        if len(live_games) > 0:
            msg = ''
            for i in range(len(live_games)):
                msg += str(i+1) + ': ' + live_games[i]['title'] + '\n'
            await client.send_message(message.channel, msg)
        else:
            await client.send_message(message.channel, 'No games currently airing')

    elif message.content.startswith('$start'):
        try:
            game_num = int(message.content.replace('$start ', ''))
            game = scraper.get_live_games()[game_num-1]
            game_id = game['id']

            msg = 'Starting game: ' + game['title']
            await client.send_message(message.channel, msg)

            game = Witness(config, scraper, game_id, client, message.channel)
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

client.run(config['discord']['token'])