import datetime as datetime

import current_session
import users
import util

from prettytable import PrettyTable
import pymysql
from datetime import datetime, time

# Define returned query data position
USER_ID = 1
SESSION_BUY_IN = 2
SESSION_PAY_OUT = 3
SESSION_PROFIT = 4
ENTRY_TIME = 6
CASH_OUT_TIME = 7
PAY_OUT = 8


# Update all players long term stats
def update(db):
    # Fetch data from current session
    cur = db.cursor()
    cur.execute('''SELECT * FROM current_session''')
    session = cur.fetchall()

    print('\n' + '*' * 60)
    print('\nStart logging individual stats ...')

    ########### Add user into player stats table if they don't have an entry ###########
    cur.execute('''SELECT player_id FROM current_session WHERE player_id NOT IN (SELECT player_id FROM player_stats)''')
    new_user_entry = [i[0] for i in cur.fetchall()]

    if len(new_user_entry) != 0:
        query = '''INSERT INTO player_stats (player_id) VALUES (%s)'''
        cur.executemany(query, [(i,) for i in new_user_entry])
        db.commit()

    ########### Prepare user data for query ###########

    # Update user entries
    stats_update_list = []

    for user in session:
        # User id
        user_id = user[USER_ID]

        # Personal duration
        entry_time = user[ENTRY_TIME]
        cash_out_time = user[CASH_OUT_TIME]
        duration = util.elapsed_interval(entry_time, cash_out_time)

        # Buy in, profit
        buy_in = user[SESSION_BUY_IN]
        profit = user[SESSION_PROFIT]

        # Append to list
        stats_update_list.append((buy_in, profit, duration, user_id))

    ########### Update DB ###########
    try:
        query = '''UPDATE player_stats SET total_buyin = total_buyin + %s, total_profit =  total_profit + %s,
                    total_games = total_games + 1, total_time = ADDTIME(total_time, %s), 
                    avg_profit_game = round(total_profit / total_games, 2), avg_profit_hour = ROUND(total_profit / GREATEST(HOUR(total_time),1), 2) 
                    WHERE player_id = %s'''

        cur.executemany(query, [(i[0], i[1], i[2], i[3]) for i in stats_update_list])

    except pymysql.Error as e:
        db.rollback()
        print('Failed to update personal sessions.')
        return

    db.commit()
    print('\nUpdated all stats ...')


# Show stats for a specific player by nick_name
def show_stats_nick_name(db, nick_name):
    cur = db.cursor()

    # Fetch user id by nick name
    user_id = users.get_id_by_nick_name(db, nick_name)

    # Fetch user data
    cur.execute(
        '''SELECT player_id, total_buyin, total_profit, total_games, total_time, avg_profit_game, avg_profit_hour FROM player_stats WHERE player_id = %s''',
        (user_id,))
    user_summary = cur.fetchone()

    # Create summary table
    t_summary = PrettyTable(
        ['ID', 'Name', 'Total Buy in', 'Total Profit', 'Total Games', 'Total Game Time', 'Profit/Game', 'Profit/Hour'])

    user_summary = list(user_summary)
    user_summary.insert(1, nick_name)
    t_summary.add_row(user_summary)

    print(t_summary)


# Show stats for all users, sorted by passed argument
def show_stats_all(db, order_arg):
    cur = db.cursor()

    # Fetch all entries
    cur.execute(
        '''SELECT ps.player_id, concat(u.first_name, ' ',  u.last_name), ps.total_buyin, ps.total_profit, ps.total_games, ps.total_time, 
                  ps.avg_profit_game, ps.avg_profit_hour 
           FROM player_stats ps
           INNER JOIN users u on ps.player_id = u.id
           ORDER BY {} DESC'''.format(order_arg))
    users_summary = cur.fetchall()

    # Create summary table
    t_summary = PrettyTable(
        ['ID', 'Name', 'Total Buy in', 'Total Profit', 'Total Games', 'Total Game Time', 'Profit/Game', 'Profit/Hour'])

    for user in users_summary:
        t_summary.add_row(list(user))

    print(t_summary)
