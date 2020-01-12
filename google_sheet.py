import pygsheets
import pymysql


# Init connection to the google sheet and return the sheet
def __init__():
    # Authorization with json token
    print('\nAuthorizing Google Sheet Access...')
    gc = pygsheets.authorize()
    # Return active worksheet
    return gc.open('Skyloft Poker Tracker V2.0')


def update_users(sh, db):
    ID = 0
    FIRST_NAME = 1
    LAST_NAME = 2
    VENMO = 4
    REGISTER_DATE = 7

    print('\nUpdating users on Google Sheet...')
    user_wks = sh.worksheet_by_title("Players")
    user_list = []

    try:
        cur = db.cursor()
        cur.execute('SELECT * FROM users')
        users = cur.fetchall()

        for user in users:
            user_id = user[ID]
            user_name = user[FIRST_NAME] + ' ' + user[LAST_NAME]
            venmo = user[VENMO]
            member_since = user[REGISTER_DATE].date().strftime("%m/%d/%Y")
            user_list.append([user_id, user_name, venmo, member_since])

        user_wks.update_values('B3', user_list)

        print('\nUpdate completed...')

    except pymysql.Error as e:
        print('\nFailed to show all users')
        print(e)


def update_sessions(sh, db):
    ID = 0
    DATE = 1
    DURATION = 4
    SMALL = 5
    BIG = 6
    BUY_IN = 7
    NUM_BUY_BACK = 10
    NUM_USER = 12

    print('\nUpdating sessions on Google Sheet...')
    session_wks = sh.worksheet_by_title("Session Log")
    session_list = []

    try:
        cur = db.cursor()
        cur.execute('SELECT * FROM session_log')
        sessions = cur.fetchall()

        for session in sessions:
            id = session[ID]
            date = session[DATE].strftime("%m/%d/%Y")
            duration = str(session[DURATION])
            small = str(session[SMALL])
            big = str(session[BIG])
            tot_buy_in = str(session[BUY_IN])
            num_buy_back = str(session[NUM_BUY_BACK])
            num_user = str(session[NUM_USER])

            session_list.append([id, date, duration, small, big, tot_buy_in, num_buy_back, num_user])

        session_wks.update_values('B3', session_list)

        total_session = len(session_list)

        print('\nUpdate completed...')

    except pymysql.Error as e:
        print('\nFailed to show all users')
        print(e)


def update_usere_stats(sh, db):
    ID = 0
    FIRST_NAME = 1
    LAST_NAME = 2
    TOT_BUY_IN = 3
    TOTAL_PROFIT = 4
    TOTAL_GAMES = 5
    TOTAL_TIME = 6
    AVG_PT_GAME = 7
    AVG_PT_HR = 8

    print('\nUpdating Stats on Google Sheet...')
    stats_wks = sh.worksheet_by_title("Stats")
    stats_list = []

    try:
        cur = db.cursor()
        cur.execute('''SELECT u.id, u.first_name, u.last_name, ps.total_buyin, ps.total_profit, ps.total_games,
                            ps.total_time, ps.avg_profit_game, ps.avg_profit_hour
                       FROM users u 
                       INNER JOIN player_stats ps on u.id = ps.player_id
        ''')
        stats = cur.fetchall()

        for stat in stats:
            id = stat[ID]
            name = stat[FIRST_NAME] + ' ' + stat[LAST_NAME]
            t_buy_in = str(stat[TOT_BUY_IN])
            t_pt = str(stat[TOTAL_PROFIT])
            t_games = stat[TOTAL_GAMES]
            t_time = str(stat[TOTAL_TIME])
            avg_game = str(stat[AVG_PT_GAME])
            avg_hr = str(stat[AVG_PT_HR])
            stats_list.append([id, name, t_buy_in, t_pt, t_games, t_time, avg_game, avg_hr])

        stats_wks.update_values('B3', stats_list)

        print('\nUpdate completed...')

    except pymysql.Error as e:
        print('\nFailed to show all users')
        print(e)


