from time import sleep


class Veiculo():
    '''
        tt = Tempo para atravessar a ponte
        it = Intervalo de tempo entre o próximo veiculo de mesmo tipo
    '''

    def __init__(self, id, tt, origem, tipo, it=0):
        self.id = id
        self.tt = tt
        self.it = it
        self.origem = origem
        self.tipo = tipo

    def atravessar(self, ja_atravessaram, qnt_total, ponte):
        sleep(self.tt)
        print('--- {} - {} atravessou! --- {}/{}\n'.format(self.tipo.upper(), self.id, ja_atravessaram+1, qnt_total))
        ponte.atravessou(self.origem, self.tipo)


class Carro(Veiculo):
    def __init__(self, id, tt, origem, tipo, it=0):
        super().__init__(id, tt, origem, tipo, it)


class Caminhao(Veiculo):
    def __init__(self, id,  tt, origem, tipo, it=0):
        super().__init__(id, tt, origem, tipo, it)


class Ponte:
    def __init__(self):
        self.carros_atravessaram_para_esquerda = 0
        self.carros_atravessaram_para_direita = 0
        self.caminhoes_atravessaram_para_direita = 0
        self.caminhoes_atravessaram_para_esquerda = 0
        self.ocupada = False

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

    def total_atravessou_para(self, destino):
        if destino == 'esquerda':
            return self.caminhoes_atravessaram_para_esquerda+self.carros_atravessaram_para_esquerda
        return self.caminhoes_atravessaram_para_direita+self.carros_atravessaram_para_direita

    def total(self):
        return self.caminhoes_atravessaram_para_direita+self.caminhoes_atravessaram_para_esquerda+self.carros_atravessaram_para_direita+self.carros_atravessaram_para_esquerda
