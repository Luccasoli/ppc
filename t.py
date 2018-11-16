import threading
import calendar

class V:
    def __init__(self, *args, **kwargs):
        self.valor = []


def recebe(**kwargs):
    x = kwargs['x']
    x.valor = 4

x = V()
x.valor = None
print(x.valor)
t = threading.Thread(target=recebe, kwargs={'x' :x})
t.start()
t.join()
print(x.valor)