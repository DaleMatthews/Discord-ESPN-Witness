import requests
from bs4 import BeautifulSoup
import datetime

class Scraper:

    def __init__(self):
        self.live_games_timer = None
        self.live_games = self.get_live_games()

    # Returns list of games from the ESPN Scoreboard
    def get_live_games(self):
        current_time = datetime.datetime.now()
        if self.live_games_timer is not None and current_time - self.live_games_timer < datetime.timedelta(minutes=1):
            return self.live_games
        self.live_games_timer = current_time

        response = requests.get('http://www.espn.com/nhl/scoreboard')
        content = response.content
        parser = BeautifulSoup(content, 'html.parser')
        live_games_content = parser.select('.mod-scorebox-in-progress') # final

        live_games = []
        for game in live_games_content:
            game_table = game.select('table.game-header-table')[0]
            game_title = game_table['summary'].replace(' Scores', '')
            game_link = game.select('.expand-gameLinks a')[0]['href']
            game_id = game_link.split('gameId=')[1]
            live_games.append({'title': game_title, 'id': game_id})
        return live_games

    # Returns list play-by-play events of specified game
    # Raises Exception upon failure
    def get_game_events(self, game_id):
            url = 'http://www.espn.com/nhl/playbyplay?gameId=' + game_id + '&period=0'
            response = requests.get(url)
            print('Status: ', response.status_code)
            if response.status_code != 200:
                msg = 'Error: status code ' + response.status_code + ' from URL ' + url
                raise Exception(msg)

            print('Type: ', response.headers['content-type'])
            content = response.content
            parser = BeautifulSoup(content, 'html.parser')

            # Get all the game events from the webpage
            game_events_content = parser.select('.mod-content tbody tr')
            if len(game_events_content) == 0:
                raise Exception('Error: scraping failed from URL ' + url)

            # Construct game events list
            game_events = []
            for i in range(0, len(game_events_content)):
                info = game_events_content[i].select('td')
                # Three columns: time, team, and detail
                if len(info) == 3:
                    game_events.append([info[0].text, info[1].text, info[2].text])
            return game_events


''' Currently has no use...
    # e.g. returns [['Blues', 'Rangers'], ['1', '3']]
    def get_scoreboard(self):
        names = self.parser.select('.team-info a')
        names = [names[0].text, names[1].text] if len(names) == 2 else None
        scores = self.parser.select('.team-info span')
        scores = [scores[0].text, scores[1].text] if len(scores) == 2 else None
        if scores is None or names is None:
            return None
        return [names, scores]
'''
