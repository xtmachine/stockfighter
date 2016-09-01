import numpy as np
from stockfighter import Stockfighter
from stockfighter import GM
from gym import spaces

class Env(object):

    def __init__(self):

        # action space
        self.max_price = 10000
        self.min_price = 0
        self.max_qty = 100
        self.min_qty = 0
        self.max_dir = 1 # buy if max_dir > 0
        self.min_dir = -1
        self.action_max = np.array([self.max_price,
            self.max_qty,
            self.max_dir])
        self.action_min = np.array([self.min_price,
            self.min_qty,
            self.min_dir])
        self.action_space = spaces.Box(low = self.action_min,
                high = self.action_max)

        # observation space
        high = np.array([
            10000000,
            10000000,
            10000000])
        self.observation_space = spaces.Box(-high, high)

        self.gm = GM()
        self.level = self.gm.start('sell_side')
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
        reward = 0
        action = np.clip(action, self.action_min, self.action_max)
        # set price 
        try:
            if action[0] < 0:
                price = 0
            else:
                price = int(action[0])
        except:
            price = 0
        print "\nprice chosen:" + str(price)

        # set quantity
        try:
            if action[1] < 0:
                qty = 0
            else:
                qty = np.int(action[1])
        except:
            qty = 0
        print "qty chosen:" + str(qty)

        # set direction
        try:
            if action[2] > 0:
                direction = 'buy'
            else:
                direction = 'sell'
        except:
            direction = 'buy'
        print "direction chosen:" + direction

        print "action: " + str(action)

        order = self.market.place_new_order(self.stock,
                                            price,
                                            qty,
                                            direction,
                                            'limit')
        try:
            order_id = order['id']
            self.pending_orders.append(order_id)
        except:
            pass

        # update balance and position and mean
        old_pos = self.pos
        old_avg_cost = self.avg_cost
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
        #if self.avg_cost > .0001:
        #    reward = 1.0 / self.avg_cost
        #    # add additional reward if pos inc
        #    if self.pos - old_pos > 0:
        #        reward += 1.0 / self.avg_cost
        #else:
        #    reward = 0

        # reward for pos inc
        if self.pos - old_pos > 0:
            reward += 10
        # penalty for avg cost inc
        if self.avg_cost - old_avg_cost > 0:
            reward -= 5
        reward -= 1 # penalize for each step taken

        print "\nreward:" + str(reward) + "\n"

        self.iter += 1

        done = False

        # restart level if termination conditions are met
        #if  self.iter > 100:
        #    done = True
        #else:
        #    done = False

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
