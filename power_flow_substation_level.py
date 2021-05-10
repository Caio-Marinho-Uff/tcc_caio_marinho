# Todos os import
import sys  # Importando biblioteca para conseguir terminar o programa em linha de código
import os.path  # Importando biblioteca para conseguir extraia, do caminho de um arquivo, sua extensão
import pandas as pd  # Importando biblioteca Pandas para utilização de dataframes
import numpy as np  # Importando biblioteca numpy para utilização em contas
import time

# Importando biblioteca para conseguir o caminho do arquivo por UI e para exibir a caixa de diálogo
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# Função que lê arquivos PWF
def read_file_pwf(name):
    with open(name, "r") as data_file:

        dbar_location = 0  # Variável do local, no arquivo, do início dos dados de barra (onde está o DBAR)
        dlin_location = 0  # Variável do local, no arquivo, do início dos dados de linha (onde está o DLIN)
        dbar_out = False  # Variável que indica se a posição de DBAR já foi encontrada
        dlin_out = False  # Variável que indica se a posição de DLIN já foi encontrada

        # Percorre o arquivo até encontrar a seção de dados de barra (DBAR) e a seção de dados de linha (DLIN)
        while True:
            line_from_file = data_file.readline()

            if line_from_file[0:4] == "DBAR":
                dbar_location = data_file.tell()
                dbar_out = True

            if line_from_file[0:4] == "DLIN":
                dlin_location = data_file.tell()
                dlin_out = True

            if dbar_out and dlin_out:
                break

        # Dicionário que guardará todos os valores úteis de barras do PWF
        bus = dict({'number': [], 'type': [], 'voltage': [], 'angle': [], 'generated_MW': [], 'generated_Mvar': [],
                    'load_MW': [], 'load_Mvar': [], 'shunt': []})

        # Usar esse dicionário se eu quiser ler tudo do PWF, mas não precisa
        # bus = dict({'number': [], 'type': [], 'name': [], 'voltage': [], 'angle': [], 'generated_MW': [],
        #             'generated_Mvar': [], 'min_Mvar': [], 'max_Mvar': [], 'controlled_bus': [], 'load_MW': [],
        #             'load_Mvar': [], 'shunt': [], 'area': []})

        data_file.seek(dbar_location, 0)  # Coloca o arquivo na posição de DBAR para leitura

        while True:
            line_from_file = data_file.readline()

            # Verifica se a linha em questão é comentada ou está vazia
            while (line_from_file[0:1] == "(") or (not line_from_file):
                line_from_file = data_file.readline()

            # Verifica se chegou ao final da seção de dados de barra, se chegar vai sair do loop
            if line_from_file[0:5] == "99999":
                break

            # Preenche, no dicionário, o número da barra
            bus['number'].append(int(line_from_file[0:5]))

            # Preenche, no dicionário, o tipo da barra (0 - PQ / 1 - PV / 2 - SWING)
            # Se não tiver nada no PWF, o default será 0 - PQ
            if (line_from_file[7].isspace()) or (not line_from_file[7]) or \
                    (int(line_from_file[7]) < 0) or (int(line_from_file[7]) > 2):
                bus['type'].append(0)
            else:
                bus['type'].append(int(line_from_file[7]))

            # Preenche, no dicionário, a tensão da barra (p.u.)
            # Se não tiver nada no PWF, o default será 1.0 p.u.
            if (line_from_file[24:28].isspace()) or (not line_from_file[24:28]):
                bus['voltage'].append(1.0)
            else:
                bus['voltage'].append(float(line_from_file[24:28]) / 1000)

            # Preenche, no dicionário, o ângulo da barra (º)
            # Se não tiver nada no PWF, o default será 0.0º
            if (line_from_file[28:32].isspace()) or (not line_from_file[28:32]):
                bus['angle'].append(0.0)
            else:
                bus['angle'].append(float(line_from_file[28:32]))

            # Preenche, no dicionário, a potência ativa sendo gerada da barra (MW)
            # Se não tiver nada no PWF, o default será 0.0 MW
            if (line_from_file[32:37].isspace()) or (not line_from_file[32:37]):
                bus['generated_MW'].append(0.0)
            else:
                bus['generated_MW'].append(float(line_from_file[32:37]))

            # Preenche, no dicionário, a potência reativa sendo gerada da barra (Mvar)
            # Se não tiver nada no PWF, o default será 0.0 Mvar
            if (line_from_file[37:42].isspace()) or (not line_from_file[37:42]):
                bus['generated_Mvar'].append(0.0)
            else:
                bus['generated_Mvar'].append(float(line_from_file[37:42]))

            # Preenche, no dicionário, a carga ativa da barra (MW)
            # Se não tiver nada no PWF, o default será 0.0 MW
            if (line_from_file[58:63].isspace()) or (not line_from_file[58:63]):
                bus['load_MW'].append(0.0)
            else:
                bus['load_MW'].append(float(line_from_file[58:63]))

            # Preenche, no dicionário, a carga reativa da barra (Mvar)
            # Se não tiver nada no PWF, o default será 0.0 Mvar
            if (line_from_file[63:68].isspace()) or (not line_from_file[63:68]):
                bus['load_Mvar'].append(0.0)
            else:
                bus['load_Mvar'].append(float(line_from_file[63:68]))

            # Preenche, no dicionário, o shunt da barra (p.u.)
            # Se não tiver nada no PWF, o default será 0.0 p.u.
            if (line_from_file[69:73].isspace()) or (not line_from_file[69:73]):
                bus['shunt'].append(0.0)
            else:
                bus['shunt'].append(float(line_from_file[69:73]) / 100)

            # Usar  se eu quiser ler tudo do PWF, mas não precisa
            # bus['name'].append(line_from_file[10:22])
            # bus['min_Mvar'].append(float(line_from_file[42:47]))          # [Mvar]
            # bus['max_Mvar'].append(float(line_from_file[47:52]))          # [Mvar]
            # bus['controlled_bus'].append(int(line_from_file[52:58]))
            # bus['area'].append(int(line_from_file[73:76]))

        # Dicionário que guardará todos os valores úteis de circuitos do PWF
        circuit = dict({'bus_from': [], 'bus_to': [], 'resistance': [], 'reactance': [], 'susceptance': []})

        # Usar esse dicionário se eu quiser ler tudo do PWF, mas não precisa
        # circuit = dict({'bus_from': [], 'bus_to': [], 'circuit_number': [], 'resistance': [], 'reactance': [],
        #                 'susceptance': [], 'tap': []})

        data_file.seek(dlin_location, 0)  # Coloca o arquivo na posição de DLIN para leitura

        while True:
            line_from_file = data_file.readline()

            # Verifica se a linha em questão é comentada ou está vazia
            while (line_from_file[0:1] == "(") or (not line_from_file):
                line_from_file = data_file.readline()

            # Verifica se chegou ao final da seção de dados de barra, se chegar vai sair do loop
            if line_from_file[0:5] == "99999":
                break

            # Preenche, no dicionário, o número da barra de
            circuit['bus_from'].append(int(line_from_file[0:5]))
            # Preenche, no dicionário, o número da barra para
            circuit['bus_to'].append(int(line_from_file[10:15]))

            # Preenche, no dicionário, a resistência da linha (p.u.)
            # Se não tiver nada no PWF, o default será 0.0 p.u.
            if (line_from_file[20:26].isspace()) or (not line_from_file[20:26]):
                circuit['resistance'].append(0.0)
            else:
                circuit['resistance'].append(float(line_from_file[20:26]) / 100)

            # Preenche, no dicionário, a reatância da linha (p.u.)
            # Se não tiver nada no PWF, o default será 0.001 p.u.
            if (line_from_file[26:32].isspace()) or (not line_from_file[26:32]):
                circuit['reactance'].append(0.001)
            else:
                circuit['reactance'].append(float(line_from_file[26:32]) / 100)

            # Preenche, no dicionário, a susceptância da linha (p.u.)
            # Se não tiver nada no PWF, o default será 0.0 p.u.
            if (line_from_file[32:38].isspace()) or (not line_from_file[32:38]):
                circuit['susceptance'].append(0.0)
            else:
                circuit['susceptance'].append(float(line_from_file[32:38]) / 100)

            # Usar  se eu quiser ler tudo do PWF, mas não precisa
            # circuit['circuit_number'].append(line_from_file[15:17])
            # circuit['tap'].append(float(line_from_file[38:43]))

        bus_df = pd.DataFrame(bus)  # Cria um dataframe a partir do dicionário de barras
        circuit_df = pd.DataFrame(circuit)  # Cria um dataframe a partir do dicionário de circuitos

        # Busca na dataframe quantas barras de cada tipo existem
        number_of_each_bus_type = bus_df.pivot_table(index=['type'], aggfunc='size')

        # Verifica se há alguma barra PQ no arquivo (tipo 0)
        if not (number_of_each_bus_type.index == 0).any():
            number_of_each_bus_type[0] = 0
        # Verifica se há alguma barra PV no arquivo (tipo 1)
        if not (number_of_each_bus_type.index == 1).any():
            number_of_each_bus_type[1] = 0
        # Verifica se há pelo menos uma barra de referência no arquivo (tipo 2)
        if not (number_of_each_bus_type.index == 2).any():
            bus_df['type'][0] = 2
            number_of_each_bus_type[2] = 1

        case_dict = dict({'number_buses': bus_df['number'].count(),
                          'number_circuits': circuit_df['bus_from'].count(),
                          'number_of_PQ_buses': number_of_each_bus_type[0],
                          'PQ_buses_numbers': list(bus_df[bus_df['type'].values == 0]['number']),
                          'number_of_PV_buses': number_of_each_bus_type[1],
                          'PV_buses_numbers': list(bus_df[bus_df['type'].values == 1]['number']),
                          'number_of_VT_buses': number_of_each_bus_type[2],
                          'VT_buses_numbers': list(bus_df[bus_df['type'].values == 2]['number'])})

        return bus_df, circuit_df, case_dict


