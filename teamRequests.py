from basketball_reference_scraper.teams import get_team_stats, get_opp_stats
from TEAM_ABBR import TEAM_TO_TEAM_ABBR
import connect as conn
from queries import create_tables, insert_teams, insert_stats, team_stats, team_stats_adv, user_input
from basketball_reference_scraper.players import get_stats
from nba_api.stats.static import teams
import json

from pandas import ExcelWriter

writer = ExcelWriter('NBA-2019_PerGameStats.xlsx')
team_dfs = []
sheets = []
team_list = []

# for t, a in TEAM_TO_TEAM_ABBR.items():
#     team_dfs.append(get_team_stats(a, 2019, 'PER_GAME').reset_index().transpose())
#     sheets.append(t)
#
# for df, sheet in zip(team_dfs, sheets):
#     df.to_excel(writer, sheet_name=sheet, startrow=0, startcol=0, index=False, header=False)

# writer.save()
#
# create_tables()

user_input()
