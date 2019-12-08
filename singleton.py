# DEFAULT GLOBAL VARIABLE
SMALL_BLIND = 0.1
BIG_BLIND = 0.2
BUY_IN = 10
BANK_ID = 11


# Get blind sizes
def get_blinds():
    return SMALL_BLIND, BIG_BLIND


# Set blind sizes:
def set_blinds(small_blind, big_blind):
    global SMALL_BLIND
    global BIG_BLIND

    print('Small blind changed from ${} to ${}.'.format(SMALL_BLIND, small_blind))
    print('Big blind changed from ${} to ${}.'.format(BIG_BLIND, big_blind))

    SMALL_BLIND = small_blind
    BIG_BLIND = big_blind


# Get default buy in
def get_default_buy_in():
    return BUY_IN


# Get bank name
def get_bank_id():
    return BANK_ID
