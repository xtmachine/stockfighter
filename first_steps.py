from stockfighter import Stockfighter
from stockfighter import GM
import numpy as np

class Env(object):

    def __init__(self):
        self.action_space = Discrete() 
        self.observation_space = 0 # TODO

    def step(self, action):
        qty = 1
        if action == 0:
            direction = 'sell'
            self.state -= 1
        else:
            direction = 'buy'
            self.state += 1
        self.market.place_new_order(self.stock,
                                    None,
                                    qty,
                                    direction,
                                    'market')
        reward = self.state
        if self.state > 99:
            done = True
        else:
            done = False
        return np.array(self.state), reward, done, {}

    def reset(self):
        self.gm = GM()
        self.level = self.gm.start('first_steps')
        self.acct = self.level['account']
        self.venue = self.level['venues'][0]
        self.stock = self.level['tickers'][0]
        self.market = Stockfighter(self.venue, self.acct)
        self.order_book = self.market.orderbook_for_stock(self.stock)
        self.state = 0 # init position to 0 
        return np.array(self.state)

class Discrete(object):
    def __init__(self):
        self.n = 2

    def sample(self):
        return np.random.randint(self.n) 

    def contains(self, x):
        return x == 0 or x == 1
