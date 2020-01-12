import users
import current_session
import pymysql
from prettytable import PrettyTable

# Define returned query data position
PLAYER_ID = 1
PLAYER1_NAME = 3
PLAYER2_NAME = 4
NUM_AGAINST = 5
TOTAL_PROFIT_DIFF = 6
PROFIT_DIFF_PER_GAME = 7

SESSION_PROFIT = 4


def update(db):
    cur = db.cursor()

    print('\n' + '*' * 60)
    print('\nUpdating match up performance stats ...')

    # Fetch current session summary
    cur.execute('''SELECT * FROM current_session''')
    session_summary = cur.fetchall()

    if len(session_summary) < 2:
        print("\nYou can't play poker BY YOURSELF.")
        print('Nothing updated ...')
        return

    ######## Insert if entry for p1 vs p2 doesn't exist ########
    cur.execute('''SELECT player1_id, player2_id FROM performance_against''')
    performance_summary = cur.fetchall()

    # Generate a list of vs status tuples for current session
    session_user_list = []
    vs_status = []
    for user in session_summary:
        session_user_list.append(user[PLAYER_ID])

    for p1 in range(len(session_user_list)):
        # Add vs tuple into vs list
        for p2 in range(len(session_user_list)):
            if p1 == p2:
                continue
            vs_status.append((session_user_list[p1], session_user_list[p2]))

    # Loop thru session tuples, if no match up info found on db, insert
    for vs_tuple in vs_status:

        if vs_tuple in performance_summary:
            continue

        # No logged match up, INSERT INTO database
        p1_nick_name = users.get_nick_name_by_id(db, vs_tuple[0])
        p2_nick_name = users.get_nick_name_by_id(db, vs_tuple[1])

        query = '''INSERT INTO performance_against (player1_id, player2_id, player1_nick_name, player2_nick_name,
        num_against, total_profit_difference, profit_difference_per_game) 
        
                VALUES (%s, %s, %s, %s, %s, %s, %s) '''
        value = (vs_tuple[0], vs_tuple[1], p1_nick_name, p2_nick_name, 0, 0, 0)

        try:
            cur.execute(query, value)
        except pymysql.Error as e:
            db.rollback()
            print('\nFailed to insert match up "{}" vs "{}".'.format(users.get_nick_name_by_id(db, vs_tuple[0]),
                                                                     users.get_nick_name_by_id(db,
                                                                                               vs_tuple[1])))
            print(e)
            return

        db.commit()

    ######## Update if entry for p1 vs p2 exist #######
    for user1 in range(len(session_summary)):
        user1_id = session_summary[user1][PLAYER_ID]
        user1_profit = session_summary[user1][SESSION_PROFIT]

        for user2 in range(len(session_summary)):
            if user1 == user2:
                continue

            user2_id = session_summary[user2][PLAYER_ID]
            user2_profit = session_summary[user2][SESSION_PROFIT]

            user1_profit_difference = float(user1_profit) - float(user2_profit)

            query = '''UPDATE performance_against SET num_against = num_against + 1, total_profit_difference = 
            total_profit_difference + %s, profit_difference_per_game = total_profit_difference / num_against WHERE player1_id = %s AND player2_id = %s '''
            value = (user1_profit_difference, user1_id, user2_id)
            cur.execute(query, value)
            db.commit()

    print('\nMatch up status completed ...')


# Show performance by user nick_name
def show_performance_by_nick_name(db, nick_name):
    cur = db.cursor()

    # Fetch user data
    user_id = users.get_id_by_nick_name(db, nick_name)

    cur.execute('''SELECT pa.player1_nick_name, pa.player2_nick_name, pa.num_against, pa.total_profit_difference,
                          pa.profit_difference_per_game 
                   FROM performance_against pa
                   INNER JOIN users u on pa.player1_id = u.id
                   WHERE pa.player1_id = %s
                   ORDER BY profit_difference_per_game DESC
                    ''', (user_id,))

    performance_summary = cur.fetchall()

    # If no row found, return
    if cur.rowcount == 0:
        print('\nNo performance history found for {}'.format(nick_name.capitalize()))
        return

    # Print in table
    t_summary = PrettyTable(
        ['Name', 'Player Against', 'Number of Encounter', 'Total Profit Difference', 'Profit Difference/Game'])

    for elem in performance_summary:
        t_summary.add_row(list(elem))

    print(t_summary)


# Show performance by all
def show_performance_by_all(db):
    cur = db.cursor()

    # Fetch all user data
    cur.execute('''SELECT pa.player1_nick_name, pa.player2_nick_name, pa.num_against, pa.total_profit_difference,
                          pa.profit_difference_per_game 
                   FROM performance_against pa
                   ORDER BY id''')

    performance_summary = cur.fetchall()
    # If no row found, return
    if cur.rowcount == 0:
        print('\nNo performance history found.')
        return

    # Print table
    t_summary = PrettyTable(
        ['Name', 'Player Against', 'Number of Encounter', 'Total Profit Difference', 'Profit Difference/Game'])

    for elem in performance_summary:
        t_summary.add_row(list(elem))

    print(t_summary)
