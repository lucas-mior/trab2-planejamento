from gurobipy import GRB, Model
import pandas as pd
import pprint
# import numpy as np
# import gurobipy as gp
pp = pprint.PrettyPrinter(indent=4)
print("\n## Questão 1: Sorteio com 20 trios de demanda e afluência ##")
# Para demanada de 25MW e desvio padrão de 2MW:
media = 25  # mu, demanda
desvio_padrao = 2  # sigma, variação na demanda

# L1 = [0] * 20
L1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
print(f"Demanda barra 1 L1: {L1}")

# L2 = list(np.random.normal(media, desvio_padrao, 20))
# L2 = [round(item) for item in L2]
L2 = [24, 24, 25, 22, 22, 25, 24, 29, 25, 25,
      26, 25, 26, 30, 23, 24, 25, 25, 27, 25]
print(f"Demanda barra 2 L2: {L2}")

# L3 = list(np.random.normal(media, desvio_padrao, 20))
# L3 = [round(item) for item in L3]
L3 = [28, 27, 23, 25, 25, 27, 23, 27, 24, 28,
      22, 25, 22, 24, 24, 24, 27, 21, 26, 26]
print(f"Demanda barra 3 L3: {L3}")

# Y = list(np.random.uniform(0, 100, 20))
# Y = [round(item) for item in Y]
Y = [77, 28, 17, 41, 97, 18, 13, 21, 95, 0,
     62, 4, 30, 58, 23, 87, 67, 60, 47, 69]
print(f"Afluência Y: {Y}")


print("\n## Questão 2: Para cada trio sorteado, obter o despacho ótimo")


def roda_caso(L1, L2, L3, Y):
    m = Model('Custo')
    inf = GRB.INFINITY
    gt1 = m.addVar(lb=0,   ub=30,     name='gt1')
    gt2 = m.addVar(lb=0,   ub=20,     name='gt2')
    gt3 = m.addVar(lb=0,   ub=100,    name='gt3')
    alfa = m.addVar(lb=0,  ub=inf,    name='alfa')
    v = m.addVar(lb=0,     ub=100,    name='volume final')
    y = m.addVar(lb=0,     ub=300,    name='afluencia')
    s = m.addVar(lb=0,     ub=1*10e8, name='vertimento')
    q = m.addVar(lb=0,     ub=100,    name='q')
    gh = m.addVar(lb=0,    ub=100,    name='gh')
    f13 = m.addVar(lb=-15, ub=15,     name='F13 (f1)')
    f12 = m.addVar(lb=-15, ub=15,     name='F12 (f2)')
    f32 = m.addVar(lb=-10, ub=10,     name='F32 (f3)')

    m.addConstr(y == Y, 'afluência')
    m.addConstr(v + q + s == y, 'balanço de volume')
    m.addConstr(gh == 0.9*q + 0.1*v, 'balanço de volume')
    m.addConstr(gh - f12 - f13 == L1, 'barra 1')
    m.addConstr(gt1 + gt2 + f12 + f32 == L2, 'barra 2')
    m.addConstr(gt3 + f13 - f32 == L3, 'barra 3')
    m.addConstr(alfa + 6*v >= 287.5, 'corte 1')
    m.addConstr(alfa + 4*v >= 237.5, 'corte 2')
    m.addConstr(alfa + 1.5*v >= 112.5, 'corte 3')
    m.addConstr(alfa >= 0, 'corte 4')

    m.setObjective(gt1 + 2*gt2 + 5*gt3 + alfa, GRB.MINIMIZE)
    m.params.timelimit = 120
    m.params.MIPGap = 0.000001
    m.optimize()
    if m.status == GRB.Status.OPTIMAL:
        mvars = m.getVars()
        names = m.getAttr('VarName', mvars)
        values = m.getAttr('X', mvars)
        result = dict(zip(names, values))
        result['custo'] = m.objval
    else:
        print('Inviável!!!')
        # exit()

    return result


