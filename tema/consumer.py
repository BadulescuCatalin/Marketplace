"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
from threading import Thread


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.kwargs = kwargs

    def run(self):
        name = self.kwargs['name']
        for cart in self.carts:
            cart_id = self.marketplace.new_cart()
            # in carts am o lista cu tupluri formate din produsele pe care
            # le-a pus in cart si id-ul producatorului care l-a furnizat
            self.marketplace.carts[cart_id] = []
            for action in cart:
                # extrag actiunile din cart
                action_type = action['type']
                prod = action['product']
                quantity = action['quantity']
                # incerc sa adaug sau sa sterg produsul din cart
                for _ in range(quantity):
                    if action_type == "add":
                        while self.marketplace.add_to_cart(cart_id, prod) is False:
                            time.sleep(self.retry_wait_time)
                    else:
                        self.marketplace.remove_from_cart(cart_id, prod)

            # fac o lista cu produsele care au fost in comanda finala si
            # o afisez dupa formatul dorit in teste
            cons_cart_list = self.marketplace.place_order(cart_id)
            for product in cons_cart_list:
                print(name + " bought " + str(product))
