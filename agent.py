import random

class Agent(object):
    def __init__(self, market, symb, max_price=100, max_qty=100):
        self.market = market
        self.symb = symb
        self.max_price = max_price
        self.max_qty = max_qty

        # Price and quantity must be non-negative
        if max_price < 0:
            raise ValueError('Max price must be non-negative.')
        if max_qty < 0:
            raise ValueError('Max quantity must be non-negative')

    def rand_act(self):
        # Determine price
        #price = random.randint(0, self.max_price)
        price = None

        # Determine quantity
        qty = random.randint(0, self.max_qty)

        # Determine direction 
        direction = 'buy'
        if random.random() < .5:
            direction = 'sell'

        # Determine order_type
        #types = ['limit', 'market', 'fill-or-kill', 'immediate-or-cancel']
        types = ['market']
        type_idx = random.randint(0, len(types)-1)
        order_type = types[type_idx]

        # Place order
        order = self.market.place_new_order(self.symb, price, qty, direction, order_type)
        return order


