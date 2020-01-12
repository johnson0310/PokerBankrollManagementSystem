import init
import users
import player_stats
import current_session
import performance_against
import personal_session_log
import session_log
import personal_session_log
import player_stats
import payment
import google_sheet
import util
import pymysql
import time
import venmo
from contextlib import closing
from datetime import datetime

##### Init mySQL connection #####
db, cur = init.init_sql()

##### Main #####
with closing(db.cursor()) as cur:
    print('\n' + '*' * 60)
    print('\nWelcome to the Poker Bankroll Management System ... ...')

    # Define arg position
    ONE = 0
    TWO = 1
    THREE = 2
    FOUR = 3
    FIVE = 4

    # Parse arguments
    while True:
        try:
            argument = input('\nPoker BMS --> ')
            argument_list = argument.lower().split(" ")

            if argument_list[ONE] == 'session':
                if argument_list[TWO] == 'start':
                    session_log.start_session(db)

                elif argument_list[TWO] == 'status':
                    current_session.show_session_status(db)

                elif argument_list[TWO] == 'end':
                    session_log.end_session(db)

            elif argument_list[ONE] == 'add':
                if argument_list[TWO] == 'player':
                    first_name = input('    First name: ')
                    last_name = input('    Last name: ')
                    venmo_address = input('    Venmo address: ')
                    users.add_new_user(db, (first_name, last_name, venmo_address, 1234))

            elif argument_list[ONE] == 'show':
                if argument_list[TWO] == 'all':
                    if argument_list[THREE] == 'players':
                        users.show_all_users(db)

            elif argument_list[ONE] == 'buy':
                if argument_list[TWO] == 'in':
                    if len(argument_list) == 4:
                        current_session.buy_in_venmo(db, argument_list[THREE], argument_list[FOUR])
                    elif argument_list[THREE] == 'cash':
                        current_session.buy_in_cash(db, argument_list[THREE], argument_list[FOUR])

                elif argument_list[TWO] == 'back':
                    if len(argument_list) == 3:
                        current_session.default_buy_back_venmo(db, argument_list[THREE])
                    elif len(argument_list[THREE]) == 4:
                        current_session.any_buy_back_venmo(db, argument_list[THREE], argument_list[FOUR])
                    elif argument_list[THREE] == 'partial':
                        current_session.partial_buy_back_venmo(db, argument_list[FOUR], argument_list[FIVE])


            elif argument_list[ONE] == 'cash':
                if argument_list[TWO] == 'out':
                    current_session.cash_out(db, argument_list[THREE], argument_list[FOUR])
                print()

            elif argument_list[ONE] == 'stats':
                if argument_list[TWO] == 'all' and len(argument_list) == 2:
                    player_stats.show_stats_all(db, 'total_profit')

                elif argument_list[TWO] == 'all' and argument_list[THREE] == 'id':
                    player_stats.show_stats_all(db, 'player_id')

                elif argument_list[TWO] == 'all' and argument_list[THREE] == 'b':
                    player_stats.show_stats_all(db, 'total_buyin')

                elif argument_list[TWO] == 'all' and argument_list[THREE] == 'p':
                    player_stats.show_stats_all(db, 'total_profit')

                elif argument_list[TWO] == 'all' and argument_list[THREE] == 'g':
                    player_stats.show_stats_all(db, 'total_games')

                elif argument_list[TWO] == 'all' and argument_list[THREE] == 't':
                    player_stats.show_stats_all(db, 'total_time')

                elif argument_list[TWO] == 'all' and argument_list[THREE] == 'pg':
                    player_stats.show_stats_all(db, 'avg_profit_game')

                elif argument_list[TWO] == 'all' and argument_list[THREE] == 'ph':
                    player_stats.show_stats_all(db, 'avg_profit_hour')

                elif len(argument_list) == 2:
                    player_stats.show_stats_nick_name(db, argument_list[TWO])

            elif argument_list[ONE] == 'performance':
                if argument_list[TWO] == 'all':
                    performance_against.show_performance_by_all(db)
                elif len(argument_list) == 2:
                    performance_against.show_performance_by_nick_name(db, argument_list[TWO])

            elif argument_list[ONE] == 'pay':
                if argument_list[TWO] == 'out':
                    current_session.auto_pay_out(db)

            elif argument_list[ONE] == 'help':
                util.help_documentation()

            elif argument_list[ONE] == 'quit':
                # Check for current active sesison
                if session_log.is_session_active(db) == 1:
                    arg = input("\nCurrently there's an active game session, are you sure you want to quit? [y/n]")
                    if arg == 'y':
                        print('\nThanks for using Poker BMS ... ')
                        break
                    elif arg == 'n':
                        continue
                    else:
                        print('\nPlease enter a valid option.')
                else:
                    print('\nThanks for using Poker BMS ... ')
                    break
        except IndexError as e:
            print('\nArguments not valid, please look at the documentation and try again.')
            continue

    # session_log.start_session(db)
    #
    # current_session.buy_in_venmo(db, 'Ben')
    # current_session.buy_in_venmo(db, 'Kate')
    # current_session.buy_in_cash(db, 'Johnson')
    # current_session.buy_in_venmo(db, 'Carter')
    # current_session.buy_in_venmo(db, 'Austin')
    # current_session.buy_in_venmo(db, 'Nihar')
    # current_session.buy_in_venmo(db, 'ASD')
    # current_session.show_session_status(db)
    # time.sleep(1)
    #
    # current_session.default_buy_back_venmo(db, "Ben")
    # current_session.default_buy_back_venmo(db, "Johnson")
    # current_session.show_session_status(db)
    # time.sleep(1)
    #
    # current_session.cash_out(db, 'Johnson', 20)
    # current_session.cash_out(db, 'Ben', 20)
    # current_session.cash_out(db, 'Carter', 40)
    # current_session.cash_out(db, 'ASD', 20)
    # current_session.cash_out(db, 'Austin', 10)
    # current_session.cash_out(db, 'Nihar', 0)
    # current_session.cash_out(db, 'Kate', 0)
    # current_session.show_session_status(db)
    # time.sleep(1)
    #
    # current_session.auto_pay_out(db)
    # #
    # session_log.end_session(db)

db.close()
