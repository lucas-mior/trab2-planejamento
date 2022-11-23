import numpy as np
from gurobipy import GRB, Model
# import gurobipy as gp

# Para demanada de 25MW e desvio padrão de 2MW:
media = 25  # mu, demanda
desvio_padrao = 2  # sigma, variação na demanda

demanda_barra_1 = [0] * 20
print(demanda_barra_1)

demanda_barra_2 = list(np.random.normal(int(media), int(desvio_padrao), 20))
demanda_barra_2 = [round(item) for item in demanda_barra_2]
print(demanda_barra_2)

demanda_barra_3 = list(np.random.normal(int(media), int(desvio_padrao), 20))
demanda_barra_3 = [round(item) for item in demanda_barra_3]
print(demanda_barra_3)

volume_afluente = list(np.random.uniform(0, 100, 20))
volume_afluente = [round(item) for item in volume_afluente]
print(volume_afluente)


def roda_caso(demanda_barra_1, demanda_barra_2, demanda_barra_3, volume_afluente):
    m = Model('Custo')
    gt1 = m.addVar(lb=0, ub=30, name='potencia termica 1')
    gt2 = m.addVar(lb=0, ub=20, name='potencia termica 2')
    gt3 = m.addVar(lb=0, ub=100, name='potencia termica 3')
    alfa = m.addVar(lb=0, ub=GRB.INFINITY, name='alfa')
    v = m.addVar(lb=0, ub=100, name='volume final')
    y = m.addVar(lb=0, ub=100, name='afluencia')
    s = m.addVar(lb=0, ub=1*10e8, name='vertimento')
    q = m.addVar(lb=0, ub=100, name='vazão turbinada')
    f12 = m.addVar(lb=15, ub=15, name='Fluxo LT 1-2')
    f31 = m.addVar(lb=-15, ub=15, name='Fluxo LT 3-1')
    f23 = m.addVar(lb=-10, ub=10, name='Fluxo LT 2-3')

    m.addConstr(y == volume_afluente, 'afluência')
    m.addConstr(v + q + s - y == 0, 'balanço de volume')
    m.addConstr(q - f12 - f31 == demanda_barra_1, 'barra 1')
    m.addConstr(gt1 + gt2 + f12 + f23 == demanda_barra_2, 'barra 2')
    m.addConstr(gt3 + f31 - f23 == demanda_barra_3, 'barra 3')
    m.addConstr(alfa + 6*v >= 287.5, 'corte 1')
    m.addConstr(alfa + 4*v >= 237.5, 'corte 2')
    m.addConstr(alfa + 1.5*v >= 112.5, 'corte 3')
    m.addConstr(alfa >= 0, 'corte 4')

    m.setObjective(gt1 + 2*gt2 + 5*gt3 + alfa, GRB.MINIMIZE)
    m.params.timelimit = 120
    m.params.MIPGap = 0.000001
    m.optimize()
    if m.status == GRB.Status.OPTIMAL:
        fobj = m.objval
        GT1 = m.getAttr('x', m.getVars())
        linha = GT1
        linha.append(fobj)
    else:
        print('Inviável!!!')
    print(f'gt1 {gt1}')
    print(f'gt2 {gt2}')
    print(f'gt3 {gt3}')
    print(f'alfa {alfa}')
    print(f'v {v}')
    print(f'y {y}')
    print(f's {s}')
    print(f'q {q}')
    print(f'f12 {f12}')
    print(f'f31 {f31}')
    print(f'f23 {f23}')
    print(f'linha {linha}')
    print('FALTA CALCULAR: _f, cmo_1, cmo_2, cmo_3, receita_gerada, custo_mercado, EM, EMT')

    return linha, fobj


roda_caso(demanda_barra_1[0], demanda_barra_2[0], demanda_barra_3[0], volume_afluente[0])
