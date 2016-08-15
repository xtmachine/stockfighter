from stockfighter import Stockfighter
from stockfighter import GM
from agent import Agent

# Start level 2
gm = GM()
level = gm.start('chock_a_block')

# Get venue and account information
acct = level['account']
venue = level['venues'][0]
symb = level['tickers'][0]

# Init market and agent
market = Stockfighter(venue=venue, account=acct)
agent = Agent(market, symb, 10, 10)

# Place random order
agent.rand_act()

# Place 10 random orders
for i in range(10):
    print agent.rand_act()
