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
        old_pos = self.pos
        # place order
        qty = 10
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
            order_id = order['id']
            self.pending_orders.append(order_id)
        except:
            pass

        # update balance and position
        for order_id in self.pending_orders:
            status = self.market.status_for_order(order_id, self.stock)
            if not status['open']:
                self.pending_orders.remove(order_id)
                for fill in status['fills']:
                    if status['direction'] == 'buy':
                        self.pos += fill['qty']
                        self.bal -= fill['qty'] * fill['price']
                    else:
                        self.pos -= fill['qty']
                        self.bal += fill['qty'] * fill['price']

        self.state = [self.pos, self.bal]
        print "iter:" + str(self.iter)
        print self.state
        reward = self.pos - old_pos 
        self.iter += 1

        # restart level if termination conditions are met
        if self.state[0] > 99 or self.state[0] < -99 or self.iter > 100:
            done = True
        else:
            done = False

        return np.array(self.state), reward, done, {}

    def reset(self):
        self.gm = GM()
        self.level = self.gm.start('first_steps')
        self.instance_id = self.level['instanceId']
        self.acct = self.level['account']
        self.venue = self.level['venues'][0]
        self.stock = self.level['tickers'][0]
        self.market = Stockfighter(self.venue, self.acct)
        self.iter = 0
        self.pending_orders = []
        self.completed_orders = []
        self.pos = 0
        self.bal = 0
        self.state = [self.pos, self.bal]
        return np.array(self.state)
