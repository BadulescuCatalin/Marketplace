"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
import logging
from logging.handlers import RotatingFileHandler
from threading import Lock
import unittest
import threading
from tema.product import Product, Coffee, Tea

logger = logging.getLogger('file_logger')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler("file.log", backupCount=100, maxBytes=10000000000)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
handler.formatter.converter = time.gmtime


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer

        # current_producer_id il folosesc ca sa generez id pentru producers
        self.current_producer_id = -1

        # current_cart_id il folosesc ca sa generez id pentru carturi
        self.current_cart_id = -1

        # dictionar de producers avand ca cheie id-ul producatorului
        # si ca valoare un dictionar cu chei produsele sale si valoare
        # numarul de produse
        self.producers = {}

        # dictionar de carturi in care cheile sunt id-urile carturilor
        # iar valorile sunt liste formate din tupluri care contine
        # numele produsului si id-ul producatorului de la care a cumparat
        self.carts = {}

        # lista cu lock-uri pentru fiecare producator pentru ca
        # dictionarele de producatori se modifica atat de producatori
        # cat si de consumatori
        self.producers_locks = []

        # lock pentru generarea de id_uri pentru producatori
        self.register_producer_lock = Lock()

        # lock petnru generarea id-urilor de carturi
        self.new_cart_lock = Lock()

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        logger.info("Am intrat in register_producer")
        with self.register_producer_lock:
            self.current_producer_id += 1
            self.producers_locks.append(Lock())
            logger.info("Am iesit din register_producer")
            return self.current_producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        logger.info("Am intrat in publish cu arg: producer_id = %s product = %s"
                    , producer_id, product)
        product_name = product[0]
        quantity = product[1]

        # daca am produs un numar de produse de un anumit tip mai mare decat
        # queue_size / nr de tipuri de produse furnizate de acel producator
        # nu mai adaug pentru ca acestea nu s-au cumparat si nu are
        # sens sa mai produc pentru ca o sa mi se umple queue_size-ul
        # doar cu produsul acesta si apoi nu voi mai putea sa produc
        # produsele care se cumpara
        if self.producers[producer_id][product_name] > \
                self.queue_size_per_producer / len(self.producers[producer_id]):
            logger.info("Am iesit din publish pe restrictie")
            return True

        # verific daca pot sa adaug produsul ( daca mai am loc )
        if self.producers[producer_id]['Total_products'] + quantity > self.queue_size_per_producer:
            logger.info("Am iesit din publish pe False")
            return False

        # daca pot pune produsul foloses lock-ul asignat producatorului
        # care il produce pentru ca dictionarul poate fi modificat si de
        # consumatori
        with self.producers_locks[producer_id]:
            self.producers[producer_id][product_name] += quantity
            self.producers[producer_id]['Total_products'] += quantity
            logger.info("Am iesit din publish si am pus in dictionar")
            return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        logger.info("Am intrat in new_cart")
        with self.new_cart_lock:
            self.current_cart_id += 1
            logger.info("Am iesit din new_cart")
            return self.current_cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        logger.info("Am intrat in add_to_cart cu arg: cart_id = %s product = %s"
                    , cart_id, product)

        # caut de la ce producator pot sa cumpar
        # ma uit intr-o copie a dictionarului pentru ca el se poate
        # modifica de catre alte threaduri
        for producer, producer_products in list(self.producers.items()):
            # daca gases de unde sa cumpar foloses lock-ul producatorului
            # si ii scot produsul de pe piata si il pun in cart
            if product in producer_products:
                with self.producers_locks[producer]:
                    if producer_products[product] > 0:
                        producer_products["Total_products"] = \
                            producer_products["Total_products"] - 1
                        producer_products[product] = producer_products[product] - 1
                        self.carts[cart_id].append((product, producer))
                        logger.info("Am iesit din add_to_cart pe True")
                        return True

        logger.info("Am iesit din add_to_cart pe False")
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        logger.info("Am intrat in remove_from_cart cu arg: cart_id = %s product = %s"
                    , cart_id, product)

        # caut produsul in lista cartului ca sa il scot din cart
        # si sa il pun inapoi in dictionarul producatorului
        for (prod, producer) in list(self.carts[cart_id]):
            if prod == product:
                # folosesc lock-ul producatorului ca sa modific dictionarul
                with self.producers_locks[producer]:
                    self.producers[producer]["Total_products"] = \
                        self.producers[producer]["Total_products"] + 1
                    self.producers[producer][prod] = self.producers[producer][prod] + 1
                    self.carts[cart_id].remove((prod, producer))
                    logger.info("Am iesit din remove_from_cart")
                    break

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        logger.info("Am intrat in place_order cu arg: cart_id = %s", cart_id)
        if len(self.carts[cart_id]) == 0:
            return []
        logger.info("Am iesit din place_order")

        # fac lista cu din cart doar cu produsul, pentru ca eu in cart
        # retin un tuplu cu produsul si idul producatorului de la care a luat
        return [product for (product, producer) in self.carts[cart_id]]


