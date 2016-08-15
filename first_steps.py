from stockfighter import Stockfighter
from stockfighter import GM

class first_steps(object):

    def __init__(self):
        self.gm = GM()
        self.level = self.gm.start('first_steps')
        self.acct = self.level['account']
        self.venue = self.level['venues'][0]
        self.stock = self.level['tickers'][0]
        self.market = Stockfighter(self.venue, self.acct)
        self.order_book = self.market.orderbook_for_stock(self.stock)

    def _step(self, action):
        qty, direction = action
        self.market.place_new_order(self.stock,
                                    None,
                                    qty,
                                    direction,
                                    'market')
