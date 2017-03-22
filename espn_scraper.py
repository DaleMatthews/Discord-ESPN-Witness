import requests
from bs4 import BeautifulSoup
import datetime

class Scraper:

    def __init__(self):
        self.live_games_timer = None
        self.live_games = self.get_live_games()

    def get_live_games(self):
        current_time = datetime.datetime.now()
        if self.live_games_timer is not None and current_time - self.live_games_timer < datetime.timedelta(minutes=1):
            return self.live_games
        self.live_games_timer = current_time

        response = requests.get('http://www.espn.com/nhl/scoreboard')
        content = response.content
        parser = BeautifulSoup(content, 'html.parser')
        live_games_content = parser.select('.mod-scorebox-final') #in-progress')

        live_games = []
        for game in live_games_content:
            game_table = game.select('table.game-header-table')[0]
            game_title = game_table['summary'].replace(' Scores', '')
            game_link = game.select('.expand-gameLinks a')[0]['href']
            game_id = game_link.replace('gameId=', '|').split('|')[1]
            live_games.append({'title': game_title, 'id': game_id})
        return live_games