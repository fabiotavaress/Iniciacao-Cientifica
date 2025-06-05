import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pycirclize import Circos
import matplotlib.cm as cm

# Carregar os dados
data = pd.read_csv("plano_4D.csv", header=None)
#data = pd.read_csv("wfg4_dwu-dec.csv", header=None)
min_value, max_value = data.min().min(), data.max().max()
num_points, num_dims = data.shape

# Criar setores
sectors = {str(i+1): max_value for i in range(num_dims)}

# Criar a instância do Circos
circos = Circos(sectors=sectors, space=5)

# Adicionar trilhas
for sector in circos.sectors:
    track = sector.add_track((95, 100))
    track.xticks_by_interval(1)

# Gerar uma paleta de cores baseada nos pontos (linhas do DataFrame)
cmap = cm.get_cmap("rainbow", num_points)  # Alterne para "viridis", "inferno" ou outra paleta se quiser outro efeito

# Criar conexões entre pontos com cores variadas
for k in range(num_points):  # Agora as cores variam conforme os pontos (linhas do DataFrame)
    color = cmap(k / num_points)  # Definir cor baseada na linha do DataFrame
    for i in range(num_dims):  
        aux = (i + 1) % num_dims  # Conectar o último setor ao primeiro
        circos.link_line((str(i+1), data.iloc[k, i]), (str(aux+1), data.iloc[k, aux]), lw=1, color=color)

# Gerar e mostrar o gráfico
fig = circos.plotfig()
plt.show()
