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