def update_ranking(sh, db):
    FIRST_NAME = 0
    LAST_NAME = 1
    ATTRIBUTE = 2

    print('\nUpdating Ranking on Google Sheet...')
    ranking_wks = sh.worksheet_by_title("Ranking")
    ranking_list = []
    count = 0

    try:
        cur = db.cursor()

        # Update total profit ranking #
        cur.execute('''SELECT u.first_name, u.last_name, ps.total_profit
                       FROM users u 
                       INNER JOIN player_stats ps on u.id = ps.player_id
                       ORDER BY ps.total_profit DESC
            ''')
        users = cur.fetchall()

        for user in users:
            name = user[FIRST_NAME] + ' ' + user[LAST_NAME]
            t_pt = str(user[ATTRIBUTE])
            count += 1
            ranking_list.append([count, name, t_pt])

        ranking_wks.update_values('A4', ranking_list)

        # Update profit/game ranking #
        # Reset variables
        count = 0
        ranking_list = []

        cur.execute('''SELECT u.first_name, u.last_name, ps.avg_profit_game
                               FROM users u 
                               INNER JOIN player_stats ps on u.id = ps.player_id
                               ORDER BY ps.avg_profit_game DESC
                    ''')
        users = cur.fetchall()

        for user in users:
            name = user[FIRST_NAME] + ' ' + user[LAST_NAME]
            avg_profit_game = str(user[ATTRIBUTE])
            count += 1
            ranking_list.append([count, name, avg_profit_game])

        ranking_wks.update_values('E4', ranking_list)

        # Update profit/hour ranking #
        # Reset variables
        count = 0
        ranking_list = []

        cur.execute('''SELECT u.first_name, u.last_name, ps.avg_profit_hour
                                       FROM users u 
                                       INNER JOIN player_stats ps on u.id = ps.player_id
                                       ORDER BY ps.avg_profit_hour DESC
                            ''')
        users = cur.fetchall()

        for user in users:
            name = user[FIRST_NAME] + ' ' + user[LAST_NAME]
            avg_profit_hour = str(user[ATTRIBUTE])
            count += 1
            ranking_list.append([count, name, avg_profit_hour])

        ranking_wks.update_values('I4', ranking_list)

        print('\nUpdate completed...')

    except pymysql.Error as e:
        print('\nFailed to show all users')
        print(e)


def update_tracker(sh, db):
    ID = 0
    FIRST_NAME = 1
    LAST_NAME = 2
    DATE = 3
    DURATION = 4
    BUY_IN = 5
    PROFIT = 6

    print('\nUpdating Tracker on Google Sheet...')
    tracker_wks = sh.worksheet_by_title("Tracker")
    tracker_wks.set_text_alignment("LEFT")
    tracker_list = []

    try:
        cur = db.cursor()

        cur.execute('''SELECT ps.session_id, u.first_name, u.last_name, ps.date, ps.duration, ps.buy_in, ps.profit
                       FROM users u 
                       INNER JOIN personal_session_log ps on u.id = ps.player_id
                       INNER JOIN session_log sl on ps.session_id = sl.id
                       ORDER BY ps.id
                ''')
        sessions = cur.fetchall()

        for session in sessions:
            id = session[ID]
            name = session[FIRST_NAME] + ' ' + session[LAST_NAME]
            date = str(session[DATE])
            duration = str(session[DURATION])
            buy_in = str(session[BUY_IN])
            profit = str(session[PROFIT])
            tracker_list.append([id, name, date, duration, buy_in, profit])

        tracker_wks.update_values('B3', tracker_list, horizontal_alignment=True)

    except pymysql.Error as e:
        print('\nFailed to show all users')
        print(e)


def update_facts(sh, db):
    facts_wks = sh.worksheet_by_title("Big Facts")

    total_buy_in = 0
    total_buy_back = 0
    total_user = 0

    facts_wks.update_value('B2', '{}')
    # facts_wks.update_value('B3', 'A total of {} games have been played on this table since Jan 2020.'.format(
    #     total_session))
    facts_wks.update_value('B4', '${} have been tossed around this table.'.format(total_buy_in))
    facts_wks.update_value('B5', 'People busted and bought back {} times.'.format(total_buy_back))
    facts_wks.update_value('B6', '{} people have gambled .'.format(total_buy_back))
