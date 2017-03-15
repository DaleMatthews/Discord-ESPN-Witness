import logging
import asyncio
import configparser
import discord
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

client = discord.Client()

# Returns true if string s is a desired event
def desired_event(s):
    desired = ['goal scored', 'penalty', 'end of', 'start of']
    for d in desired:
        if d in s.lower():
            return True
    return False

def get_scoreboard(parser):
    names = parser.select('.team-info a')
    names = [names[0].text, names[1].text] if len(names) == 2 else None
    scores = parser.select('.team-info span')
    scores = [scores[0].text, scores[1].text] if len(scores) == 2 else None
    if scores is None or names is None:
        return None
    return [names, scores]

def construct_message(e):
    msg = ''
    if 'goal scored' in e[2].lower():
        if 'st. louis' in e[1].lower():
            msg += ':smiley: '
        else:
            msg += ':rage: '
    elif 'penalty' in e[2].lower():
        msg += ':comet: '

    msg += e[0] + ': '           # Time expired in the period
    if e[1] != '':
        msg += '@' + e[1] + ' '  # Team
    msg += e[2]                  # Detailed message
    return msg

@client.event
async def on_message(message):
    global parser
    if message.content.startswith('$start'):
        url = message.content.replace('$start ', '')
        await client.send_message(message.channel, 'Starting game from ' + url)
        old_events = [['0:0', '', 'placeholder']]

        while not old_events[-1][2].lower().startswith('end of game'):
            response = requests.get(url)
            #response = requests.get('http://www.espn.com/nhl/playbyplay?gameId=400885340&period=0')
            print('Status: ', response.status_code)
            if response.status_code != 200:
                await client.send_message(message.channel, 'Error: status code ', response.status_code)
                break
            print('Type: ', response.headers['content-type'])
            content = response.content
            parser = BeautifulSoup(content, 'html.parser')

            # Get all the game events from the webpage
            game_events_content = parser.select('.mod-content tbody tr')
            if len(game_events_content) == 0:
                await client.send_message(message.channel, 'Error: scraping failed')
                break;

            # Construct game events list
            game_events = []
            for i in range(0, len(game_events_content)):
                info = game_events_content[i].select('td')
                # Three columns: time, team, and detail
                game_events.append([info[0].text, info[1].text, info[2].text])

            # Filter events and add to old_events
            game_events = [e for e in game_events if desired_event(e[2])]
            game_events = game_events[len(old_events)-1:]
            old_events.extend(game_events)

            for e in game_events:
                msg = construct_message(e)
                #print(msg)
                await client.send_message(message.channel, msg)
                await asyncio.sleep(3)
            await asyncio.sleep(10)

        await client.send_message(message.channel, 'El Fin.')

    elif message.content.startswith('$score'):
        scoreboard = get_scoreboard(parser)
        if scoreboard is not None:
            msg = scoreboard[0][0] + ': ' + scoreboard[1][0]
            msg += '\n' + scoreboard[0][1] + ': ' + scoreboard[1][1]
            await client.send_message(message.channel, msg)

config = configparser.RawConfigParser()
config.read('bot.cfg')
client.run(config.get('discord', 'token'))
