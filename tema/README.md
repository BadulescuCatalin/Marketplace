333CC Badulescu Andrei-Catalin

Tema 1 ASC

Solutie:

   In thread-urile de producer am definit dictionarul de producer din marketplace.
Acesta contine cheia fiind id-ul producatorului, iar valoarea este un dictionar 
cu cheile produsele  pe care le furnizeaza si valorile cate astfel de produse a furnizat. 
Mai am inca o cheie Total_products care imi zice cate produse a frunizat in total pentru
a verifica mai usor daca poate sa mai adauge produse sau nu.
Apoi intr-un while True incerc sa adaug produse cat timp mai exista cumparatori.

   In thread-urile de consumer am definit un dictionar de cart-uri care care cheia
id-ul cart-ului, iar ca valoare are o lista de tupluri: produsul cumparat si id-ul
producatorului de la care l-a cumparat, pentru stii in ce dictionar sa il adaug
daca apoi urmeaza sa ii dea remove din cart. Mai departe am luat fiecare cart in
parte si am inceput sa adaug / sterg produse din cart. Apoi am apelat place_order
care din lista de tupluri imi intoare o lista de produse, pe care ulterior le afisez
dupa modelul dorit in tema.

   In marketplace am lista de producatori, de cart-uri si o lista de lock-uri pe care
le folosesc atunci cand incerc sa modific dictionarul unui producator ori in add_to_cart,
in remove_from_cart ori in publish.
    In new_cart si in register_producer doar am folosit un lock pentru a genera id-uri
unice fiecarui producator / cart pentru ca nu trebuie sa fie doi producatori / doua cart-uri 
care sa aibe acelasi id. 
    In publish eu mi-am pus o restrictie: pentru fiecare producator, nu pot sa produc
mai mult de queue_size / nr_tipuri_produse_furnizate_de_el produse de un anumit tip,
deoarece la testul 10 am observat ca se intampla cateodata ca producatorii sa isi
umple queue_size-ul doar cu produse care nu se cumpara, neavand apoi loc sa mai
produca din cele care chiar se cumparau.
    In add_to_cartdoar am cautat de unde pot sa iau si de acolo iau produsul, iar
in remove_from_cart pun produsul inapoi.
    Am creat si unittests pentru testarea functiilor din marketplace.


Observatii:
   -Tema mi-a placut si chiar a fost foarte interesanta. M-a ajutat sa invat mai
bine python si paralelizarea in python, dar am ivatat sa fac si unittesting
si logging.
    -Am mai multe comentarii utile in cod

Github:





