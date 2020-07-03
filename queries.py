import psycopg2
from nba_api.stats.static import players
from connect import config
from TEAM_ABBR import TEAM_TO_TEAM_ABBR, TEAM_ABV_DICTIONARY
from basketball_reference_scraper.teams import get_team_stats, get_team_misc, get_roster, get_roster_stats, get_opp_stats
from pandas import ExcelWriter


# Function if I want to create tables for database, right now putting data into excel sheets
def create_tables():
    queries = (
        """
               CREATE TABLE if not exists teams (
                   team_id SERIAL PRIMARY KEY,
                   team_name VARCHAR(255) NOT NULL,
                   abbreviation VARCHAR(3) NOT NULL
                   );
                 """,
        """
                CREATE TABLE if not exists players (
                     player_id INTEGER PRIMARY KEY,
                     full_name VARCHAR(255) NOT NULL,
                     first_name VARCHAR(30) NOT NULL, 
                     last_name VARCHAR(30) NOT NULL, 
                     is_active boolean NOT NULL
                );
        """,

        """
                CREATE TABLE if not exists team_stats_per_game (
                     team_id SERIAL PRIMARY KEY,
                     G SMALLINT NOT NULL,
                     MP DECIMAL(5,1) NOT NULL, 
                     FG NUMERIC(3, 1) NOT NULL, 
                     FGA NUMERIC(3, 1) NOT NULL, 
                     FG_PCT FLOAT(3) NOT NULL,
                     THREE_PTS NUMERIC(3, 1) NOT NULL, 
                     THREE_PTS_ATT NUMERIC(3, 1) NOT NULL,
                     THREE_POINTS_PCT FLOAT(3) NOT NULL, 
                     TWO_POINTS NUMERIC(3,1) NOT NULL, 
                     TWO_POINT_ATT NUMERIC(4,2) NOT NULL, 
                     TWO_POINT_PCT FLOAT(3) NOT NULL, 
                     FT NUMERIC(3,1) NOT NULL, 
                     FTA NUMERIC(3,1) NOT NULL, 
                     FT_PCT FLOAT(3) NOT NULL, 
                     ORB NUMERIC(3,1) NOT NULL, 
                     DRB NUMERIC(3,1) NOT NULL, 
                     TRB NUMERIC(3,1) NOT NULL, 
                     AST NUMERIC(3,1) NOT NULL, 
                     STL NUMERIC(3,1) NOT NULL,
                     BLK NUMERIC (3,1) NOT NULL, 
                     TOV NUMERIC (3,1) NOT NULL, 
                     PF NUMERIC(3,1) NOT NULL, 
                     PTS NUMERIC (5,2) NOT NULL, 
                     TEAM VARCHAR(3) NOT NULL, 
                     SEASON VARCHAR(7) NOT NULL                 
                );
        """

    )

    conn = None
    try:
        params = config()

        conn = psycopg2.connect(**params)
        print('Connected to database')
        cur = conn.cursor()

        for query in queries:
            cur.execute(query)

        cur.close()
        conn.commit()
        print('Queries completed')

    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    if __name__ == '__main__':
        create_tables()


def insert_teams():
    conn = None

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.executemany("""INSERT INTO teams(team_name, abbreviation) VALUES (%(team)s, %(abv)s)""",
                        TEAM_ABV_DICTIONARY)
        conn.commit()
        cur.close()
        print('Finished inserting data')

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def insert_players():
    conn = None
    player_list = players.get_active_players()
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.executemany("""INSERT INTO players VALUES 
                            (%(id)s, %(full_name)s, %(first_name)s, %(last_name)s, %(is_active)s)""",
                        player_list)
        conn.commit()
        cur.close()
        print('Finished inserting data')

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def insert_stats(year):
    team_dfs = []
    sheets = []

    writer = ExcelWriter("./Excel-Sheets/NBA-%d_PerGameStats.xlsx" % year)

    # for t, a in TEAM_TO_TEAM_ABBR.items():
    #     team_dfs.append(get_team_stats(a, year, 'PER_GAME'))

    for t, a in TEAM_TO_TEAM_ABBR.items():
        team_dfs.append(get_team_stats(a, year, 'PER_GAME').reset_index().transpose())
        sheets.append(t)

    for df, sheet in zip(team_dfs, sheets):
        df.to_excel(writer, sheet_name=sheet, startrow=0, startcol=0, index=False, header=False)

    writer.save()


# queries needed if I want to put into a database ex.PostGres
# try:
#     params = config()
#     conn = psycopg2.connect(**params)
#     cur = conn.cursor()
#     cur.executemany("""INSERT INTO team_stats_per_game VALUES
#                            (DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s,
#                           %s, %s, %s, %s, %s, %s, %s,
#                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
#                     teams_dfs)
#     conn.commit()
#     cur.close()
#     print('Finished inserting data')
#
# except (Exception, psycopg2.DatabaseError) as error:
#     print(error)
# finally:
#     if conn is not None:
#         conn.close()


