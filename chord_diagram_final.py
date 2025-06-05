import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pycirclize import Circos

# Carregar os dados
data = pd.read_csv("wfg4_dwu-dec.csv", header=None)
#data = pd.read_csv("plano_4D.csv", header=None)
min_value, max_value = data.min().min(), data.max().max()
num_points, num_dims = data.shape

# Criar setores otimizados
sectors = {str(i+1): max_value for i in range(num_dims)}

# Criar a instância do Circos
circos = Circos(sectors=sectors, space=5)

# Adicionar trilhas e personalizar
for sector in circos.sectors:
    track = sector.add_track((95, 100))
    track.xticks_by_interval(1)

# Criar conexões entre os pontos
for k in range(num_points):  
#for k in range(1):  
    for i in range(num_dims):  
        #aux = (i + 1) % num_dims if (i + 1) % num_dims != 0 else num_dims -1
        aux = (i + 1) % num_dims #if (i + 1) % num_dims != 0 else num_dims - 1
        #circos.link_line((str(i+1), data.iloc[k, i]), (str(aux+1), data.iloc[k, aux]))
        circos.link_line((str(i+1), data.iloc[k, i]), (str(aux+1), data.iloc[k, aux]), lw=.3, color='blue')

# Gerar e mostrar o gráfico
fig = circos.plotfig()
plt.show()
