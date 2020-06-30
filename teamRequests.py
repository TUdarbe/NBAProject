from basketball_reference_scraper.teams import get_team_stats
from TEAM_ABBR import TEAM_TO_TEAM_ABBR
import connect as conn
from queries import create_tables, insert_teams, insert_stats, team_stats, team_stats_adv
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
insert_stats(2019)
insert_stats(2018)
team_stats('TOR', 2019)
team_stats_adv('TOR', 2019)
