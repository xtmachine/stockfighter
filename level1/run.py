from stockfighter import Stockfighter

# Globals
ACCT = 'SRB39147702'
VENUE = 'POMEX'
SYMB = 'TRI'

# Buy 100 shares
s = Stockfighter(venue=VENUE, account=ACCT)
s.place_new_order(SYMB, None, 100, 'buy', 'market')
