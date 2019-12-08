import users
import singleton
import util
import payment
import session_log
from datetime import datetime
from datetime import timedelta
import time
import pymysql
from prettytable import PrettyTable


##########################################
#                                        #
#            INTERNAL METHODS            #
#                                        #
##########################################
# Read players status and calculate current session money flow
def get_session_money_flow(db):
    total_session_buy_in = 0
    total_session_payout = 0
    total_difference = 0

    cur = db.cursor()
    cur.execute('''SELECT session_buy_in, session_payout FROM current_session''')
    money_flow = cur.fetchall()
    for entry in money_flow:
        total_session_buy_in += entry[0]
        total_session_payout += entry[1]

    total_difference = total_session_payout - total_session_buy_in

    return total_session_buy_in, total_session_payout, total_difference


# Get current session duration
def get_session_duration(db):
    current_time = datetime.now() + timedelta(seconds=1)
    cur = db.cursor()
    cur.execute('''SELECT session_starting_time FROM session_log ORDER BY id DESC LIMIT 1''')
    session_start_time = cur.fetchone()[0]
    return util.elapsed_interval(session_start_time, current_time)


# Get number of players in the current session
def get_num_users(db):
    cur = db.cursor()
    cur.execute('''SELECT player_id FROM current_session''')
    return cur.rowcount


# Buy in helper, payment method can be specified by "v" for venmo, "c" for cash
def buy_in_helper(db, nick_name, buy_in_method):
    # Active session check
    if not session_log.is_session_active(db):
        print("\nFailed to add user, there's no active game session you fool.")
        return

    # Valid user check
    if not users.is_user_by_nick_name(db, nick_name):
        print('\nNo matching player by name "{}", please register first.'.format(nick_name.capitalize()))
        return

    try:
        # Check if player is already in the current session
        cur = db.cursor()

        user_id = users.get_id_by_nick_name(db, nick_name)

        cur.execute('''SELECT player_id FROM current_session WHERE player_id = %s''', (user_id,))
        # Check if user id exists in current session
        row_count = cur.rowcount
        if row_count != 0:
            print('\nThis player is already playing you fool.')
            return

        print('\n' + '*' * 60)
        print('\nAdding Player "{}" to the current session ...'.format(nick_name.capitalize()))

        # Query
        query = '''INSERT INTO current_session (player_id, session_buy_in, session_payout, entry_time) VALUES  (
        %s, %s, %s, %s) '''

        # Value
        buy_in = singleton.get_default_buy_in()
        payout = 0
        entry_time = datetime.now()
        value = (user_id, buy_in, payout, entry_time)

        # Execute
        cur.execute(query, value)

    except pymysql.Error as e:
        db.rollback()
        print('Failed to add {} to the current session.'.format(nick_name.capitalize()))
        print(e)
        return

    # No error, commit changes
    db.commit()

    # Charge depending on payment method
    # Update payment method status
    if buy_in_method == 'v':
        print('\nPayment method: Venmo')
        cur.execute('''UPDATE current_session SET payment_method = %s WHERE player_id = %s''', ('Venmo', user_id))
        payment.buy_in(db, user_id)

    elif buy_in_method == 'c':
        print('\nPayment method: Cash')
        cur.execute('''UPDATE current_session SET payment_method = %s WHERE player_id = %s''', ('Cash', user_id))

    db.commit()
    print(
        '\n"{}" is buying in for ${} at {}.'.format(nick_name.capitalize(), singleton.get_default_buy_in(), entry_time))


# Buy back helper function, buys back for any amount, payment method can be specified by "v" for venmo, "c" for cash
def buy_back_helper(db, nick_name, amount, buy_back_method):
    # Active session check
    if not session_log.is_session_active(db):
        print("\nFailed to buy back, there's no active game session you fool.")
        return

    # Valid user check
    if not users.is_user_by_nick_name(db, nick_name):
        print('\nNo matching player by name "{}", please register first.'.format(nick_name.capitalize()))
        return

    # Give nick_name the amount
    try:
        cur = db.cursor()

        # Fetch user id by nick name
        user_id = users.get_id_by_nick_name(db, nick_name)

        # Fetch user data in current session

        # Check if the user is in the current session
        cur.execute('''SELECT session_buy_in FROM current_session WHERE player_id = %s''', (user_id,))
        row_count = cur.rowcount
        if row_count == 0:
            print('\n"{}" is not currently in the game session, add the player first.'.format(nick_name.capitalize()))
            return

        print('\n' + '*' * 60)
        print('\nBuying back for Player "{}" ...'.format(nick_name.capitalize()))

        # User exists, add amount to buy in
        user_total_buy_in = cur.fetchone()[0]
        user_total_buy_in = float(user_total_buy_in)
        user_total_buy_in += amount
        round(user_total_buy_in, 2)

        # Charge depending on payment method
        if buy_back_method == 'v':
            print('\nPayment method: Venmo')
            payment.buy_in(db, user_id)

        elif buy_back_method == 'c':
            print('\nPayment method: Cash')

        # Execute query for buy back amount update
        cur.execute('''UPDATE current_session SET session_buy_in = %s WHERE player_id = %s''',
                    (user_total_buy_in, user_id))

        # Execute query for number of buy backs update
        last_row_id = util.get_column_from_last_row(db, 'session_log', 'id')
        cur.execute('''UPDATE session_log SET number_buy_back = number_buy_back + 1 WHERE id = %s''', (last_row_id,))

    except pymysql.Error as e:
        db.rollback()
        print('Failed to buy back for "${}".'.format(nick_name.capitalize()))
        print(e)
        return

    # No error
    db.commit()
    print('\n"{}" just bought back for ${}, he is now ${} deep.'.format(nick_name.capitalize(), amount,
                                                                        user_total_buy_in))


