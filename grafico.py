import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pycirclize import Circos

# ===============================
# 1) Processamento dos pontos
# ===============================
# Lê os dados do arquivo CSV
data = pd.read_csv("wfg4_dwu-dec.csv", header=None)
points = data.values  # Cada linha é um ponto; as colunas representam as dimensões

num_points, num_dims = points.shape

# Inicializa a matriz de resultados com norma e ângulos
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

# Verifica quantos pontos têm norma zero
num_invalid_points = np.sum(classification_matrix[:, 0] == -1)
print(f"\nNúmero de pontos com norma zero (não plotados): {num_invalid_points}")

# ===============================
# 3) Criação do gráfico Circos
# ===============================
# a) Define os setores dinamicamente
setores_dict = {f"Setor {i+1}": 1 for i in range(num_dims)}

# b) Inicializa o Circos para cobrir de 0 a 360 graus
circos = Circos(setores_dict, space=2, start=0, end=360)

# c) Determinar valores máximos para normalização
max_norm = np.nanmax(result_matrix[:, 0]) or 1  # Maior norma
max_coord = np.nanmax(points) or 1  # Maior coordenada dos dados

# d) Configura os setores e adiciona duas trilhas
tracks_dict = {}
for setor in circos.sectors:
    setor.axis(fc="none", ls="dashdot", lw=2, ec="black", alpha=0.5)
    setor.text(f"{setor.name}", size=12)
    
    # Trilha 1: Coordenadas Paralelas (linhas), raio 0 a 50
    parallel_track = setor.add_track((0, 50))
    parallel_track.axis(fc="none", ls="solid", lw=1, ec="grey", alpha=0.3)
    
    # Trilha 2: Dispersão (pontos), raio 50 a 100
    scatter_track = setor.add_track((50, 100))
    scatter_track.axis(fc="none", ls="solid", lw=1, ec="grey", alpha=0.3)
    
    # Armazena as trilhas no dicionário
    tracks_dict[setor.name] = {'parallel': parallel_track, 'scatter': scatter_track}

# e) Cria uma lista com os nomes dos setores em ordem
nomes_setores = [f"Setor {i+1}" for i in range(num_dims)]

# f) Filtra pontos válidos (norma != 0)
valid_mask = classification_matrix[:, 0] >= 0
valid_indices = np.where(valid_mask)[0]

# g) Coleta os pontos por setor
points_by_setor = {setor: [] for setor in nomes_setores}
for idx in valid_indices:
    ponto = classification_matrix[idx]
    setor_index = int(ponto[0])
    setor_name = nomes_setores[setor_index]
    points_by_setor[setor_name].append(idx)

# h) Plota os pontos nas trilhas, espalhando-os adequadamente na trilha de dispersão
points_plotted = 0

for setor_name, indices in points_by_setor.items():
    if not indices:
        continue  # Pula setores sem pontos
    
    # Ordena os pontos pela norma
    norms = classification_matrix[indices, 2]
    sorted_indices = [idx for _, idx in sorted(zip(norms, indices))]
    num_points_in_setor = len(sorted_indices)
    
    # Obtém os limites do setor
    scatter_track = tracks_dict[setor_name]['scatter']
    setor_start = scatter_track.start
    setor_end = scatter_track.end
    setor_width = setor_end - setor_start
    
    # Adiciona um pequeno deslocamento para evitar que os pontos fiquem exatamente nas bordas
    padding = setor_width * 0.1  # 10% de padding em cada lado
    adjusted_start = setor_start + padding
    adjusted_end = setor_end - padding
    adjusted_width = adjusted_end - adjusted_start
    
    # Calcula posições x e y para os pontos
    for i, idx in enumerate(sorted_indices):
        ponto = classification_matrix[idx]
        norm = ponto[2]
        
        # Posição x: distribui os pontos ao longo da largura ajustada do setor
        if num_points_in_setor > 1:
            x_pos = adjusted_start + (i / (num_points_in_setor - 1)) * adjusted_width
        else:
            x_pos = adjusted_start + adjusted_width / 2  # Centraliza se for único ponto
        
        # Posição y: varia entre 50 e 100 com base na norma, com padding para evitar bordas
        y_min, y_max = 55, 95  # Adiciona padding no eixo y (5 unidades de cada lado)
        y_pos = y_min + (norm / max_norm) * (y_max - y_min)  # Normaliza para o intervalo ajustado
        
        # Plota na trilha de dispersão
        scatter_track.scatter([x_pos], [y_pos], s=20, color='blue', edgecolor='white',
                              linewidth=0.5, alpha=0.7, zorder=10)
        points_plotted += 1
        
        # Plota na trilha de coordenadas paralelas
        parallel_track = tracks_dict[setor_name]['parallel']
        coords = points[idx]
        x_vals = np.linspace(parallel_track.start, parallel_track.end, num_dims)
        y_vals = (coords / max_coord) * 50  # Normaliza para o raio 0 a 50
        parallel_track.line(x_vals, y_vals, color='red', linewidth=1.5, alpha=0.7, zorder=10)

# Debug: quantos pontos foram plotados
print(f"\nTotal de pontos plotados na trilha de dispersão: {points_plotted}")

# i) Renderiza o gráfico
fig = circos.plotfig()
plt.title(f"Gráfico Circos com Trilhas de Dispersão e Coordenadas Paralelas (Setores 1 a {num_dims})")
plt.show()
