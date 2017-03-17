import requests
import asyncio
from bs4 import BeautifulSoup

# A Witness reports on a game from a given url to a text channel on Discord
class Witness:
    def __init__(self, client, url, channel):
        self.client = client
        self.url = url
        self.channel = channel

    # e.g. returns [['Blues', 'Rangers'], ['1', '3']]
    def get_scoreboard(self):
        names = self.parser.select('.team-info a')
        names = [names[0].text, names[1].text] if len(names) == 2 else None
        scores = self.parser.select('.team-info span')
        scores = [scores[0].text, scores[1].text] if len(scores) == 2 else None
        if scores is None or names is None:
            return None
        return [names, scores]

    # Builds message from event e
    def construct_message(self, e):
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

    # Returns true if string s is a desired event
    def desired_event(self, s):
        desired = ['goal scored', 'penalty', 'end of', 'start of']
        for d in desired:
            if d in s.lower():
                return True
        return False

    async def start(self):
        old_events = [['0:0', '', 'placeholder']]

        while not old_events[-1][2].lower().startswith('end of game'):
            response = requests.get(self.url)
            print('Status: ', response.status_code)
            if response.status_code != 200:
                await self.client.send_message(self.channel, 'Error: status code ', response.status_code)
                break
            print('Type: ', response.headers['content-type'])
            content = response.content
            self.parser = BeautifulSoup(content, 'html.parser')

            # Get all the game events from the webpage
            game_events_content = self.parser.select('.mod-content tbody tr')
            if len(game_events_content) == 0:
                await self.client.send_message(self.channel, 'Error: scraping failed')
                break;

            # Construct game events list
            game_events = []
            for i in range(0, len(game_events_content)):
                info = game_events_content[i].select('td')
                # Three columns: time, team, and detail
                game_events.append([info[0].text, info[1].text, info[2].text])

            # Filter events and add to old_events
            game_events = [e for e in game_events if self.desired_event(e[2])]
            game_events = game_events[len(old_events)-1:]
            old_events.extend(game_events)

            for e in game_events:
                msg = self.construct_message(e)
                #print(msg)
                await self.client.send_message(self.channel, msg)
                await asyncio.sleep(3)
            await asyncio.sleep(10)

        await self.client.send_message(self.channel, 'El Fin.')