# Função que monta a martriz de admitâcias
def admittance_matrix(buses, circuits, case):
    y_bus = np.zeros((case['number_buses'], case['number_buses']), dtype=np.complex)
    open_breakers_quantity = closed_breakers_quantity = 0
    breakers_state = []
    breaker_k = []
    breaker_m = []

    for index, circuit in circuits.iterrows():
        r = circuit['resistance']
        x = circuit['reactance']
        b = circuit['susceptance']

        local_bus_from = buses.index[buses['number'].values == circuit['bus_from']].tolist()[0]
        local_bus_to = buses.index[buses['number'].values == circuit['bus_to']].tolist()[0]

        if (x != 0.00001) and (x != 99.99):
            ykk = complex(r / ((r ** 2) + (x ** 2)), (-x / ((r ** 2) + (x ** 2))) + (b / 2))
            ykm = complex(r / ((r ** 2) + (x ** 2)), -x / ((r ** 2) + (x ** 2)))

            y_bus[local_bus_from, local_bus_from] += ykk
            y_bus[local_bus_to, local_bus_to] += ykk
            y_bus[local_bus_from, local_bus_to] -= ykm
            y_bus[local_bus_to, local_bus_from] = y_bus[local_bus_from, local_bus_to]
        else:
            breaker_k.append(local_bus_from)
            breaker_m.append(local_bus_to)

        if x == 0.00001:
            closed_breakers_quantity += 1
            breakers_state.append(1)
        elif x == 99.99:
            open_breakers_quantity += 1
            breakers_state.append(0)

    case['breakers'] = pd.DataFrame({'bus_from_index': breaker_k, 'bus_to_index': breaker_m, 'state': breakers_state})
    case['open_breakers'] = case['breakers'].drop(case['breakers'].index[case['breakers']['state'] == 1].tolist())
    case['open_breakers'].index = range(len(case['open_breakers']))
    case['closed_breakers'] = case['breakers'].drop(case['breakers'].index[case['breakers']['state'] == 0].tolist())
    case['closed_breakers'].index = range(len(case['closed_breakers']))
    case['number_of_breakers'] = closed_breakers_quantity + open_breakers_quantity
    case['number_of_open_breakers'] = open_breakers_quantity
    case['number_of_closed_breakers'] = closed_breakers_quantity

    for index, bus in buses.iterrows():
        y_bus[index, index] += complex(0.0, bus['shunt'])

    return y_bus, case


