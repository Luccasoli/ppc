from time import sleep


class Veiculo():
    '''
        tempo_de_travessia = Tempo para atravessar a ponte
        intervalo_entre_carros = Intervalo de tempo entre o próximo veiculo de mesmo tipo
    '''

    def __init__(self, id, tempo_de_travessia, origem, tipo, data_criacao, intervalo_entre_carros=0):
        self.data_criacao = data_criacao
        self.id = id
        self.tempo_de_travessia = tempo_de_travessia
        self.intervalo_entre_carros = intervalo_entre_carros
        self.origem = origem
        self.tipo = tipo

    def atravessar(self):
        sleep(self.tempo_de_travessia)
        print('--- {} - {} atravessou! --- \n'.format(self.tipo.upper(), self.id))


class Carro(Veiculo):
    def __init__(self, id, tempo_de_travessia, origem, tipo, data_criacao, intervalo_entre_carros=0):
        super().__init__(id, tempo_de_travessia, origem, tipo, data_criacao, intervalo_entre_carros)


class Caminhao(Veiculo):
    def __init__(self, id,  tempo_de_travessia, origem, tipo, data_criacao, intervalo_entre_carros=0):
        super().__init__(id, tempo_de_travessia, origem, tipo, data_criacao, intervalo_entre_carros)


class Ponte:
    def __init__(self):
        self.carros_atravessaram_para_esquerda = 0
        self.carros_atravessaram_para_direita = 0
        self.caminhoes_atravessaram_para_direita = 0
        self.caminhoes_atravessaram_para_esquerda = 0
        self.ocupada = False
        self.sentido = None

    def atravessou(self, origem, tipo, total):
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

        print('Quantidade total que já passou pela ponte: {}/{}'.format(self.total(), total))

    def total_atravessou_para(self, destino):
        if destino == 'esquerda':
            return self.caminhoes_atravessaram_para_esquerda+self.carros_atravessaram_para_esquerda
        return self.caminhoes_atravessaram_para_direita+self.carros_atravessaram_para_direita

    def total(self):
        return self.caminhoes_atravessaram_para_direita+self.caminhoes_atravessaram_para_esquerda+self.carros_atravessaram_para_direita+self.carros_atravessaram_para_esquerda

class UltimoCaminhao:
    def __init__(self, *args, **kwargs):
        self.caminhao = None