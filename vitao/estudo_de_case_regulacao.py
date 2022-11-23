from gurobipy import Model, GRB
import pandas as pd
# import numpy as np

# Demanda Barra 2 - entre 23 e 27 # D2 = np.random.randint(23, 27, size=(20))
D2 = [26, 26, 24, 23, 25, 23, 24, 23, 23, 25,
      23, 23, 25, 24, 26, 25, 26, 26, 25, 26]
# Demanda Barra 3 - entre 20 e 30 # D3 = np.random.randint(20, 30, size=(20))
D3 = [20, 22, 21, 21, 24, 24, 29, 25, 26, 26,
      20, 24, 21, 28, 20, 22, 22, 26, 29, 29]
# Afluência - entre 0 e 100 # afl = np.random.randint(0, 100, size=(20))
afl = [72, 54, 77,  1, 26, 35, 81, 1,  7,  0,
       48, 85, 78, 93, 61, 78, 69, 90, 52, 16]
print(D2)
print(D3)
print(afl)


# roda a resolução do problema (gurobupy)
def roda_caso(D1, D2, D3, afl):
    m = Model("Custo")
    gt1 = m.addVar(lb=0, ub=30, name="ptermica 1")
    gt2 = m.addVar(lb=0, ub=20, name="ptermica 1")
    gt3 = m.addVar(lb=0, ub=100, name="ptermica 3")
    alfa = m.addVar(lb=0, ub=GRB.INFINITY, name="alfa")
    v = m.addVar(lb=0, ub=100, name="volume final")
    y = m.addVar(lb=0, ub=100, name="afluência")
    s = m.addVar(lb=0, ub=1*10e8, name="vertimento")
    q = m.addVar(lb=0, ub=100, name="vazão turbinada")
    f12 = m.addVar(lb=-25, ub=25, name="Fluxo lt:1-2")  # f3
    f31 = m.addVar(lb=-50, ub=50, name="Fluxo lt:3-1")  # f1
    f23 = m.addVar(lb=-35, ub=35, name="Fluxo lt:2-3")  # f2

    m.addConstr(y == afl, "afluência")
    m.addConstr(v + q + s - y == 0, "balanço de volume")
    m.addConstr(q - f12 - f31 == D1, "Barra 1")
    m.addConstr(gt1 + gt2 + f12 + f23 == D2, "Barra 2")
    m.addConstr(gt3 + f31 - f23 == D3, "Barra 3")
    m.addConstr(alfa + 5*v >= 320, "corte 1")
    m.addConstr(alfa + 2*v >= 170, "corte 2")
    m.addConstr(alfa + 1*v >= 100, "corte 3")
    m.addConstr(alfa >= 0, "corte 4")

    m.setObjective(gt1 + 2*gt2 + 5*gt3 + alfa, GRB.MINIMIZE)
    # m.write("retricoes2.1p")
    m.params.timelimit = 120
    m.params.MIPGap = 0.0000001
    m.optimize()
    if m.status == GRB.Status.OPTIMAL:
        fobj = m.objval
        GT1 = m.getAttr("x", m.getVars())
        linha = GT1
        linha.append(fobj)
    else:
        print("InviáveL!!!")
    return linha, fobj


# calcula os CMOs e cria uma linha com os dados relevantes
def CMO(D1, D2, D3, afl):
    custo_base = roda_caso(D1, D2, D3, afl)
    D1_incr = roda_caso(D1+1, D2, D3, afl)
    D2_incr = roda_caso(D1, D2+1, D3, afl)
    D3_incr = roda_caso(D1, D2, D3+1, afl)

    CMO_1 = D1_incr[1] - custo_base[1]
    CMO_2 = D2_incr[1] - custo_base[1]
    CMO_3 = D3_incr[1] - custo_base[1]
    linha = custo_base[0]
    linha = linha + [CMO_1, CMO_2, CMO_3]

    return linha, CMO_1, CMO_2, CMO_3


# #cria dataframe
header = ['gt1', 'gt2', 'gt3', 'alfa', 'v', 'y', 's', 'q',
          'f12', 'f31', 'f23', '_f_', 'cmo_1', 'cmo_2', 'cmo_3']
# df = pd.DataFrame(columns=[header])
lista = []
for trio in range(0, 20):
    caso = CMO(0, D2[trio], D3[trio], afl[trio])
    lista.append(caso[0])

df = pd.DataFrame(lista, columns=[header])
df['D2'] = D2
df['D3'] = D3
df['receita_ger'] = df['cmo_1']*df['q'].values + (df['cmo_2']*(df['gt1']+df['gt2'].values).values).values + (df['cmo_3']*(df['gt3'].values)).values
df['custo_mercado'] = df['cmo_2'].multiply(D2, axis=0) + df['cmo_3'].multiply(D3, axis=0).values # #bug encontrado ao tentar somar e multiplicar o DF, só funciona com .values no final

df['EM'] = df['custo_mercado'] - df['_f_'].values
df['EMT'] = df['custo_mercado'] - df['receita_ger'].values

# questão 4 contabilização
# sem contratos
contr = pd.DataFrame(columns=['gt1', 'gt2', 'gt3', 'gh', 'D2', 'D3'])
zeros = [0, 0, 0, 0, 0, 0]
contr.loc[0] = zeros

# com contratos
contr2 = pd.DataFrame(columns=['gt1', 'gt2', 'gt3', 'gh', 'D2', 'D3'])
contr2.loc[0] = [20, 10, 5, 15, 25, 25]


def contabilizacao(df_completo, df_contratações):
    # geradores
    df_mcp = pd.DataFrame()
    df_mcp['MCP_gt1'] = (df_completo.gt1 - df_contratações.gt1.loc[0]) * df_completo.cmo_2.values
    df_mcp['MCP_gt2'] = (df_completo.gt2 - df_contratações.gt2.loc[0]) * df_completo.cmo_2.values
    df_mcp['MCP_gt3'] = (df_completo.gt3 - df_contratações.gt3.loc[0]) * df_completo.cmo_3.values
    df_mcp['MCP_gh'] = (df_completo.q - df_contratações.gt1.loc[0]) * df_completo.cmo_1.values
    # consumidores
    df_mcp['MCP_B2'] = (df_completo.D2 - df_contratações.D2.loc[0]) *  df_completo.cmo_2.values
    df_mcp['MCP_B3'] = (df_completo.D3 - df_contratações.D3.loc[0]) *  df_completo.cmo_3.values
    df_mcp['EMT'] = df_mcp[['MCP_gt1', 'MCP_gt2', 'MCP_gt3', 'MCP_gh']].sum(axis=1) - df_mcp[['MCP_B2', 'MCP_B3']].sum(axis=1).values
    # "MCP ---> Mercado de Curto Prazo"
    return df_mcp


s_contrato = contabilizacao(df, contr)
c_contrato = contabilizacao(df, contr2)
print('end')
