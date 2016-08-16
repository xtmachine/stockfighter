from stockfighter import Stockfighter
from stockfighter import GM
import numpy as np

class env(object):

    def __init__(self):
        self.action_space = 0 # TODO
        self.observation_space = 0 # TODO

    def step(self, action):
        qty, direction = action
        self.market.place_new_order(self.stock,
                                    None,
                                    qty,
                                    direction,
                                    'market')

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

class action_space(object):
    def __init__(self, n):
        pass