# Função que monta a função a ser resolvida pelo flsove(), no formato de F(x) = 0
def mismatch(x, y_bus, buses, case):
    buses_quantity = case['number_buses']
    npq = case['number_of_PQ_buses']
    npv = case['number_of_PV_buses']
    nbk = case['number_of_breakers']
    nob = case['number_of_open_breakers']
    ncb = case['number_of_closed_breakers']

    buses_pq_pv = buses[['number', 'type']].copy()
    buses_pq_pv = buses_pq_pv.drop(buses_pq_pv.index[buses_pq_pv['type'] == 2].tolist())
    buses_pq_pv.index = range(len(buses_pq_pv))

    delta = np.zeros(npq + npv + npq + (2 * nbk))

    for i in range(buses_quantity):
        angle_position_i = 0
        angle_position_j = 0

        if buses['type'][i] != 2:
            angle_position_i = buses_pq_pv.index[buses_pq_pv['number'].values == buses['number'][i]].tolist()[0]

        for j in range(buses_quantity):
            breaker_general_index = -1
            open_breaker_index = -1
            closed_breaker_index = -1

            if buses['type'][j] != 2:
                angle_position_j = buses_pq_pv.index[buses_pq_pv['number'].values == buses['number'][j]].tolist()[0]

            if (case['breakers']['bus_from_index'].values == i).any() and \
                    (case['breakers']['bus_to_index'].values == j).any():
                counter_open = -1
                counter_closed = -1

                for index, breakers in case['breakers'].iterrows():
                    if breakers['state'] == 0:
                        counter_open += 1
                    else:
                        counter_closed += 1

                    if (breakers['bus_from_index'] == i) and (breakers['bus_to_index'] == j):
                        breaker_general_index = index
                        if breakers['state'] == 0:
                            open_breaker_index = counter_open
                            closed_breaker_index = -1
                        else:
                            closed_breaker_index = counter_closed
                            open_breaker_index = -1
                        break

            if breaker_general_index >= 0:
                if closed_breaker_index >= 0:
                    if buses['type'][j] == 2:

                        if buses['type'][i] == 0:
                            n = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][i])

                            delta[npq + npv + npq + closed_breaker_index] = x[angle_position_i] - \
                                                                            np.radians(buses['angle'][j])
                            delta[npq + npv + npq + ncb + closed_breaker_index] = x[n] - buses['voltage'][j]
                        elif buses['type'][i] == 1:
                            delta[npq + npv + npq + closed_breaker_index] = x[angle_position_i] - \
                                                                            np.radians(buses['angle'][j])
                            delta[npq + npv + npq + ncb + closed_breaker_index] = buses['voltage'][i] - \
                                                                                  buses['voltage'][j]
                        else:
                            delta[npq + npv + npq + closed_breaker_index] = np.radians(buses['angle'][i])\
                                                                            - np.radians(buses['angle'][j])
                            delta[npq + npv + npq + ncb + closed_breaker_index] = buses['voltage'][i] - \
                                                                                  buses['voltage'][j]

                    elif buses['type'][j] == 1:

                        if buses['type'][i] == 0:
                            n = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][i])

                            delta[npq + npv + npq + closed_breaker_index] = x[angle_position_i] - \
                                                                            x[angle_position_j]
                            delta[npq + npv + npq + ncb + closed_breaker_index] = x[n] - buses['voltage'][j]
                        elif buses['type'][i] == 1:
                            delta[npq + npv + npq + closed_breaker_index] = x[angle_position_i] - \
                                                                            x[angle_position_j]
                            delta[npq + npv + npq + ncb + closed_breaker_index] = buses['voltage'][i] - \
                                                                                  buses['voltage'][j]
                        else:
                            delta[npq + npv + npq + closed_breaker_index] = np.radians(buses['angle'][i]) - \
                                                                            x[angle_position_j]
                            delta[npq + npv + npq + ncb + closed_breaker_index] = buses['voltage'][i] - \
                                                                                  buses['voltage'][j]

                    else:

                        nj = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][j])

                        if buses['type'][i] == 0:
                            ni = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][i])

                            delta[npq + npv + npq + closed_breaker_index] = x[angle_position_i] - \
                                                                            x[angle_position_j]
                            delta[npq + npv + npq + ncb + closed_breaker_index] = x[ni] - x[nj]
                        elif buses['type'][i] == 1:
                            delta[npq + npv + npq + closed_breaker_index] = x[angle_position_i] - \
                                                                            x[angle_position_j]
                            delta[npq + npv + npq + ncb + closed_breaker_index] = buses['voltage'][i] - x[nj]
                        else:
                            delta[npq + npv + npq + closed_breaker_index] = np.radians(buses['angle'][i]) - \
                                                                            x[angle_position_j]
                            delta[npq + npv + npq + ncb + closed_breaker_index] = buses['voltage'][i] - x[nj]

                elif open_breaker_index >= 0:
                    delta[npq + npv + npq + (2 * ncb) + open_breaker_index] = x[npq + npv + npq + breaker_general_index]
                    delta[npq + npv + npq + (2 * ncb) + nob + open_breaker_index] = \
                        x[npq + npv + npq + nbk + breaker_general_index]

    for angle_position_i in range(npq + npv):
        i = buses.index[buses['number'].values == buses_pq_pv['number'][angle_position_i]].tolist()[0]
        sum_active = sum_reactive = sum_active_breaker = sum_reactive_breaker = angle_position_j = 0

        for j in range(buses_quantity):
            breaker_general_index = -1
            contrary = 0

            if buses['type'][j] != 2:
                angle_position_j = buses_pq_pv.index[buses_pq_pv['number'].values == buses['number'][j]].tolist()[0]

            if (case['breakers']['bus_from_index'].values == i).any() and \
                    (case['breakers']['bus_to_index'].values == j).any():
                for index, breakers in case['breakers'].iterrows():
                    if (breakers['bus_from_index'] == i) and (breakers['bus_to_index'] == j):
                        breaker_general_index = index
                        contrary = 1
                        break

            if (case['breakers']['bus_from_index'].values == j).any() and \
                    (case['breakers']['bus_to_index'].values == i).any():
                for index, breakers in case['breakers'].iterrows():
                    if (breakers['bus_from_index'] == j) and (breakers['bus_to_index'] == i):
                        breaker_general_index = index
                        contrary = -1
                        break

            if breaker_general_index >= 0:
                sum_active_breaker += x[npq + npv + npq + breaker_general_index] * contrary
                if buses['type'][i] == 0:
                    sum_reactive_breaker += x[npq + npv + npq + nbk + breaker_general_index] * contrary

            if buses['type'][j] == 2:
                sum_active += (buses['voltage'][j] * ((y_bus[i, j].real * np.cos(x[angle_position_i] -
                                                                                 np.radians(buses['angle'][j]))) +
                                                      (y_bus[i, j].imag * np.sin(x[angle_position_i] -
                                                                                 np.radians(buses['angle'][j])))))

                if buses['type'][i] == 0:
                    sum_reactive += (buses['voltage'][j] * ((y_bus[i, j].real * np.sin(x[angle_position_i] -
                                                                                       np.radians(buses['angle'][j]))) -
                                                            (y_bus[i, j].imag * np.cos(x[angle_position_i] -
                                                                                       np.radians(buses['angle'][j])))))

            elif buses['type'][j] == 1:
                if i == j:
                    sum_active += (buses['voltage'][j] * y_bus[i, j].real)
                else:
                    sum_active += (buses['voltage'][j] * ((y_bus[i, j].real * np.cos(x[angle_position_i] -
                                                                                     x[angle_position_j])) +
                                                          (y_bus[i, j].imag * np.sin(x[angle_position_i] -
                                                                                     x[angle_position_j]))))

                if buses['type'][i] == 0:
                    if i == j:
                        sum_reactive -= (buses['voltage'][j] * y_bus[i, j].imag)
                    else:
                        sum_reactive += (buses['voltage'][j] * ((y_bus[i, j].real * np.sin(x[angle_position_i] -
                                                                                           x[angle_position_j])) -
                                                                (y_bus[i, j].imag * np.cos(x[angle_position_i] -
                                                                                           x[angle_position_j]))))

            else:
                n = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][j])

                if i == j:
                    sum_active += (x[n] * y_bus[i, j].real)
                else:
                    sum_active += (x[n] * ((y_bus[i, j].real * np.cos(x[angle_position_i] - x[angle_position_j])) +
                                           (y_bus[i, j].imag * np.sin(x[angle_position_i] - x[angle_position_j]))))

                if buses['type'][i] == 0:
                    if i == j:
                        sum_reactive -= (x[n] * y_bus[i, j].imag)
                    else:
                        sum_reactive += (x[n] * ((y_bus[i, j].real * np.sin(x[angle_position_i] -
                                                                            x[angle_position_j])) -
                                                 (y_bus[i, j].imag * np.cos(x[angle_position_i] -
                                                                            x[angle_position_j]))))

        if buses['type'][i] == 1:
            delta[angle_position_i] = (buses['voltage'][i] * sum_active) + sum_active_breaker
        elif buses['type'][i] == 0:
            n = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][i])

            delta[angle_position_i] = (x[n] * sum_active) + sum_active_breaker
            delta[n] = ((buses['generated_Mvar'][i] - buses['load_Mvar'][i]) / 100) - ((x[n] * sum_reactive) +
                                                                                       sum_reactive_breaker)

        delta[angle_position_i] = ((buses['generated_MW'][i] - buses['load_MW'][i]) / 100) - delta[angle_position_i]

    return delta


