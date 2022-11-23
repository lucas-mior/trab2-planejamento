from gurobipy import GRB, Model
# import numpy as np
# import gurobipy as gp

# Para demanada de 25MW e desvio padrão de 2MW:
media = 25  # mu, demanda
desvio_padrao = 2  # sigma, variação na demanda

# L_b1 = [0] * 20
L_b1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
print(f"L_b1: {L_b1}")

# L_b2 = list(np.random.normal(media, desvio_padrao, 20))
# L_b2 = [round(item) for item in L_b2]
L_b2 = [24, 24, 25, 22, 22, 25, 24, 29, 25, 25,
        26, 25, 26, 30, 23, 24, 25, 25, 27, 25]
print(f"L_b2: {L_b2}")

# L_b3 = list(np.random.normal(media, desvio_padrao, 20))
# L_b3 = [round(item) for item in L_b3]
L_b3 = [28, 27, 23, 25, 25, 27, 23, 27, 24, 28,
        22, 25, 22, 24, 24, 24, 27, 21, 26, 26]
print(f"L_b3: {L_b3}")

# Y = list(np.random.uniform(0, 100, 20))
# Y = [round(item) for item in Y]
Y = [77, 28, 17, 41, 97, 18, 13, 21, 95, 0,
     62, 4, 30, 58, 23, 87, 67, 60, 47, 69]
print(f"Y: {Y}")


def roda_caso(L_b1, L_b2, L_b3, Y):
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

    m.addConstr(y == Y, 'afluência')
    m.addConstr(v + q + s - y == 0, 'balanço de volume')
    m.addConstr(q - f12 - f31 == L_b1, 'barra 1')
    m.addConstr(gt1 + gt2 + f12 + f23 == L_b2, 'barra 2')
    m.addConstr(gt3 + f31 - f23 == L_b3, 'barra 3')
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


roda_caso(L_b1[0], L_b2[0], L_b3[0], Y[0])