#NEED LATER:

    # team_dfs = []
    # sheets = []
    #
    # writer = ExcelWriter("%s-%d_AdvancedStats.xlsx" % (team, year))
    # team_dfs.append(get_team_misc(team, year).reset_index().transpose())
    # sheets.append(team)
    #
    # for df, sheet in zip(team_dfs, sheets):
    #     df.to_excel(writer, sheet_name=team, startrow=0, startcol=0, index=False, header=False)
    #
    # writer.save()


def team_stats(team, year, data_format):

    print("Saving into excel sheet... ")
    writer = ExcelWriter("./Excel-Sheets/%s-%d_%s.xlsx" % (team, year, data_format))
    team_df = get_team_stats(team, year, data_format).reset_index().transpose()

    team_df.to_excel(writer, sheet_name=team, startrow=0, startcol=0, index=False, header=True)

    writer.save()


def team_opp_stats(team, year, data_format):

    print("Saving into excel sheet... ")
    writer = ExcelWriter("./Excel-Sheets/%s-%d_OPP-STATS_%s.xlsx" % (team, year, data_format))
    team_df = get_team_stats(team, year, data_format).reset_index().transpose()
    team_df.to_excel(writer, sheet_name=team, startrow=0, startcol=0, index=False, header=True)

    writer.save()


def roster_list(team, year):

    print("Saving into excel sheet... ")
    writer = ExcelWriter("./Excel-Sheets/%s-%d_Roster.xlsx" % (team, year))

    team_df = get_roster(team, year)
    print(team_df)

    team_df.to_excel(writer, sheet_name=team, startrow=0, startcol=0, index=False, header=True)

    writer.save()


def roster_stats(team, year, data_format, playoffs):

    print("Saving into excel sheet... ")
    writer = ExcelWriter("./Excel-Sheets/%s-%d_Roster_Stats_%s.xlsx" % (team, year, data_format))
    roster_stats_df = get_roster_stats(team, year, data_format, playoffs)

    roster_stats_df.to_excel(writer, sheet_name=team, startrow=0, startcol=0, index=False, header=True)

    writer.save()


def team_stats_adv(team, year):

    writer = ExcelWriter("%s-%d_AdvancedStats.xlsx" % (team, year))
    team_df = get_team_misc(team, year)
    team_df.to_excel(writer, sheet_name=team, startrow=0, startcol=0, index=False, header=True)

    writer.save()


def team_misc(team, year):
    print("Saving into excel sheet... ")
    writer = ExcelWriter("./Excel-Sheets/%s-%d_MISC_Stats.xlsx" % (team, year))
    roster_stats_df = get_team_misc(team, year).reset_index().transpose()

    roster_stats_df.to_excel(writer, sheet_name=team, startrow=0, startcol=0, index=False, header=True)

    writer.save()


def user_input():
    team_or_player = input("What stats would you like to see: (1)Team or (2)Player ")

    if team_or_player is '1':
        user_team = input("What team would you like to view? ")
        user_season = int(input("Enter the desired season: "))

        user_stats = input("Enter the number for what stat you would like to see: \n1.) Roster List\n"
                           "2.) Team Stats\n"
                           "3.) Team Opponent Stats\n"
                           "4.) Roster Stats\n"
                           "5.) Misc Stats\n")
        print_or_excel = input("Would you like to save information in an excel sheet (Y/N)? ")
        if user_stats is '1':
            if print_or_excel is 'Y' or 'y':
                roster_list(user_team, user_season)
                print(get_roster(user_team, user_season))
            elif print_or_excel is 'N' or 'n':

                print(get_roster(user_team, user_season))

        elif user_stats is '2':
            data_format = input("Enter data format: (TOTAL | PER_GAME): ").upper()

            if print_or_excel is 'Y' or 'y':
                team_stats(user_team, user_season, data_format)
                print(get_team_stats(user_team, user_season, data_format))

            elif print_or_excel is 'N' or 'n':
                print(get_team_stats(user_team, user_season, data_format))

        elif user_stats is '3':
            data_format = input("Enter data format: (TOTAL | PER_GAME: ").upper()

            if print_or_excel is 'Y' or 'y':
                team_opp_stats(user_team, user_season, data_format)
                print(get_opp_stats(user_team, user_season, data_format))

            elif print_or_excel is 'N' or 'n':
                print(get_opp_stats(user_team, user_season, data_format))

        elif user_stats is '4':
            user_playoffs = input("Would you like playoff roster stats? (Y/N) ")
            data_format = input("Enter data format: (TOTAL | PER_GAME): ").upper()
            playoffs = False

            if user_playoffs is 'Y' or 'y':
                playoffs = True
            if print_or_excel is 'Y' or 'y':
                roster_stats(user_team, user_season, data_format, playoffs)
                print(get_roster_stats(user_team, user_season, data_format, playoffs))
            elif print_or_excel is 'N' or 'n':
                print(get_roster_stats(user_team, user_season, data_format, playoffs))

        elif user_stats is '5':
            if print_or_excel is 'Y' or 'y':
                team_misc(user_team, user_season)
                print(get_team_misc(user_team, user_season))
            elif print_or_excel is 'N' or 'n':
                print(get_team_misc(user_team, user_season))