# Função que monta a função a ser resolvida pelo flsove(), no formato de F(x) = 0
def jacobian(x, y_bus, buses, case, previous, number_iteration):
    buses_quantity = case['number_buses']
    npq = case['number_of_PQ_buses']
    npv = case['number_of_PV_buses']
    nbk = case['number_of_breakers']
    nob = case['number_of_open_breakers']
    ncb = case['number_of_closed_breakers']

    buses_pq_pv = buses[['number', 'type']].copy()
    buses_pq_pv = buses_pq_pv.drop(buses_pq_pv.index[buses_pq_pv['type'] == 2].tolist())
    buses_pq_pv.index = range(len(buses_pq_pv))

    # if number_iteration == 0:
    #     jacobian = np.zeros((npq + npv + npq + (2 * nbk), npq + npv + npq + (2 * nbk)))
    # else:
    #     jacobian = previous

    jacobian = previous

    if number_iteration == 0:
        for i in range(buses_quantity):
            angle_position_i = 0
            angle_position_j = 0

            if buses['type'][i] != 2:
                angle_position_i = buses_pq_pv.index[buses_pq_pv['number'].values == buses['number'][i]].tolist()[0]

            for j in range(buses_quantity):
                breaker_general_index = -1
                open_breaker_index = -1
                closed_breaker_index = -1

                if buses['type'][j] != 2:
                    angle_position_j = buses_pq_pv.index[buses_pq_pv['number'].values == buses['number'][j]].tolist()[0]

                if (case['breakers']['bus_from_index'].values == i).any() and \
                        (case['breakers']['bus_to_index'].values == j).any():
                    counter_open = -1
                    counter_closed = -1

                    for index, breakers in case['breakers'].iterrows():
                        if breakers['state'] == 0:
                            counter_open += 1
                        else:
                            counter_closed += 1

                        if (breakers['bus_from_index'] == i) and (breakers['bus_to_index'] == j):
                            breaker_general_index = index
                            if breakers['state'] == 0:
                                open_breaker_index = counter_open
                                closed_breaker_index = -1
                            else:
                                closed_breaker_index = counter_closed
                                open_breaker_index = -1
                            break

                if breaker_general_index >= 0:
                    if buses['type'][i] == 0:
                        n = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][i])

                        jacobian[angle_position_i, npq + npv + npq + breaker_general_index] = 1
                        jacobian[n, npq + npv + npq + nbk + breaker_general_index] = 1
                    elif buses['type'][i] == 1:
                        jacobian[angle_position_i, npq + npv + npq + breaker_general_index] = 1

                    if buses['type'][j] == 0:
                        n = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][j])

                        jacobian[angle_position_j, npq + npv + npq + breaker_general_index] = -1
                        jacobian[n, npq + npv + npq + nbk + breaker_general_index] = -1
                    elif buses['type'][j] == 1:
                        jacobian[angle_position_j, npq + npv + npq + breaker_general_index] = -1

                    if closed_breaker_index >= 0:
                        if buses['type'][i] == 0:
                            n = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][i])

                            jacobian[npq + npv + npq + closed_breaker_index, angle_position_i] = -1
                            jacobian[npq + npv + npq + ncb + closed_breaker_index, n] = -1
                        elif buses['type'][i] == 1:
                            jacobian[npq + npv + npq + closed_breaker_index, angle_position_i] = -1

                        if buses['type'][j] == 0:
                            n = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][j])

                            jacobian[npq + npv + npq + closed_breaker_index, angle_position_j] = 1
                            jacobian[npq + npv + npq + ncb + closed_breaker_index, n] = 1
                        elif buses['type'][j] == 1:
                            jacobian[npq + npv + npq + closed_breaker_index, angle_position_j] = 1

                    elif open_breaker_index >= 0:
                        jacobian[npq + npv + npq + (2 * ncb) + open_breaker_index,
                                 npq + npv + npq + breaker_general_index] = -1
                        jacobian[npq + npv + npq + (2 * ncb) + nob + open_breaker_index,
                                 npq + npv + npq + nbk + breaker_general_index] = -1

    for angle_position_i in range(npq + npv):
        i = buses.index[buses['number'].values == buses_pq_pv['number'][angle_position_i]].tolist()[0]
        sum_h = 0
        sum_n = 0
        sum_m = 0
        sum_l = 0

        for j in range(buses_quantity):
            if buses['type'][j] != 2:
                angle_position_j = buses_pq_pv.index[buses_pq_pv['number'].values == buses['number'][j]].tolist()[0]

            if buses['type'][j] == 2:
                sum_h += (buses['voltage'][j] * ((y_bus[i, j].real * np.sin(x[angle_position_i] -
                                                                            np.radians(buses['angle'][j]))) -
                                                 (y_bus[i, j].imag * np.cos(x[angle_position_i] -
                                                                            np.radians(buses['angle'][j])))))
                sum_n += (buses['voltage'][j] * ((y_bus[i, j].real * np.cos(x[angle_position_i] -
                                                                            np.radians(buses['angle'][j]))) +
                                                 (y_bus[i, j].imag * np.sin(x[angle_position_i] -
                                                                            np.radians(buses['angle'][j])))))
                sum_m += (buses['voltage'][j] * ((y_bus[i, j].real * np.cos(x[angle_position_i] -
                                                                            np.radians(buses['angle'][j]))) +
                                                 (y_bus[i, j].imag * np.sin(x[angle_position_i] -
                                                                            np.radians(buses['angle'][j])))))
                sum_l += (buses['voltage'][j] * ((y_bus[i, j].real * np.sin(x[angle_position_i] -
                                                                            np.radians(buses['angle'][j]))) -
                                                 (y_bus[i, j].imag * np.cos(x[angle_position_i] -
                                                                            np.radians(buses['angle'][j])))))
            elif buses['type'][j] == 1:
                if i == j:
                    sum_h += (buses['voltage'][j] * y_bus[i, j].imag)
                    sum_n += (buses['voltage'][j] * y_bus[i, j].real)
                    sum_m -= (buses['voltage'][j] * y_bus[i, j].real)
                    sum_l -= (buses['voltage'][j] * y_bus[i, j].imag)

                sum_h += (buses['voltage'][j] * ((y_bus[i, j].real * np.sin(x[angle_position_i] -
                                                                            x[angle_position_j])) -
                                                 (y_bus[i, j].imag * np.cos(x[angle_position_i] -
                                                                            x[angle_position_j]))))
                sum_n += (buses['voltage'][j] * ((y_bus[i, j].real * np.cos(x[angle_position_i] -
                                                                            x[angle_position_j])) +
                                                 (y_bus[i, j].imag * np.sin(x[angle_position_i] -
                                                                            x[angle_position_j]))))
                sum_m += (buses['voltage'][j] * ((y_bus[i, j].real * np.cos(x[angle_position_i] -
                                                                            x[angle_position_j])) +
                                                 (y_bus[i, j].imag * np.sin(x[angle_position_i] -
                                                                            x[angle_position_j]))))
                sum_l += (buses['voltage'][j] * ((y_bus[i, j].real * np.sin(x[angle_position_i] -
                                                                            x[angle_position_j])) -
                                                 (y_bus[i, j].imag * np.cos(x[angle_position_i] -
                                                                            x[angle_position_j]))))
            else:
                n = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][j])

                if i == j:
                    sum_h += (x[n] * y_bus[i, j].imag)
                    sum_n += (x[n] * y_bus[i, j].real)
                    sum_m -= (x[n] * y_bus[i, j].real)
                    sum_l -= (x[n] * y_bus[i, j].imag)

                sum_h += (x[n] * ((y_bus[i, j].real * np.sin(x[angle_position_i] - x[angle_position_j])) -
                                  (y_bus[i, j].imag * np.cos(x[angle_position_i] - x[angle_position_j]))))
                sum_n += (x[n] * ((y_bus[i, j].real * np.cos(x[angle_position_i] - x[angle_position_j])) +
                                  (y_bus[i, j].imag * np.sin(x[angle_position_i] - x[angle_position_j]))))
                sum_m += (x[n] * ((y_bus[i, j].real * np.cos(x[angle_position_i] - x[angle_position_j])) +
                                  (y_bus[i, j].imag * np.sin(x[angle_position_i] - x[angle_position_j]))))
                sum_l += (x[n] * ((y_bus[i, j].real * np.sin(x[angle_position_i] - x[angle_position_j])) -
                                  (y_bus[i, j].imag * np.cos(x[angle_position_i] - x[angle_position_j]))))

            if (buses['type'][j] != 2) and (i != j):
                # H
                jacobian[angle_position_i, angle_position_j] = ((y_bus[i, j].real * np.sin(x[angle_position_i] -
                                                                                           x[angle_position_j])) -
                                                                (y_bus[i, j].imag * np.cos(x[angle_position_i] -
                                                                                           x[angle_position_j])))

                if buses['type'][i] == 0:
                    i_pq = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][i])

                    # H
                    jacobian[angle_position_i, angle_position_j] *= x[i_pq]
                    # M
                    jacobian[i_pq, angle_position_j] = - x[i_pq] * ((y_bus[i, j].real * np.cos(x[angle_position_i] -
                                                                                               x[angle_position_j])) +
                                                                    (y_bus[i, j].imag * np.sin(x[angle_position_i] -
                                                                                               x[angle_position_j])))

                    if buses['type'][j] == 0:
                        j_pq = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][j])

                        # M
                        jacobian[i_pq, angle_position_j] *= x[j_pq]
                    else:
                        # M
                        jacobian[i_pq, angle_position_j] *= buses['voltage'][j]
                else:
                    # H
                    jacobian[angle_position_i, angle_position_j] *= buses['voltage'][i]

                if buses['type'][j] == 0:
                    j_pq = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][j])

                    # H
                    jacobian[angle_position_i, angle_position_j] *= x[j_pq]
                    # N
                    jacobian[angle_position_i, j_pq] = ((y_bus[i, j].real * np.cos(x[angle_position_i] -
                                                                                   x[angle_position_j])) +
                                                        (y_bus[i, j].imag * np.sin(x[angle_position_i] -
                                                                                   x[angle_position_j])))

                    if buses['type'][i] == 0:
                        i_pq = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][i])

                        # N
                        jacobian[angle_position_i, j_pq] *= x[i_pq]
                    else:
                        # N
                        jacobian[angle_position_i, j_pq] *= buses['voltage'][i]
                else:
                    # H
                    jacobian[angle_position_i, angle_position_j] *= buses['voltage'][j]

                if (buses['type'][i] == 0) and (buses['type'][j] == 0):
                    i_pq = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][i])
                    j_pq = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][j])

                    # L
                    jacobian[i_pq, j_pq] = x[i_pq] * ((y_bus[i, j].real * np.sin(x[angle_position_i] -
                                                                                 x[angle_position_j])) -
                                                      (y_bus[i, j].imag * np.cos(x[angle_position_i] -
                                                                                 x[angle_position_j])))

        if buses['type'][i] == 0:
            i_pq = (npq + npv) + case['PQ_buses_numbers'].index(buses['number'][i])

            jacobian[angle_position_i, angle_position_i] = - x[i_pq] * sum_h
            jacobian[angle_position_i, i_pq] = sum_n
            jacobian[i_pq, angle_position_i] = x[i_pq] * sum_m
            jacobian[i_pq, i_pq] = sum_l
        else:
            jacobian[angle_position_i, angle_position_i] = - buses['voltage'][i] * sum_h

    # print(jacobian)

    return jacobian


