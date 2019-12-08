import users
import current_session
import pymysql

# Define returned query data position
PLAYER_ID = 1
PROFIT = 4


def update(db):
    cur = db.cursor()

    print('\n' + '*' * 60)
    print('\nUpdating match up performance stats ...')

    # Fetch current session summary
    cur.execute('''SELECT * FROM current_session''')
    session_summary = cur.fetchall()

    if len(session_summary) < 2:
        print("\nYou can't play poker BY YOURSELF.")
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
        # If p1 is the last player in the list, break
        if p1 == len(session_user_list) - 1:
            break

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
        query = '''INSERT INTO performance_against (player1_id, player2_id, num_against, profit_difference) 
                VALUES (%s, %s, %s, %s) '''
        value = (vs_tuple[0], vs_tuple[1], 0, 0)

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
        user1_profit = session_summary[user1][PROFIT]

        # If reaches the last user, update completed
        if user1 == len(session_summary) - 1:
            break

        # Loop the rest of the users
        user2 = user1 + 1

        for user2 in range(len(session_summary)):
            if user1 == user2:
                continue

            user2_id = session_summary[user2][PLAYER_ID]
            user2_profit = session_summary[user2][PROFIT]

            user1_profit_difference = user1_profit - user2_profit

            query = '''UPDATE performance_against SET num_against = num_against + 1, profit_difference = 
            profit_difference + %s WHERE player1_id = %s AND player2_id = %s '''
            value = (user1_profit_difference, user1_id, user2_id)
            cur.execute(query, value)
            db.commit()

    print('\nMatch up status completed ...')