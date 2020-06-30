
import psycopg2
from nba_api.stats.static import players
from connect import config
from TEAM_ABBR import TEAM_TO_TEAM_ABBR, TEAM_ABV_DICTIONARY
from basketball_reference_scraper.teams import get_team_stats, get_team_misc
from pandas import ExcelWriter

#Function if I want to create tables for database, right now putting data into excel sheets
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
    writer = ExcelWriter("NBA-%d_PerGameStats.xlsx" % year)

    # for t, a in TEAM_TO_TEAM_ABBR.items():
    #     team_dfs.append(get_team_stats(a, year, 'PER_GAME'))

    for t, a in TEAM_TO_TEAM_ABBR.items():
        team_dfs.append(get_team_stats(a, year, 'PER_GAME').reset_index().transpose())
        sheets.append(t)

    for df, sheet in zip(team_dfs, sheets):
        df.to_excel(writer, sheet_name=sheet, startrow=0, startcol=0, index=False, header=False)

    writer.save()

#queries needed if I want to put into a database ex.PostGres
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


def team_stats(team, year):
    team_dfs = []
    sheets = []

    print("Getting stats for " + team)
    writer = ExcelWriter("%s-%d_PerGameStats.xlsx" % (team,year))
    team_dfs.append(get_team_stats(team, year, 'PER_GAME').reset_index().transpose())
    sheets.append(team)

    for df, sheet in zip(team_dfs, sheets):
        df.to_excel(writer, sheet_name=team, startrow=0, startcol=0, index=False, header=False)

    writer.save()


def team_stats_adv(team, year):
    team_dfs = []
    sheets = []

    writer = ExcelWriter("%s-%d_AdvancedStats.xlsx" % (team, year))
    team_dfs.append(get_team_misc(team, year).reset_index().transpose())
    sheets.append(team)

    for df, sheet in zip(team_dfs, sheets):
        df.to_excel(writer, sheet_name=team, startrow=0, startcol=0, index=False, header=False)

    writer.save()
