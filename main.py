from classes import Carro, Caminhao, Ponte
from queue import Queue
from threading import Thread, Condition
from random import randint
from time import sleep

N_CARROS = 100
N_CAMINHOES = 2
TRAVESSIA_CARRO = 5
TRAVESSIA_CAMINHAO = 8
# Intervalo de geração de veículos
TA = [2, 6]


def gera_veiculo(**kwargs):
    fila = kwargs['fila']
    condition = kwargs['condition']
    origem = kwargs['origem']
    carros_gerados = 0
    caminhoes_gerados = 0

    while(carros_gerados < N_CARROS/2 or caminhoes_gerados < N_CAMINHOES/2):
        # ZONA CRÍTICA
        sleep(randint(TA[0], TA[1]))
        with condition:
            # GERA CARRO
            if randint(0, 1):
                if carros_gerados < N_CARROS/2:

                    carro = Carro('{}_{}'.format(
                        carros_gerados+1, origem.upper()), TRAVESSIA_CARRO, origem, 'carro', 2)
                    fila.put_nowait(carro)
                    carros_gerados += 1
                    print('Carro {} gerado na {}'.format(
                        carros_gerados, origem.upper()))
                    # print('Quantidade de carros na {}: {}\n'.format(
                    #     origem, carros_gerados))

                elif caminhoes_gerados < N_CAMINHOES/2:

                    caminhao = Caminhao('{}_{}'.format(
                        caminhoes_gerados+1, origem.upper()), TRAVESSIA_CAMINHAO, origem, 'caminhao')
                    fila.put_nowait(caminhao)
                    caminhoes_gerados += 1
                    print('Caminhão {} gerado na {}'.format(
                        caminhoes_gerados, origem.upper()))
                    # print('Quantidade de caminhões na {}: {}\n'.format(
                    #     origem, caminhoes_gerados))


            # GERA CAMINHÃO
            else:
                if caminhoes_gerados < N_CAMINHOES/2:

                    caminhao = Caminhao('{}_{}'.format(
                        caminhoes_gerados+1, origem.upper()), TRAVESSIA_CAMINHAO, origem, 'caminhao')
                    fila.put_nowait(caminhao)
                    caminhoes_gerados += 1
                    print('Caminhão {} gerado na {}'.format(
                        caminhoes_gerados, origem.upper()))
                    # print('Quantidade de caminhões na {}: {}\n'.format(
                    #     origem, caminhoes_gerados))
                elif carros_gerados < N_CARROS/2:

                    carro = Carro('{}_{}'.format(
                        carros_gerados+1, origem.upper()), TRAVESSIA_CARRO, origem, 'carro', 2)
                    fila.put_nowait(carro)
                    carros_gerados += 1
                    print('Carro {} gerado na {}'.format(
                        carros_gerados, origem.upper()))
                    # print('Quantidade de carros na {}: {}\n'.format(
                    #     origem, carros_gerados))

            # AVISA QUE EXISTE VEÍCULO NA FILA
            condition.notify_all()

        # FIM DA ZONA CRÍTICA
    print('\n\nGERAÇÃO NA {} CONCLUÍDA!'.format(origem.upper()))


def atravessa(**kwargs):
    fila = kwargs['fila']
    condition = kwargs['condition']
    origem = kwargs['origem']
    destino = kwargs['destino']
    ponte = kwargs['ponte']
    ponte_sync = kwargs['ponte_sync']
    threads = []

    while(True):
        with ponte_sync:
            if ponte.ocupada:
                print("*** PONTE OCUPADA ***")
                ponte_sync.wait()

            ponte.ocupada = True

            if ponte.total_atravessou_para(destino) >= (N_CAMINHOES+N_CARROS)/2:
                print("*** TODOS ATRAVESSARAM PARA A {} ***".format(destino))
                ponte.ocupada = False
                ponte_sync.notify_all()
                return

            with condition:
                if fila.empty():
                    condition.wait()

                veiculo = fila.get_nowait()

            print("UM {} VAI ATRAVESSAR!".format(veiculo.tipo.upper()))
            print('{} - {} - ATRAVESSANDO para {}'.format(veiculo.tipo, veiculo.id, destino))
            veiculo.atravessar(ponte.total(), N_CAMINHOES+N_CARROS)  # SLEEP
            # INCREMENTA NA PONTE
            ponte.atravessou(veiculo.origem, veiculo.tipo)

            ponte_sync.notify_all()
            ponte.ocupada = False
        # sleep(1)


def main():
    # Uma condição pra cada sentido de origem
    cond_na_esquerda = Condition()
    cond_na_direita = Condition()
    ponte_sync = Condition()

    # A ponte contabiliza os veiculos que atravessaram a mesma
    ponte = Ponte()

    # Armazena os veiculos de cada lado de origem
    qe = Queue()
    qr = Queue()

    gera_na_esquerda = Thread(target=gera_veiculo, kwargs={
                              'fila': qe, 'condition': cond_na_esquerda, 'origem': 'esquerda'})
    gera_na_direita = Thread(target=gera_veiculo, kwargs={
                             'fila': qr, 'condition': cond_na_direita, 'origem': 'direita'})
    travessia_para_direita = Thread(target=atravessa, kwargs={'fila': qe,
                                                              'condition': cond_na_esquerda,
                                                              'origem': 'esquerda',
                                                              'destino': 'direita',
                                                              'ponte_sync': ponte_sync,
                                                              'ponte': ponte})
    travessia_para_esquerda = Thread(target=atravessa, kwargs=
                                            {'fila': qr,
                                            'condition': cond_na_direita,
                                            'destino': 'esquerda',
                                            'origem': 'direita',
                                            'ponte_sync': ponte_sync,
                                            'ponte': ponte})

    gera_na_direita.start()
    gera_na_esquerda.start()
    travessia_para_direita.start()
    travessia_para_esquerda.start()

    gera_na_direita.join()
    gera_na_esquerda.join()
    travessia_para_direita.join()
    travessia_para_esquerda.join()


if __name__ == '__main__':
    main()