# Função que resolve o problema de fluxo de potência, através do método Newton Raphson, pelo
def newton(y_bus, buses, case):
    npq = case['number_of_PQ_buses']
    npv = case['number_of_PV_buses']
    nbk = case['number_of_breakers']

    # Cria o vetor de chute inicial para o cálculo do flow
    # Considera Tensão = 1, Ângulo = 0, ukm e tkm = 0 para disjuntor aberto, ukm e tkm = 1 para disjuntor fechado
    initial_guess = np.zeros(npq + npv)
    initial_guess = np.append(initial_guess, np.ones(npq))
    initial_guess = np.append(initial_guess, case['breakers']['state'].tolist())
    initial_guess = np.append(initial_guess, case['breakers']['state'].tolist())

    iteration = 0
    J = np.zeros((npq + npv + npq + (2 * nbk), npq + npv + npq + (2 * nbk)))

    while True:
        D = mismatch(initial_guess, y_bus, buses, case)
        epsilon = abs(max(np.amin(D), np.amax(D), key=abs))

        if epsilon < 0.000001:
            break

        J = jacobian(initial_guess, y_bus, buses, case, J, iteration)
        D_result = np.linalg.solve(J, D)
        initial_guess += D_result

        # print("Estados")
        # print(initial_guess)
        # print("\nMismathc")
        # print(D)
        # print("\nJacobiana")
        # print(J)
        print("\nIteração")
        print(iteration)
        print("\nEpsilon")
        print(epsilon)
        print("\n")

        iteration += 1

    return initial_guess


