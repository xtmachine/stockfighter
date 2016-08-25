import numpy as np
from stockfighter import Stockfighter
from stockfighter import GM
from gym import spaces

class Env(object):

    def __init__(self):
        self.action_space = spaces.Discrete(2)
        high = np.array([
            10000000,
            10000000,
            10000000])
        self.observation_space = spaces.Box(-high, high)

        self.gm = GM()
        self.level = self.gm.start('chock_a_block')
        self.instance_id = self.level['instanceId']
        self.acct = self.level['account']
        self.venue = self.level['venues'][0]
        self.stock = self.level['tickers'][0]
        self.market = Stockfighter(self.venue, self.acct)

        # initialize price
        self.mean_price = None
        while self.mean_price is None:
            self.mean_price = self.get_mean()

        self.start_price = self.mean_price # start price used for reward

        self.reset()

    def step(self, action):
        # place order
        qty = 25
        if action == 0:
            direction = 'sell'
        else:
            direction = 'buy'
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

        # update balance and position and mean
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

        self.mean_price = self.get_mean()

        self.state = [self.pos, self.bal, self.mean_price]
        print "iter:" + str(self.iter)
        print ['pos', 'bal', 'mean price']
        print self.state
        reward = 1 /(np.abs(self.mean_price - self.start_price) + 1)
        self.iter += 1

        # restart level if termination conditions are met
        if  self.iter > 500:
            done = True
        else:
            done = False

        return np.array(self.state), reward, done, {}

    def reset(self):
        self.iter = 0
        self.pending_orders = []
        self.completed_orders = []
        self.pos = 0
        self.bal = 0
        self.mean_price = self.get_mean()
        self.state = [self.pos, self.bal, self.mean_price]
        return np.array(self.state)

    def get_mean(self):
        """
        Gets the mean of prices in the order book
        if possible. Otherwise, it returns the previous mean.
        """
        prices = []
        book = self.market.orderbook_for_stock(self.stock)
        try:
            asks = book['asks']
            for ask in asks:
                prices.append(ask['price'])
            self.mean_price = np.mean(np.array(prices))
        except:
            pass
        return self.mean_price
