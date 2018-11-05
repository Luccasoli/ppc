from time import sleep

class Veiculo():
    '''
        tt = Tempo para atravessar a ponte
        it = Intervalo de tempo entre o próximo veiculo de mesmo tipo
    '''

    def __init__(self, tt, it=0):
        self.tt = tt
        self.it = it

    def atravessar(self):
        sleep(self.tt)
        print('Atravessei')

class Carro(Veiculo):
    def __init__(self, tt, it):
        super().__init__(tt, it)


class Caminhao(Veiculo):
    def __init__(self, tt):
        super().__init__(tt)


class Ponte:
    def __init__(self):
        self.carros_atravessaram_para_esquerda = 0
        self.carros_atravessaram_para_direita = 0
        self.caminhoes_atravessaram_para_direita = 0
        self.caminhoes_atravessaram_para_esquerda = 0
