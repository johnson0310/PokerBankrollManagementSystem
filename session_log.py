import pymysql
import singleton
import util
import current_session
import performance_against
import personal_session_log
import player_stats
from datetime import datetime
from prettytable import PrettyTable

"""
    Session Log Table:
    id, session_date, session_starting_time, session_ending_time, session_duration
    small_blind, big_blind, session_buy_in, session_payout, session_difference
"""


# Return the status of active session
def is_session_active(db):
    return util.get_column_from_last_row(db, 'session_log', 'is_active')


# Start a new session
def start_session(db):
    print('\n' + '*' * 60)
    print('\nStarting a new session ...')

    cur = db.cursor()

    # Clear current session table
    try:
        cur.execute('''TRUNCATE TABLE current_session''')
    except pymysql.Error as e:
        cur.rollback()
        print('Failed to clear current session table.')
        print(e)
        return

    print('\nCurrent session table cleared.')

    try:
        # Add new session in to the session log
        query = '''INSERT INTO session_log (session_date, session_starting_time, small_blind, big_blind, total_num_users,is_active) 
        VALUES (%s, %s, %s, %s, %s, %s) '''

        small_blind, big_blind = singleton.get_blinds()
        current_time = datetime.now()
        total_num_users = 0
        is_active = 1
        value = (current_time.date(), current_time, small_blind, big_blind, total_num_users, is_active)

        cur.execute(query, value)

    except pymysql.Error as e:
        db.rollback()
        print("Failed to start a new session.")
        print(e)
        return

    # No error
    db.commit()

    latest_session_id = util.get_column_from_last_row(db, 'session_log', 'id')
    print('\nSession {} started successfully on {}.'.format(latest_session_id, current_time.date()))


# End the current session
def end_session(db):
    cur = db.cursor()

    print('\n' + '*' * 60)
    print('\nEnding the current session ...')

    ##### Update session_log with current session data #####

    # Check if all players were paid out
    cur.execute('''SELECT player_id FROM current_session WHERE paid_out = %s''', ('No',))
    rowcount = cur.rowcount
    if rowcount != 0:
        print('\nSome players are not paid out, get current session status and check again.')
        print('PAY THEM.')
        return

    # Fetch all player id, and determine number of players
    cur.execute('''SELECT player_id FROM current_session''')
    num_players = len(cur.fetchall())

    # Fetch session ending time, update session duration
    session_ending_time = datetime.now()
    session_duration = current_session.get_session_duration(db)

    # Fetch session buy in, Update session payout ,Update session payout difference
    total_session_buy_in, total_session_payout, total_difference = current_session.get_session_money_flow(db)

    # Turn the session log into not active
    is_active = 0

    # Find last session id
    latest_session_id = util.get_column_from_last_row(db, 'session_log', 'id')

    # Update all required fields
    try:

        query = '''UPDATE session_log SET session_ending_time = %s, session_duration = %s, session_buy_in = %s, 
        session_payout = %s, payout_difference = %s, is_active = %s, total_num_users = %s WHERE id = %s'''

        value = (
            session_ending_time, session_duration, total_session_buy_in, total_session_payout, total_difference,
            is_active,
            num_players, latest_session_id)

        cur.execute(query, value)

    except pymysql.Error as e:
        db.rollback()
        print("Failed to end the current session.")
        return

    db.commit()

    ##### Update personal_log with current session data #####
    personal_session_log.update(db)

    ##### Update performance_against with current session data #####
    performance_against.update(db)

    ##### Update player stats with current session data #####
    player_stats.update(db)

    ##### END #####
    print('\nSession Summary:')
    t_summary = PrettyTable(
        ['ID', 'Session Date', 'Session Duration', 'Small Blind', 'Big Blind', 'Number of Buy Backs',
         'Number of Players', 'Total Buy In'])

    cur.execute('''SELECT id, session_date, session_duration, small_blind, big_blind, number_buy_back, 
        total_num_users, session_buy_in FROM session_log WHERE id = %s''', (latest_session_id,))

    session_summary = cur.fetchone()
    t_summary.add_row(list(session_summary))
    print(t_summary)

    return 0
