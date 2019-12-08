import util
import users
import pymysql
from datetime import datetime

# Define returned query data position
USER_ID = 1
SESSION_BUY_IN = 2
SESSION_PAY_OUT = 3
SESSION_PROFIT = 4
ENTRY_TIME = 6
CASH_OUT_TIME = 7
PAY_OUT = 8


# Update personal session logs
def update(db):
    # Fetch data from current session
    cur = db.cursor()
    cur.execute('''SELECT * FROM current_session''')
    session = cur.fetchall()

    print('\n' + '*' * 60)
    print('\nStart logging personal sessions ...')

    for user in session:
        session_id = util.get_column_from_last_row(db, 'session_log', 'id')
        user_id = user[USER_ID]
        entry_time = user[ENTRY_TIME]
        cash_out_time = user[CASH_OUT_TIME]
        duration = util.elapsed_interval(entry_time, cash_out_time)
        date = entry_time.date()
        buy_in = user[SESSION_BUY_IN]
        pay_out = user[SESSION_PAY_OUT]
        profit = user[SESSION_PROFIT]
        query = '''INSERT INTO personal_session_log (session_id, player_id, date, duration, buy_in, pay_out, 
        profit) VALUES (%s, %s, %s, %s, %s, %s, %s) '''
        value = (session_id, user_id, date, duration, buy_in, pay_out, profit)

        # Execute query
        try:
            cur.execute(query, value)
        except pymysql.Error as e:
            db.rollback()
            print('Failed to update personal sessions.')
            return

        db.commit()
        nick_name = users.get_nick_name_by_id(db, user_id)
        print('\nLogged sessions for "{}".'.format(nick_name))

    print('\nPersonal sessions logging completed ...')

