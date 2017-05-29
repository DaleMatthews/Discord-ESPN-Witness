import asyncio

# A Witness reports on a game from a given game_id to a text channel on Discord
class Witness:
    def __init__(self, config, scraper, game_id, client, channel):
        self.scraper = scraper
        self.game_id = game_id
        self.client = client
        self.channel = channel
        self.events = config['nhl']['events']

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
        for e in self.events:
            if e in s.lower():
                return True
        return False

    async def start(self):
        old_events = [['0:0', '', 'placeholder']]

        while not old_events[-1][2].lower().startswith('end of game'):
            game_events = self.scraper.get_game_events(self.game_id)
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
