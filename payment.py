import singleton
import venmo

current_bank = singleton.get_bank_name()


# Charge user default buy in amoung
def buy_in(user):
    # If the added user is the bank, then stop
    if user.nick_name == current_bank:
        print("\nDon't you charge the bank himself you fool.")
        return

    # User is not bank
    user_venmo = user.venmo_address

    try:
        print('payed without auth')
        # venmo.payment.charge(user_venmo, singleton.get_default_buy_in(), 'Congratulations, you are one step closer to '
        #                                                                  'becoming a degenerate.')
    except KeyError as e:
        # If catches a key error, re-auth and charge again
        print('\nCurrent access token expired')
        venmo.auth.configure()
        print('paid with auth')
        # venmo.payment.charge(user_venmo, singleton.get_default_buy_in(), 'Congratulations, you are one step closer to '
        #                                                                  'becoming a degenerate.')
