from time import sleep

class Veiculo():
    '''
        tt = Tempo para atravessar a ponte
        it = Intervalo de tempo entre o próximo veiculo de mesmo tipo
    '''

    def __init__(self, tt, origem, tipo, it=0):
        self.tt = tt
        self.it = it
        self.origem = origem
        self.tipo = tipo

    def atravessar(self):
        sleep(self.tt)
        print('Atravessei')

class Carro(Veiculo):
    def __init__(self, tt, origem, tipo, it=0):
        super().__init__(tt, origem, tipo, it)


class Caminhao(Veiculo):
    def __init__(self, tt, origem, tipo, it=0):
        super().__init__(tt, origem, tipo, it)


class Ponte:
    def __init__(self):
        self.carros_atravessaram_para_esquerda = 0
        self.carros_atravessaram_para_direita = 0
        self.caminhoes_atravessaram_para_direita = 0
        self.caminhoes_atravessaram_para_esquerda = 0

    def atravessou(self, origem, tipo):
        if origem == 'esquerda':
            if tipo == 'carro':
                self.carros_atravessaram_para_direita += 1
            else:
                self.caminhoes_atravessaram_para_direita += 1
        elif origem == 'direita':
            if tipo == 'carro':
                self.carros_atravessaram_para_esquerda += 1
            else:
                self.caminhoes_atravessaram_para_esquerda += 1
        else:
            print('Origem incorreta!')         

    def total(self):
        return self.caminhoes_atravessaram_para_direita+self.caminhoes_atravessaram_para_esquerda+self.carros_atravessaram_para_direita+self.carros_atravessaram_para_esquerda     