"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
from threading import Thread


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.kwargs = kwargs

    def run(self):
        # asignez un id producatorului
        id_prod = self.marketplace.register_producer()
        # voi avea un dictionar pentru producatori, cheia fiind id-ul producatorului
        # iar valoarea este un dictionar cu cheile produsele
        # pe care le furnizeaza si valorile cate astfel de produse a furnizat
        # mai am inca o cheie Total_products care imi zice cate produse a frunizat in total
        self.marketplace.producers[id_prod] = {}
        self.marketplace.producers[id_prod]['Total_products'] = 0
        for (prod, _, _) in self.products:
            self.marketplace.producers[id_prod][prod] = 0

        # cat timp am cunsmatori, trebuie sa produc
        while True:
            for (prod, quantity, wait_time) in self.products:
                # astept timpul de produs si incer sa produc
                time.sleep(wait_time)
                # cat timp nu pot sa produc astept si reincerc
                while self.marketplace.publish(id_prod, (prod, quantity, wait_time)) is False:
                    time.sleep(self.republish_wait_time)
