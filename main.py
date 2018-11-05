from classes import Carro, Caminhao, Ponte
from queue import Queue
from threading import Thread, Condition
from random import randint
from time import sleep

N_CARROS = 10
N_CAMINHOES = 2
TA = [1, 2]


def gera_veiculo(**kwargs):
    fila = kwargs['fila']
    condition = kwargs['condition']
    origem = kwargs['origem']
    carros_gerados = 0
    caminhoes_gerados = 0
    while(carros_gerados+caminhoes_gerados < (N_CAMINHOES+N_CARROS)/2):
        # ZONA CRÍTICA
        with condition:
            # GERA CARRO
            if randint(0, 1):
                if carros_gerados < N_CARROS/2:
                    sleep(randint(TA[0], TA[1]))
                    carro = Carro(10, 2)
                    fila.put_nowait(carro)
                    carros_gerados += 1
                    print('Carro {} gerado na {}'.format(carros_gerados, origem.upper()))
            # GERA CAMINHÃO
            else:
                if caminhoes_gerados < N_CAMINHOES/2:
                    sleep(randint(TA[0], TA[1]))
                    caminhao = Caminhao(20)
                    fila.put_nowait(caminhao)
                    caminhoes_gerados += 1
                    print('Caminhão {} gerado na {}'.format(caminhoes_gerados, origem.upper()))
            
            # AVISA QUE EXISTE VEÍCULO NA FILA
            condition.notify_all()
        # FIM DA ZONA CRÍTICA
    print('\n\nGERAÇÃO NA {} CONCLUÍDA!'.format(origem.upper()))

def atravessa(**kwargs):
    origem_na_esquerda = kwargs['qe']
    origem_na_direita = kwargs['qr']
    cond_na_esquerda = kwargs['cond_na_esquerda']
    cond_na_direita = kwargs['cond_na_direita']

    while(True):
        comp = randint(0, 1)
        fila = origem_na_esquerda if comp else origem_na_direita
        condition = cond_na_esquerda if comp else cond_na_direita
        with condition:
            if fila.empty():
                condition.wait()
            v = fila.get_nowait()
            v.atravessar()


def main():
    cond_na_esquerda = Condition()
    cond_na_direita = Condition()
    qe = Queue()
    qr = Queue()

    gera_na_esquerda = Thread(target=gera_veiculo, kwargs={'fila': qe, 'condition': cond_na_esquerda, 'origem': 'esquerda'})
    gera_na_direita = Thread(target=gera_veiculo, kwargs={'fila': qr, 'condition': cond_na_direita, 'origem': 'direita'})

    gera_na_direita.start()
    gera_na_esquerda.start()

    gera_na_direita.join()
    gera_na_esquerda.join()


if __name__ == '__main__':
    main()
