import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pycirclize import Circos

# ===============================
# 1) Processamento dos pontos
# ===============================
data = pd.read_csv("wfg4_dwu-dec.csv", header=None)
points = data.values  # Cada linha é um ponto; as colunas representam as dimensões

num_points, num_dims = points.shape

result_matrix = np.zeros((num_points, num_dims + 1))

for i in range(num_points):
    point = points[i]
    norm = np.linalg.norm(point)
    result_matrix[i, 0] = norm
    if norm != 0:
        result_matrix[i, 1:] = np.arccos(point / norm)
    else:
        result_matrix[i, 1:] = np.nan

# Exibe os dados de cada ponto (opcional)
for i in range(num_points):
    print(f"Ponto {i + 1}:")
    print("  Coordenadas:         ", np.array2string(points[i], precision=4, separator=', '))
    print(f"  Norma:               {result_matrix[i, 0]:.4f}")
    print("  Ângulos (radianos):   ", np.array2string(result_matrix[i, 1:], precision=4, separator=', '))
    print("-" * 60)

# ===============================
# 2) Classificação pelo menor ângulo
# ===============================
classification_matrix = np.zeros((num_points, 3))

for i in range(num_points):
    angles = result_matrix[i, 1:]
    norm = result_matrix[i, 0]
    if norm != 0:
        min_index = np.argmin(angles)
        min_angle = angles[min_index]
    else:
        min_index = -1
        min_angle = np.nan
    classification_matrix[i] = [min_index, min_angle, norm]

# Contagem de pontos por setor para debug
setor_counts = {}
for i in range(num_points):
    idx = int(classification_matrix[i, 0])
    if idx != -1:  # Ignora pontos nulos
        setor = f"Setor {idx + 1}"
        setor_counts[setor] = setor_counts.get(setor, 0) + 1

print("\nContagem de pontos por setor:")
for setor, count in setor_counts.items():
    print(f"{setor}: {count} pontos")

# Exibe a matriz de classificação detalhada (opcional)
print("\nMatriz de Classificação Detalhada:")
for i in range(num_points):
    print(f"Ponto {i + 1}:")
    idx_menor = classification_matrix[i, 0]
    if idx_menor == -1:
        print("  Ponto nulo (norma = 0.0000)")
    else:
        print(f"  Índice do menor ângulo: {int(idx_menor)}")
        print(f"  Menor ângulo (rad): {classification_matrix[i, 1]:.4f}")
        print(f"  Norma: {classification_matrix[i, 2]:.4f}")
    print("-" * 60)

# ===============================
# 3) Criação do gráfico Circos
# ===============================
# a) Define os setores dinamicamente, começando de "Setor 1"
setores_dict = {f"Setor {i+1}": 1 for i in range(num_dims)}

# b) Inicializa o Circos para cobrir de 0 a 360 graus
circos = Circos(setores_dict, space=2, start=0, end=360)

# c) Determinar valores máximos para normalização
max_norm = np.nanmax(result_matrix[:, 0]) or 1  # Maior norma
max_coord = np.nanmax(points) or 1  # Maior coordenada dos dados
max_angle = np.pi  # Máximo ângulo possível (180 graus em radianos)

# d) Configura os setores e adiciona duas trilhas
tracks_dict = {}
for setor in circos.sectors:
    setor.axis(fc="none", ls="dashdot", lw=2, ec="black", alpha=0.5)
    setor.text(f"{setor.name}", size=12)
    
    # Trilha 1: Dispersão (ângulo x norma), raio 0 a 50
    scatter_track = setor.add_track((0, 50))
    scatter_track.axis(fc="none", ls="solid", lw=1, ec="grey", alpha=0.3)
    
    # Trilha 2: Coordenadas Paralelas (coordenadas originais como pontos), raio 50 a 100
    parallel_track = setor.add_track((50, 100))
    parallel_track.axis(fc="none", ls="solid", lw=1, ec="grey", alpha=0.3)
    
    # Armazena as trilhas no dicionário
    tracks_dict[setor.name] = {'scatter': scatter_track, 'parallel': parallel_track}

# e) Cria uma lista com os nomes dos setores em ordem
nomes_setores = [f"Setor {i+1}" for i in range(num_dims)]

# f) Posiciona os pontos nas trilhas
valid_mask = classification_matrix[:, 0] >= 0  # Filtra pontos válidos (norma != 0)
valid_indices = np.where(valid_mask)[0]  # Índices dos pontos válidos

for idx in valid_indices:
    ponto = classification_matrix[idx]
    setor_index = int(ponto[0])  # Índice do setor (0 a num_dims-1)
    setor_name = nomes_setores[setor_index]  # Ajusta para "Setor 1" a "Setor num_dims"
    
    # Acessa as trilhas do setor
    scatter_track = tracks_dict[setor_name]['scatter']
    parallel_track = tracks_dict[setor_name]['parallel']
    
    # Dados para a trilha de dispersão
    min_angle = ponto[1]  # Menor ângulo (x)
    norm = ponto[2]       # Norma (y)
    
    # Normaliza os valores para o intervalo do setor (0 a 50 para dispersão)
    x_scaled = (min_angle / max_angle) * (scatter_track.end - scatter_track.start) + scatter_track.start
    y_scaled = (norm / max_norm) * 50  # Escala para o raio 0-50
    
    # Plota na trilha de dispersão
    scatter_track.scatter([x_scaled], [y_scaled], s=50, color='blue', edgecolor='white',
                          linewidth=0.8, alpha=0.7, zorder=10)
    
    # Dados para a trilha de coordenadas paralelas (como pontos)
    coords = points[idx]  # Coordenadas originais do ponto
    x_vals = np.linspace(parallel_track.start, parallel_track.end, num_dims)  # Divide o setor em num_dims partes
    y_vals = (coords / max_coord) * 50  # Normaliza para o raio 50-100 (escala 0-50 a partir de 50)
    
    # Plota na trilha de coordenadas paralelas como pontos
    parallel_track.scatter(x_vals, y_vals, s=50, color='red', edgecolor='white',
                           linewidth=0.8, alpha=0.7, zorder=10)

# g) Renderiza o gráfico
fig = circos.plotfig()
plt.title(f"Gráfico Circos com Trilhas de Dispersão e Coordenadas Paralelas (Setores 1 a {num_dims})")
plt.show()