# Função que mostra todos os resultados do Flow, independente do método
def power_flow_results(y_bus, buses, circuits, case):
    npq = case['number_of_PQ_buses']
    npv = case['number_of_PV_buses']
    nbk = case['number_of_breakers']

    # Resolve o problema básico de fluxo de potência, agora tenho todos os ângulos, tensões e fluxo em disjuntores
    results_fsolve = newton(y_bus, buses, case)

    counter_angle = 0
    counter_voltage = 0

    # Salva, no dataframe buses, os valores corretos, do fim da simulação, de ângulo e tensão
    for index_bus, bus in buses.iterrows():
        if bus['type'] != 2:
            buses['angle'][index_bus] = np.degrees(results_fsolve[counter_angle])
            counter_angle += 1

            if bus['type'] == 0:
                buses['voltage'][index_bus] = results_fsolve[npq + npv + counter_voltage]
                counter_voltage += 1
            else:
                buses['generated_Mvar'][index_bus] = buses['load_Mvar'][index_bus]
        else:
            buses['generated_MW'][index_bus] = buses['load_MW'][index_bus]
            buses['generated_Mvar'][index_bus] = buses['load_Mvar'][index_bus]

            buses[index_bus] = bus

    circuit_active_flow = np.zeros(circuits.index.size)
    circuit_reactive_flow = np.zeros(circuits.index.size)
    counter_breaker = 0
    bus_shunts = buses['shunt']

    for index_circuit, circuit in circuits.iterrows():
        i = buses.index[buses['number'].values == circuit['bus_from']].tolist()[0]
        j = buses.index[buses['number'].values == circuit['bus_to']].tolist()[0]

        voltage_i = buses['voltage'][i]
        voltage_j = buses['voltage'][j]
        angle_i = np.radians(buses['angle'][i])
        angle_j = np.radians(buses['angle'][j])

        r = circuit['resistance']
        x = circuit['reactance']
        bsh = circuit['susceptance']

        g = r / ((r ** 2) + (x ** 2))
        b = -x / ((r ** 2) + (x ** 2))

        if (x != 0.00001) and (x != 99.99):
            circuit_active_flow[index_circuit] = 100 * (((voltage_i ** 2) * g) - (voltage_i * voltage_j *
                                                                                  ((g * np.cos(angle_i - angle_j)) +
                                                                                   (b * np.sin(angle_i - angle_j)))))
            circuit_reactive_flow[index_circuit] = 100 * (- ((voltage_i ** 2) * (b + (bsh/2))) +
                                                          (voltage_i * voltage_j * ((b * np.cos(angle_i - angle_j)) -
                                                                                    (g * np.sin(angle_i - angle_j)))))
        else:
            circuit_active_flow[index_circuit] = 100 * results_fsolve[npv + npq + npq + counter_breaker]
            circuit_reactive_flow[index_circuit] = 100 * results_fsolve[npv + npq + npq + nbk + counter_breaker]

            counter_breaker += 1

        if buses['type'][i] != 0:
            buses['generated_Mvar'][i] += circuit_reactive_flow[index_circuit]

            buses['generated_Mvar'][i] -= (voltage_i ** 2) * bus_shunts[i] * 100
            bus_shunts[i] = 0

            if buses['type'][i] == 2:
                buses['generated_MW'][i] += circuit_active_flow[index_circuit]

        if buses['type'][j] != 0:
            buses['generated_Mvar'][j] -= (voltage_j ** 2) * bus_shunts[j] * 100
            bus_shunts[j] = 0

            if (x != 0.00001) and (x != 99.99):
                buses['generated_Mvar'][j] += 100 * (- ((voltage_j ** 2) * (b + (bsh/2))) +
                                                     (voltage_j * voltage_i * ((b * np.cos(angle_j - angle_i)) -
                                                                               (g * np.sin(angle_j - angle_i)))))

                if buses['type'][j] == 2:
                    buses['generated_MW'][j] += 100 * (((voltage_j ** 2) * g) -
                                                       (voltage_j * voltage_i * ((g * np.cos(angle_j - angle_i)) +
                                                                                 (b * np.sin(angle_j - angle_i)))))
            else:
                buses['generated_Mvar'][j] -= 100 * results_fsolve[npv + npq + npq + nbk + counter_breaker - 1]
                if buses['type'][j] == 2:
                    buses['generated_MW'][j] -= 100 * results_fsolve[npv + npq + npq + counter_breaker - 1]

    circuits['active_flow'] = list(circuit_active_flow)
    circuits['reactive_flow'] = list(circuit_reactive_flow)

    return buses, circuits


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    other = tk.Tk()
    other.withdraw()

    # Parte do código que pede um arquivo de entrada PWF ou CDF e os direciona para as respectivas funções de leitura
    while True:
        file_path = filedialog.askopenfilename()
        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".pwf":
            break

        read_again = messagebox.askyesno("TCC do Caio",
                                         "Arquivo selecionado não é PWF, deseja selecionar outro?")

        if not read_again:
            messagebox.showinfo("TCC do Caio", "Fim do programa")
            sys.exit()

    # Lê o arquivo de entrada
    buses, circuits, case = read_file_pwf(file_path)

    # Monta a matriz de admitâncias do sistema
    y_bus, case = admittance_matrix(buses, circuits, case)

    # Começa a contar o tempo de simulação
    t_zero = time.time()

    # Resolve o problema de fluxo de potência
    results_buses, results_circuits = power_flow_results(y_bus, buses, circuits, case)

    # Termina de contar o tempo de simulação
    t_one = time.time() - t_zero

    print(f"Demorou {t_one} segundos para rodar\n")

    # Salva os resultados da simulação em arquivos .csv
    path = os.path.splitext(file_path)[0]
    path_buses = path + "_results_buses.csv"
    path_circuits = path + "_results_circuits.csv"
    results_buses.to_csv(path_buses, index=False, sep=';')
    results_circuits.to_csv(path_circuits, index=False, sep=';')