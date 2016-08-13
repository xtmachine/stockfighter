from stockfighter import Stockfighter
from stockfighter import GM

# Start level 1
gm = GM()
level = gm.start('first_steps')

# Get venue and account information
acct = level['account']
venue = level['venues'][0]
symb = level['tickers'][0]

# Buy 100 shares
s = Stockfighter(venue=venue, account=acct)
s.place_new_order(symb, None, 100, 'buy', 'market')
