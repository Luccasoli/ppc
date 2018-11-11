from classes import Carro, Caminhao, Ponte
from queue import Queue
from threading import Thread, Condition, Semaphore
from random import randint
from time import sleep, time

N_CARROS = 100
N_CAMINHOES = 6
TRAVESSIA_CARRO = 5
TRAVESSIA_CAMINHAO = 8
INTERVALO_CARROS = 2
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
                    carro = Carro(carros_gerados+1,
                                  TRAVESSIA_CARRO, origem, 'carro', 2)
                    fila.put_nowait(carro)
                    carros_gerados += 1
                    # print('Carro {} gerado na {}'.format(carros_gerados, origem.upper()))

                elif caminhoes_gerados < N_CAMINHOES/2:
                    caminhao = Caminhao(caminhoes_gerados+1,
                                        TRAVESSIA_CAMINHAO, origem, 'caminhao')
                    fila.put_nowait(caminhao)
                    caminhoes_gerados += 1
                    # print('Caminhão {} gerado na {}'.format(caminhoes_gerados, origem.upper()))

            # GERA CAMINHÃO
            else:
                if caminhoes_gerados < N_CAMINHOES/2:
                    caminhao = Caminhao(caminhoes_gerados+1,
                                        TRAVESSIA_CAMINHAO, origem, 'caminhao')
                    fila.put_nowait(caminhao)
                    caminhoes_gerados += 1
                    # print('Caminhão {} gerado na {}'.format(caminhoes_gerados, origem.upper()))
                elif carros_gerados < N_CARROS/2:
                    carro = Carro(carros_gerados+1,
                                  TRAVESSIA_CARRO, origem, 'carro', 2)
                    fila.put_nowait(carro)
                    carros_gerados += 1
                    # print('Carro {} gerado na {}'.format(carros_gerados, origem.upper()))

            # AVISA QUE EXISTE VEÍCULO NA FILA
            condition.notify_all()

        # FIM DA ZONA CRÍTICA
    # print('\n{} GERAÇÃO NA {} CONCLUÍDA!'.format(40*'-', origem.upper()))


def atravessar_aux(**kwargs):
    destino = kwargs['destino']
    veiculo = kwargs['veiculo']
    ponte = kwargs['ponte']
    semaforo = kwargs['semaforo']

    seta = ' --> ' if destino == 'direita' else ' <-- '

    print('{} {} - {} INICIOU A TRAVESSIA PELA {}!'.format(seta,
                                                           veiculo.tipo.upper(), veiculo.id, veiculo.origem.upper()))
    veiculo.atravessar()  # SLEEP
    with semaforo:
        ponte.atravessou(veiculo.origem, veiculo.tipo, N_CAMINHOES+N_CARROS)


def atravessa(**kwargs):
    fila = kwargs['fila']
    condition = kwargs['condition']
    origem = kwargs['origem']
    destino = kwargs['destino']
    ponte = kwargs['ponte']
    ponte_sync = kwargs['ponte_sync']
    threads = []
    veiculos = []
    caminhao_aux = None

    while(True):
        sleep(1)
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
                while(not fila.empty()):
                    if caminhao_aux:
                        veiculos.append(caminhao_aux)
                        caminhao_aux = None
                        break

                    v = fila.get_nowait()

                    if v.tipo == 'caminhao':
                        if len(veiculos) == 0:
                            veiculos.append(v)
                            break

                        # Se tem carros na ponte, guarda o caminhão para a próxima vez
                        caminhao_aux = v
                        print('tem carros')

                        break
                    veiculos.append(v)

            if len(veiculos) > 1:
                print("\nSequencia de {} carros vão atravessar para {}\n".format(
                    len(veiculos), destino))
            elif len(veiculos) == 1 and veiculos[-1].tipo == 'caminhao':
                print('\nUm caminhão vai atravessar para {}'.format(destino))
            elif len(veiculos) == 1 and veiculos[-1].tipo == 'carro':
                print('\nUm carro vai atravessar para {}'.format(destino))

            else:
                ponte_sync.notify_all()
                ponte.ocupada = False
                veiculos = []
                threads = []

                continue

            semaforo = Semaphore()
            for veiculo in veiculos:
                threads.append(Thread(target=atravessar_aux, kwargs={
                    'ponte': ponte,
                    'veiculo': veiculo,
                    'destino': destino,
                    'semaforo': semaforo,
                }))
                threads[-1].start()
                sleep(INTERVALO_CARROS)

            for t in threads:
                t.join()

            threads = []
            veiculos = []

            ponte_sync.notify_all()
            ponte.ocupada = False
    

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
    travessia_para_esquerda = Thread(target=atravessa, kwargs={'fila': qr,
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
    start = time()
    main()
    print("--- %s seconds ---" % (time() - start))
