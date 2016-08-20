import numpy as np
from stockfighter import Stockfighter
from stockfighter import GM
from gym import spaces

class Env(object):

    def __init__(self):
        self.action_space = spaces.Discrete(2) 
        self.observation_space = spaces.Box(-10000, 10000, (2,)) 
        self.reset()

    def step(self, action):
        qty = 1
        if action == 0:
            direction = 'sell'
            self.state[0] -= qty
        else:
            direction = 'buy'
            self.state[0] += qty
        order = self.market.place_new_order(self.stock,
                                    None,
                                    qty,
                                    direction,
                                    'market')
        try:
            print order['direction']
        except:
            pass
        print self.state
        reward = self.state[0]
        self.iter += 1
        if self.state[0] > 500 or self.state[0] < -25 or self.iter > 500:
            done = True
            self.gm.restart(self.instance_id)
        else:
            done = False
        return np.array(self.state), reward, done, {}

    def reset(self):
        self.iter = 0
        self.gm = GM()
        self.level = self.gm.start('first_steps')
        self.instance_id = self.level['instanceId']
        self.acct = self.level['account']
        self.venue = self.level['venues'][0]
        self.stock = self.level['tickers'][0]
        self.market = Stockfighter(self.venue, self.acct)
        self.order_book = self.market.orderbook_for_stock(self.stock)
        self.state = [0,0] # init position to 0 
        return np.array(self.state)
