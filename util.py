import re
from datetime import datetime as dt


# Converts tuple of strings into 1 string
def tuple_to_str(tup):
    result = ''.join(tup)
    return result


# Calculated elapsed interval
# start, end should be in datetime.now() format
def elapsed_interval(start, end):
    elapsed = end - start
    min, secs = divmod(elapsed.days * 86400 + elapsed.seconds, 60)
    hour, minutes = divmod(min, 60)
    return '%.2d:%.2d:%.2d' % (hour, minutes, secs)


# Find column in the last row of table
def get_column_from_last_row(db, table_name, column_name):
    cur = db.cursor()
    cur.execute('SELECT {} FROM {} ORDER BY {} DESC LIMIT 1'.format(column_name, table_name, column_name))
    return cur.fetchone()[0]


# Check if there's a space in the name
def name_space_checking(name):
    if ' ' in name:
        print('\nWhy is there a space in between characters you fool.')
        return 1
    return 0


# Check if first letter if capitalized
def name_initial_cap_checking(name):
    if name[:1].islower():
        print('\nFist letter has to be capitalized you fool.')
        return 1
    return 0


# Check for special characters
def name_special_char_checking(string):
    # Make own character set and pass
    # this as argument in compile method
    regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')

    # Pass the string in search
    # method of regex object.
    if regex.search(string) is not None:
        print("\nNo special characters you fool.")
        return 1
    return 0


# Check multiple name formatting rules
def name_format_checking(name):
    if name_space_checking(name) or name_initial_cap_checking(name) or name_special_char_checking(name):
        return 1
    return 0


# Check if venmo address starts from @
def venmo_address_format_checking(venmo_address):
    if venmo_address[:1] != '@':
        print('\nVenmo address has to start with "@" you fool.')
        return 1
    elif name_space_checking(venmo_address):
        return 1
    return 0


def password_format_checking(password):
    if name_space_checking(password):
        return 1
    return 0


# Shows how to use arguments
def help_documentation():
    print('\nUse the following command format for Poker BMS:')

    print('\nRegister new players to the database:')
    print('    add player : Enter First name, Last Name, Venmo Address (must start with @), and password')

    print('\nShow all registered players:')
    print('    show all players : All players will be sorted by ID')

    print('\nSession control:')
    print('    session start : Start a new game session')
    print('    session status : Shows summary of the current session')
    print('    session end : End the current game session')

    print('\nBuy in / buy back control:')
    print('    buy in player_name buy_in_amount: Buy in for player for buy_in_amount using venmo')
    print('    buy in cash player_name : Buy in for player using cash')
    print('    buy back player_name : Buy back max buy in for player')
    print('    buy back partial player_name player_current_holding: Partial buy back to max buy in for player, enter '
          'the amount the player currently has')
    print('    buy back player_name buy_in_amount: Buy back for any amount')

    print('\nCash out control:')
    print('    cash out player_name player_current_holding : Cash out the player with the player current holding')

    print('\nPay out control:')
    print('    pay out : Pay out every player using venmo. All players must be cashed out before paying out')

    print('\nIndividual stats:')
    print('    stats player_name : Shows long term stats for the player')
    print('    stats all : Shows long term stats for all players, default sorted by total profit')
    print('        stats all b: Sort by total buy in')
    print('        stats all p: Sort by total profit')
    print('        stats all g: Sort by total games')
    print('        stats all t: Sort by total time')
    print('        stats all pg: Sort by average profit/game')
    print('        stats all ph: Sort by average profit/hour')


    print('\nPoker BMS documentation:')
    print('    help : shows all commands and controls')

    print('\nExit program:')
    print('    quit : shuts down the program and quit')
