from classes import Carro, Caminhao, Ponte
from queue import Queue
from threading import Thread, Condition, Semaphore
from random import randint
from time import sleep, time
from datetime import datetime


N_CARROS = 100
N_CAMINHOES = 6
TRAVESSIA_CARRO = 10
TRAVESSIA_CAMINHAO = 20
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
                                  TRAVESSIA_CARRO, origem, 'carro', time(), 2)
                    fila.put_nowait(carro)
                    carros_gerados += 1

                elif caminhoes_gerados < N_CAMINHOES/2:
                    caminhao = Caminhao(caminhoes_gerados+1,
                                        TRAVESSIA_CAMINHAO, origem, 'caminhao', time())
                    fila.put_nowait(caminhao)
                    caminhoes_gerados += 1

            # GERA CAMINHÃO
            else:
                if caminhoes_gerados < N_CAMINHOES/2:
                    caminhao = Caminhao(caminhoes_gerados+1,
                                        TRAVESSIA_CAMINHAO, origem, 'caminhao', time())
                    fila.put_nowait(caminhao)
                    caminhoes_gerados += 1
                elif carros_gerados < N_CARROS/2:
                    carro = Carro(carros_gerados+1,
                                  TRAVESSIA_CARRO, origem, 'carro', time(), 2)
                    fila.put_nowait(carro)
                    carros_gerados += 1

        # FIM DA ZONA CRÍTICA


def atravessar_aux(**kwargs):
    tempos_de_espera = kwargs['tempos_de_espera']
    destino = kwargs['destino']
    veiculo = kwargs['veiculo']
    ponte = kwargs['ponte']
    semaforo = kwargs['semaforo']

    seta = ' --> ' if destino == 'direita' else ' <-- '

    print('{} {} - {} INICIOU A TRAVESSIA PELA {}!'.format(seta,
                                                           veiculo.tipo.upper(), veiculo.id, veiculo.origem.upper()))
    tempos_de_espera.append(time()-veiculo.data_criacao)
    veiculo.atravessar()  # SLEEP
    with semaforo:
        ponte.atravessou(veiculo.origem, veiculo.tipo, N_CAMINHOES+N_CARROS)


def atravessa(**kwargs):
    tempo_uso_da_ponte = kwargs['tempo_uso_da_ponte']
    tempos_de_espera = kwargs['tempos_de_espera']
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
        sleep(0.1)
        with ponte_sync:
            if ponte.ocupada:
                ponte_sync.wait()

            ponte.ocupada = True

            if ponte.total_atravessou_para(destino) >= (N_CAMINHOES+N_CARROS)/2:
                print("*** TODOS ATRAVESSARAM PARA A {} ***".format(destino))
                ponte.ocupada = False
                ponte_sync.notify_all()
                return

            with condition:
                while(not fila.empty()):
                    if randint(0, 1) or randint(0, 1):
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

                            break
                        veiculos.append(v)
                    else:
                        break

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
                if ponte.total_atravessou_para(destino) == (N_CAMINHOES+N_CARROS)/2-1 and caminhao_aux:
                    veiculos.append(caminhao_aux)

                continue

            semaforo = Semaphore()
            for veiculo in veiculos:
                threads.append(Thread(target=atravessar_aux, kwargs={
                    'tempo_uso_da_ponte': tempo_uso_da_ponte,
                    'tempos_de_espera': tempos_de_espera,
                    'ponte': ponte,
                    'veiculo': veiculo,
                    'destino': destino,
                    'semaforo': semaforo,
                }))
                threads[-1].start()
                sleep(INTERVALO_CARROS)

            for t in threads:
                t.join()
            if veiculos[-1].tipo == 'caminhao':
                tempo_uso_da_ponte[0] += TRAVESSIA_CAMINHAO
            else:
                tempo_uso_da_ponte[0] += ( (len(veiculos)-1)*INTERVALO_CARROS ) + TRAVESSIA_CARRO

            threads = []
            veiculos = []

            ponte_sync.notify_all()
            ponte.ocupada = False


def main(**kwargs):
    tempos_de_espera = kwargs['tempos_de_espera']
    tempo_uso_da_ponte = kwargs['tempo_uso_da_ponte']

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
                                                              'tempo_uso_da_ponte': tempo_uso_da_ponte,
                                                              'tempos_de_espera': tempos_de_espera,
                                                              'condition': cond_na_esquerda,
                                                              'origem': 'esquerda',
                                                              'destino': 'direita',
                                                              'ponte_sync': ponte_sync,
                                                              'ponte': ponte})
    travessia_para_esquerda = Thread(target=atravessa, kwargs={'fila': qr,
                                                               'tempo_uso_da_ponte': tempo_uso_da_ponte,
                                                               'tempos_de_espera': tempos_de_espera,
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
    tempos_de_espera = []
    tempo_uso_da_ponte = [0]
    start = time()
    main(tempos_de_espera=tempos_de_espera,
         tempo_uso_da_ponte=tempo_uso_da_ponte)
    print("\n--- Tempo de execução: {} segundos ---".format((time() - start)))
    print("--- Tempo máximo de espera na fila: {} segundos ---".format(max(tempos_de_espera)))
    print("--- Tempo mínimo de espera na fila: {} segundos ---".format(min(tempos_de_espera)))
    soma = 0
    for tempo in tempos_de_espera:
        soma += tempo
    print("--- Tempo médio de espera na fila: {} segundos ---".format(soma/(N_CAMINHOES+N_CARROS)))
    print("--- Tempo de uso da ponte: {} segundos ---".format(tempo_uso_da_ponte[0]))