# User partial buy back
def partial_buy_back(db, nick_name, left_over_amount, payment_method):
    # Check if the left over is below $2
    if float(left_over_amount) > 2:
        print('\nPlayers can only buy back when they are below $2.')
        return

    max_buy_back = float(singleton.get_default_buy_in())
    buy_back_amount = max_buy_back - float(left_over_amount)
    buy_back_helper(db, nick_name, buy_back_amount, payment_method)


# User full buy back
def default_buy_back(db, nick_name, payment_method):
    amount = singleton.get_default_buy_in()
    buy_back_helper(db, nick_name, amount, payment_method)


##########################################
#                                        #
#            EXTERNAL METHODS            #
#                                        #
##########################################
# All the buy in options
def buy_in_venmo(db, nick_name):
    buy_in_helper(db, nick_name, 'v')


def buy_in_cash(db, nick_name):
    buy_in_helper(db, nick_name, 'c')


# Partially buy back to default buy in, the left over amount of the amount of chips player is holding
def partial_buy_back_venmo(db, nick_name, left_over_amount):
    partial_buy_back(db, nick_name, left_over_amount, 'v')


def partial_buy_back_cash(db, nick_name, left_over_amount):
    partial_buy_back(db, nick_name, left_over_amount, 'c')


# Full buy back the default buy in
def default_buy_back_venmo(db, nick_name):
    default_buy_back(db, nick_name, 'v')


def default_buy_back_cash(db, nick_name):
    default_buy_back(db, nick_name, 'c')


# Cash out the player and record player's current amount of chips
def cash_out(db, nick_name, cash_out_amount):
    # If no active session, return
    if not session_log.is_session_active(db):
        print('No active game sessions, start a game and add some players.')
        return

    # Valid cash out amount check
    if float(cash_out_amount) < 0:
        print("\nCash out amount can't be below 0, try again.")
        return

    # Valid user check
    if not users.is_user_by_nick_name(db, nick_name):
        print('\nNo matching player by name "{}", please register first.'.format(nick_name.capitalize()))
        return

    try:
        # Check if player is in the current session
        cur = db.cursor()

        user_id = users.get_id_by_nick_name(db, nick_name)

        # Get entry and cash out time
        cash_out_time = datetime.now()
        cur.execute('''SELECT entry_time FROM current_session WHERE player_id = %s''', (user_id,))
        entry_time = cur.fetchone()[0]
        user_session_duration = util.elapsed_interval(entry_time, cash_out_time)

        # Calculate session profit and check if user is in current session
        cur.execute('''SELECT session_buy_in FROM current_session WHERE player_id = %s''', (user_id,))

        # Check if user id exists in current session
        row_count = cur.rowcount
        if row_count == 0:
            print('\n"{}" is not in the current game session, check your spelling.'.format(nick_name.capitalize()))
            return

        print('\n' + '*' * 60)
        print('\nCashing out for Player "{}" ...'.format(nick_name.capitalize()))

        cash_out_amount = float(cash_out_amount)
        session_buy_in = cur.fetchone()[0]
        session_profit = round(cash_out_amount - float(session_buy_in), 2)

        # Update pay out amount, session profit, and cash out time
        query = '''UPDATE current_session SET session_payout = %s, session_profit = %s, cash_out_time = %s WHERE 
        player_id = %s '''

        value = (cash_out_amount, session_profit, cash_out_time, user_id)
        cur.execute(query, value)

    except pymysql.Error as e:
        db.rollback()
        print('Failed to cash out "{}".'.format(nick_name.capitalize()))
        return

    db.commit()
    print('\nSuccessfully cashed out "{}".'.format(nick_name.capitalize()))

    if session_profit > 0:
        print('\n"{}" played for {} and won ${}.'.format(nick_name.capitalize(), user_session_duration,
                                                         round(session_profit, 2)))
    elif session_profit == 0:
        print('\n"{}" played for {} and broke even.'.format(nick_name.capitalize(), user_session_duration))
    elif session_profit < 0:
        print('\n"{}" played for {} and lost ${}.'.format(nick_name.capitalize(), user_session_duration,
                                                          abs(round(session_profit, 2))))

    # Check if user is currently in the game
    #  Update cashout time, payout amount, and session profit
    #  Update personal session info
    return 0


