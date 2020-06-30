import dictionary as dict
import json
from basketball_reference_scraper.players import get_stats
from nba_api.stats.static import players
from queries import insert_players
from pandas import ExcelWriter

player_names = []
player_career_stats = []

player_details = players.get_active_players()

writer = ExcelWriter('PlayerStats.xlsx')

for full_name in player_details:
    player_names.append(full_name["full_name"])

#
# for player in player_names:
#     print(player)
#     stats = get_stats(player, 'PER_GAME', False, True)
#     print(stats)
print(players.get_active_players())
insert_players()

#
# writer.save()