class TestMarketplace(unittest.TestCase):
    """
    Clasa care reprezinta unittestingul pentru metodele clasei Marketplace
    """

    def setUp(self):
        """
        metoda de setup unde mi-am creat un marketplace, numarul de
        thread-uri si cateva obiecte de tip Tea si Coffee
        """
        self.marketplace = Marketplace(10)
        self.threads = 5
        self.tea1 = Tea(name='Linden', price=9, type='Herbal')
        self.tea2 = Tea(name='Linden', price=9, type='Herbal')
        self.coffee1 = Coffee(name='Indonezia', price=1, acidity="5.05", roast_level='MEDIUM')
        self.coffee2 = Coffee(name='Indonezia', price=1, acidity="5.05", roast_level='MEDIUM')
        self.produs = Product(name="prod", price=10)

    def test_register_producer_int(self):
        """
        Test care verifica ca register_product sa intoarca un int
        """
        producer_id = self.marketplace.register_producer()
        self.assertIsInstance(producer_id, int)

    def test_register_producer_good_values(self):
        """
        Test care verifica ca register_product sa intoarca inturi consecutive
        incepand cu 0
        """

        for i in range(10):
            self.assertEqual(self.marketplace.register_producer(), i)

    def test_register_producer_not_repeated_values(self):
        """
        Test care verifica ca register_product sa nu intoarca valori repetate
        """

        ids = []
        for _ in range(10):
            ids.append(self.marketplace.register_producer())
        for i in range(10):
            for j in range(i + 1, 10):
                self.assertNotEqual(ids[i], ids[j])

    def test_register_producer_threads(self):
        """
        Test care verifica ca register_product sa mearga bine pe mai multe threaduri
        """

        app = [0, 0, 0, 0, 0]

        def register_producer_thread():
            """
            Threadul pentru register producer
            """

            producer_id = self.marketplace.register_producer()
            app[producer_id] += 1
            self.assertLessEqual(producer_id, self.threads - 1)

        threads = [threading.Thread(target=register_producer_thread) for _ in range(self.threads)]
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        for i in range(self.threads):
            self.assertEqual(app[i], 1)

    def test_publish(self):
        """
        Test care verifica ca publish sa mearga bine pe mai multe threaduri
        """

        product = (self.tea1, 1, 1)

        def publish_thread():
            """
            Threadul pentru publish
            """

            producer_id = self.marketplace.register_producer()
            self.marketplace.producers[producer_id] = {}
            self.marketplace.producers[producer_id]['Total_products'] = 0
            self.marketplace.producers[producer_id][self.tea1] = 0
            self.marketplace.publish(producer_id, product)

        threads = [threading.Thread(target=publish_thread) for _ in range(self.threads)]
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        for _, prod_info in self.marketplace.producers.items():
            self.assertEqual({'Total_products': 1, Tea(name='Linden', price=9, type='Herbal'): 1},
                             prod_info)

    def test_new_cart(self):
        """
        Test care verifica ca new_cart sa intoarca int-uri consecutive
        incepand cu 0, pe mai multe thread-uri
        """

        app = [0, 0, 0, 0, 0]

        def new_cart_thread():
            """
            Threadul de new_cart
            """

            cart_id = self.marketplace.register_producer()
            app[cart_id] += 1
            self.assertLessEqual(cart_id, self.threads - 1)

        threads = [threading.Thread(target=new_cart_thread) for _ in range(self.threads)]
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        for i in range(self.threads):
            self.assertEqual(app[i], 1)

    def test_add_to_cart(self):
        """
        Test care verifica ca add_to_cart adauge bine in dictionar
        """

        product = (self.tea1, 1, 1)

        producer_id = self.marketplace.register_producer()
        self.marketplace.producers[producer_id] = {}
        self.marketplace.producers[producer_id]['Total_products'] = 0
        self.marketplace.producers[producer_id][self.tea1] = 0
        for _ in range(10):
            self.marketplace.publish(producer_id, product)

        def add_to_cart_thread():
            """
            Threadul de add_to_cart
            """

            carts_id = self.marketplace.new_cart()
            self.marketplace.carts[carts_id] = []
            self.marketplace.add_to_cart(carts_id, product[0])

        threads = [threading.Thread(target=add_to_cart_thread()) for _ in range(self.threads)]
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        for _, cart_list in self.marketplace.carts.items():
            self.assertEqual(cart_list, [(self.tea1, 0)])

    def test_remove_from_cart(self):
        """
        Test care verifica ca remove_from_cart sa puna produsul inapoi in
        dictionarul producatorului de unde a cumparat si sa il scoata din cart
        """

        product = (self.tea1, 1, 1)

        producer_id = self.marketplace.register_producer()
        self.marketplace.producers[producer_id] = {}
        self.marketplace.producers[producer_id]['Total_products'] = 0
        self.marketplace.producers[producer_id][self.tea1] = 0
        for _ in range(5):
            self.marketplace.publish(producer_id, product)

        self.marketplace.carts = {0: [(Tea(name='Linden', price=9, type='Herbal'), 0)],
                                  1: [(Tea(name='Linden', price=9, type='Herbal'), 0)]}

        def remove_from_cart_thread():
            """
            Threadul de remove_from_cart
            """

            carts_id = 0
            self.marketplace.remove_from_cart(carts_id, product[0])

        threads = [threading.Thread(target=remove_from_cart_thread()) for _ in range(self.threads)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        for cart_id, cart_list in self.marketplace.carts.items():
            if cart_id == 0:
                self.assertEqual(cart_list, [])
            else:
                self.assertEqual(cart_list, [(self.tea1, 0)])

        self.assertEqual(self.marketplace.producers[0]["Total_products"], 6)

    def test_place_order(self):
        """
        Testul care verifica ca place_order sa imi intoarca o lista doar
        cu primele elemente din tuplurile primite
        """

        self.marketplace.carts[0] = [(self.tea1, 0), (self.tea2, 0),
                                     (self.coffee1, 0), (self.coffee2, 0)]
        self.assertEqual([self.tea1, self.tea2, self.coffee1, self.coffee2],
                         self.marketplace.place_order(0))