def CMO(custo_base, D1, D2, D3, Y):
    D1_incr = roda_caso(D1+1, D2, D3, Y)
    D2_incr = roda_caso(D1, D2+1, D3, Y)
    D3_incr = roda_caso(D1, D2, D3+1, Y)

    CMO_1 = round(D1_incr['custo'] - custo_base, 2)
    CMO_2 = round(D2_incr['custo'] - custo_base, 2)
    CMO_3 = round(D3_incr['custo'] - custo_base, 2)

    return CMO_1, CMO_2, CMO_3


print("\nDespacho ótimo: ")
opt = []
for trio in range(20):
    r = roda_caso(L1[trio], L2[trio], L3[trio], Y[trio])
    print(f"Período {trio}:")
    pp.pprint(r)
    opt.append(r)

for trio in range(20):
    linha = CMO(opt[trio]['custo'], L1[trio], L2[trio], L3[trio], Y[trio])
    opt[trio]['cmo1'] = linha[0]
    opt[trio]['cmo2'] = linha[1]
    opt[trio]['cmo3'] = linha[2]
    # print(f"CMO {trio}: {linha}")

print("\n## Questão 3: Contabilização sem existência de contratação ##")
for trio in range(20):
    b1 = opt[trio]['cmo1'] * opt[trio]['gh']
    b2 = opt[trio]['cmo2'] * opt[trio]['gt3']
    b3 = opt[trio]['cmo3'] * (opt[trio]['gt1'] + opt[trio]['gt2'])
    opt[trio]['custo_receita'] = round(b1 + b2 + b3, 2)
    CMO = max(opt[trio]['cmo1'], opt[trio]['cmo2'], opt[trio]['cmo3'])
    L = L1[trio] + L2[trio] + L3[trio]
    opt[trio]['custo_mercado'] = round(CMO*L, 2)
    opt[trio]['EM'] = opt[trio]['custo_mercado'] - opt[trio]['custo']
    opt[trio]['EMT'] = opt[trio]['custo_mercado'] - opt[trio]['custo_receita']

df = pd.DataFrame.from_records(opt)
print(df)
df['L1'] = L1
df['L2'] = L2
df['L3'] = L3

# pp.pprint(opt)

print("\n## Questão 4: ##")
# sem contratos
contr = pd.DataFrame(columns=['gt1', 'gt2', 'gt3', 'gh', 'L2', 'L3'])
zeros = [0, 0, 0, 0, 0, 0]
contr.loc[0] = zeros

# com contratos
contr2 = pd.DataFrame(columns=['gt1', 'gt2', 'gt3', 'gh', 'L2', 'L3'])
contr2.loc[0] = [20, 10, 5, 15, 25, 25]


def contabilizacao(opt, contrato):
    # geradores
    df_mcp = pd.DataFrame()
    df_mcp['MCP_gt1'] = (opt.gt1 - contrato.gt1.loc[0]) * opt.cmo2.values
    df_mcp['MCP_gt2'] = (opt.gt2 - contrato.gt2.loc[0]) * opt.cmo2.values
    df_mcp['MCP_gt3'] = (opt.gt3 - contrato.gt3.loc[0]) * opt.cmo3.values
    df_mcp['MCP_gh'] = (opt.q - contrato.gt1.loc[0]) * opt.cmo1.values
    # consumidores
    df_mcp['MCP_B2'] = (opt.L2 - contrato.L2.loc[0]) * opt.cmo2.values
    df_mcp['MCP_B3'] = (opt.L3 - contrato.L3.loc[0]) * opt.cmo3.values
    a = df_mcp[['MCP_gt1', 'MCP_gt2', 'MCP_gt3', 'MCP_gh']].sum(axis=1)
    b = -df_mcp[['MCP_B2', 'MCP_B3']].sum(axis=1).values
    df_mcp['EMT'] = a + b
    # "MCP ---> Mercado de Curto Prazo"
    return df_mcp


s_contrato = contabilizacao(df, contr)
c_contrato = contabilizacao(df, contr2)
print("\n## Questão 5: ##")
print("\n## Questão 6: ##")
