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

        # initialize vol
        self.buy_vol = None
        self.sell_vol = None
        while self.buy_vol is None or self.sell_vol is None:
            self.buy_vol, self.sell_vol = self.get_vol()

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
        old_pos = self.pos
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
        self.cost = -self.bal
        if self.pos > 0:
            self.avg_cost = self.cost / self.pos
        else:
            self.avg_cost = 0

        self.mean_price = self.get_mean()
        self.buy_vol, self.sell_vol = self.get_vol()

        self.state = [self.mean_price, self.buy_vol, self.sell_vol]

        print "iter:" + str(self.iter)
        print ['mean price', 'buy_vol', 'sell vol']
        print self.state

        # reward for keeping the price change small
        if self.avg_cost > .0001:
            reward = 1.0 / self.avg_cost
            # add additional reward if pos inc
            if self.pos - old_pos > 0:
                reward += 1.0 / self.avg_cost
        else:
            reward = 0


        print "reward:" + str(reward)

        self.iter += 1

        # restart level if termination conditions are met
        if  self.iter > 100:
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
        self.cost = -self.bal
        self.avg_cost = 0
        self.state = [self.mean_price, self.buy_vol, self.sell_vol]
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

    def get_vol(self):
        """
        Gets the vol of prices in the order book
        if possible. Otherwise, it returns the previous vol.
        """
        buy_vol = 0
        sell_vol = 0
        book = self.market.orderbook_for_stock(self.stock)
        try:
            asks = book['asks']
            for ask in asks:
                sell_vol += ask['qty']
            self.sell_vol = sell_vol
        except:
            pass
        try:
            bids = book['bids']
            for bid in bids:
                buy_vol += bid['qty']
            self.buy_vol = buy_vol
        except:
            pass
        return [self.buy_vol, self.sell_vol]
