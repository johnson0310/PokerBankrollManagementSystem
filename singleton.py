# DEFAULT GLOBAL VARIABLE
SMALL_BLIND = 0.1
BIG_BLIND = 0.2
BUY_IN = 10
BANK = 'Johnson'


# Get blind sizes
def get_blinds():
    return SMALL_BLIND, BIG_BLIND


# Get default buy in
def get_default_buy_in():
    return BUY_IN


# Get bank name
def get_bank_name():
    return BANK
