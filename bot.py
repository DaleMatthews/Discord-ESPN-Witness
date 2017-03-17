import logging
import asyncio
import configparser
import discord
import requests
from bs4 import BeautifulSoup
from witness import Witness

logging.basicConfig(level=logging.INFO)

client = discord.Client()

@client.event
async def on_message(message):
    if message.content.startswith('$list'):
        response = requests.get('http://www.espn.com/nhl/scoreboard')
        content = response.content
        parser = BeautifulSoup(content, 'html.parser')
        live_games_content = parser.select('.mod-scorebox-in-progress')

        live_games = []
        for game in live_games_content:
            game_table = game.select('table.game-header-table')[0]
            game_title = game_table['summary'].replace(' Scores', '')
            game_link = game.select('.expand-gameLinks a')[0]['href']
            game_id = game_link.replace('gameId=', '|').split('|')[1]
            live_games.append({'title': game_title, 'id': game_id})

        msg = ''
        for i in range(len(live_games)):
            msg += str(i+1) + ': ' + live_games[i]['title'] + '\n'
        await client.send_message(message.channel, msg)

    elif message.content.startswith('$start'):
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