# Pays out according current session player standing
def auto_pay_out(db):
    print('\n' + '*' * 60)
    print('\nInitiating auto payout process ...')

    # Check if the current session is empty
    if get_num_users(db) == 0:
        print('\nUnable to auto pay out, there are no players in the current game session.')
        return

    # Check if all players are cashed out
    cur = db.cursor()
    yet_to_cash_out = []

    cur.execute('''SELECT u.id, u.nick_name, cs.session_payout ,cs.session_profit 
                    FROM users u
                    INNER JOIN current_session cs on u.id = cs.player_id
                    WHERE cs.paid_out = %s''', ('NO',))

    users_payout = cur.fetchall()

    for user_payout in users_payout:
        # if session_profit is None
        if user_payout[3] is None:
            # Append list with player nick name
            yet_to_cash_out.append(user_payout[1])

    # If the yet to cash out list is not empty, then stop paying out process
    # Print the player nick names that still require cash out
    if len(yet_to_cash_out) is not 0:
        # Some players are still in the game
        print('\nPlease cash out the following player/players and try again:')
        print(''.join(yet_to_cash_out))
        print('\n Auto payout process stopped ...')
        print('\n' + '*' * 60)
        return

    # All player cashed out, continue process
    # Update adjusted profit for all users
    cur.execute('''UPDATE current_session SET final_pay_out = session_payout''')

    # Check payout difference to ensure the house is not losing money
    # (total_buy_in, total_pay_out, difference)
    payout_difference = get_session_money_flow(db)[2]

    if payout_difference > 0:
        print('\nPayout difference > 0 detected ...')

        # All players with a positive payout will evenly split the difference
        # Select all players with positive payout
        cur.execute(
            '''SELECT player_id, session_payout FROM current_session WHERE session_payout > 0 AND paid_out = %s''',
            ('No',))

        num_positive_profit_user = cur.rowcount
        print('There are {} players with positive payout, they will split the difference evenly.'.format(
            num_positive_profit_user))

        avg_deduction = payout_difference / num_positive_profit_user
        print('The average deduction from each player will be ${}.'.format(avg_deduction))

        positive_payout_users = cur.fetchall()
        positive_payout_user_ids = []

        for user in positive_payout_users:
            positive_payout_user_ids.append(user[0])

        print(positive_payout_user_ids)

        # Update adjusted profit for all positive users
        cur.execute(
            '''UPDATE current_session SET final_pay_out = session_payout - %s WHERE player_id IN %s''',
            (avg_deduction, positive_payout_user_ids))
        db.commit()
        print('\nAdjusted payout updated ...')
        show_session_status(db)

        # Prompt bank to check the final payout amount
        arg = input('\nCheck final pay out amount, do they look correct? [y/n]')
        if arg == 'n':
            return
        elif arg == 'y':
            pass
        else:
            print('Please enter either "y" or "n".')
            return

    # Complete final payments
    print('\n' + '*' * 60)
    print('\nStarting auto payout process ...')

    # Get a tuple of tuples of user_ids and final pay out
    cur.execute('''SELECT player_id, final_pay_out FROM current_session WHERE final_pay_out > 0''')
    final_payouts = cur.fetchall()

    for individual_payout in final_payouts:
        user_id, final_payout_amount = individual_payout
        payment.pay_out(db, user_id, final_payout_amount)
        cur.execute('''UPDATE current_session SET paid_out = %s''', ('Yes',))

    print('\nAuto pay out completed ... ')
    print('\n' + '*' * 60)

    show_session_status(db)


# Prints current session status
def show_session_status(db):
    cur = db.cursor()
    cur.execute('''SELECT player_id from current_session''')

    # Check if user id exists in current session
    row_count = cur.rowcount
    if row_count == 0:
        print('\nThere are no players in the current session.')
        return

    cur.execute('''
                    SELECT u.id, u.nick_name,cs.session_buy_in, cs.session_payout, 
                           cs.session_profit, cs.payment_method,cs.entry_time, cs.cash_out_time, cs.final_pay_out,cs.paid_out
                    FROM users u
                    INNER JOIN current_session cs on u.id = cs.player_id
                    ''')
    players_status = cur.fetchall()

    # Session active status
    session_active = session_log.is_session_active(db)
    if session_active == 1:
        session_active = 'Yes'
    else:
        session_active = 'No'

    # Number of players
    num_players = cur.rowcount

    # Total buy in, payout, and difference
    total_session_buy_in, total_session_payout, total_difference = get_session_money_flow(db)

    # Current session duration
    session_duration = get_session_duration(db)

    # Create session status table
    t_session = PrettyTable(
        ['Number of Players', 'Duration', 'Total Buy In', 'Total Payout', 'Payout Difference', 'Active Session'])
    session_stats = [num_players, session_duration, total_session_buy_in, total_session_payout, total_difference,
                     session_active]
    t_session.add_row(session_stats)

    # Print players and stats in current session
    t_players = PrettyTable(
        ['ID', 'Name', 'Buy in', 'Pay out', 'Profit', 'Payment Method', 'Entry Time', 'Cash Out Time',
         'Final Payout', 'Paid out'])
    for player in players_status:
        t_players.add_row(list(player))

    print('\n' + '*' * 44 + '     Session Status     ' + '*' * 44)
    print(t_session)
    print(t_players)
