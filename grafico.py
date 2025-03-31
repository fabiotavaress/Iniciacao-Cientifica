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

# Cria uma matriz para armazenar a norma e os ângulos
result_matrix = np.zeros((num_points, num_dims + 1))

for i in range(num_points):
    point = points[i]
    norm = np.linalg.norm(point)
    result_matrix[i, 0] = norm
    if norm != 0:
        result_matrix[i, 1:] = np.arccos(point / norm)
    else:
        result_matrix[i, 1:] = np.nan

# Exibe dados de cada ponto (opcional)
for i in range(num_points):
    print("Ponto {}:".format(i + 1))
    print("  Coordenadas:         ", np.array2string(points[i], precision=4, separator=', '))
    print("  Norma:               {:.4f}".format(result_matrix[i, 0]))
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

# Exibe a matriz de classificação (opcional)
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

# a) Defina 9 setores, agora numerados de 0 a 8, cada um com "tamanho" = 1 (iguais entre si).
setores_dict = {f"Setor {i}": 1 for i in range(9)}

# b) Inicialize o Circos para cobrir de 0 a 360 graus (um círculo completo).
circos = Circos(setores_dict, space=2, start=0, end=360)

# c) Para cada setor, crie um track que vá do raio 0 até 100
tracks_dict = {}
for setor in circos.sectors:
    setor.axis(fc="none", ls="dashdot", lw=2, ec="black", alpha=0.5)
    setor.text(f"{setor.name}", size=12)
    # Cria um track do raio 0 até 100
    track = setor.add_track((0, 100))
    track.axis(fc="none", ls="solid", lw=1, ec="grey", alpha=0.3)
    tracks_dict[setor.name] = track

# d) Posicionamento dos pontos no sistema do pycirclize
# Cada ponto é posicionado em seu respectivo setor
valid_mask = classification_matrix[:, 0] >= 0
valid_points = classification_matrix[valid_mask]

for ponto in valid_points:
    setor_index = int(ponto[0])  # índice do setor (0 a 8)
    setor_obj = circos.sectors[setor_index]
    track_obj = tracks_dict[setor_obj.name]
    
    # Escolhe um ângulo dentro do intervalo do setor
    angle_deg = np.random.uniform(setor_obj.start, setor_obj.end)
    # Escolhe um raio de 0 a 100
    r_abs = np.random.uniform(0, 100)
    # Escala o raio para [0,1] (pois o track espera o valor normalizado)
    r_scaled = r_abs / 100.0
    
    # Plota no track; os valores serão convertidos para o sistema polar do setor
    track_obj.scatter(
        [r_scaled],     # raio escalado para o intervalo [0,1]
        [angle_deg],    # ângulo em graus, dentro do setor
        s=50,
        color='blue',
        edgecolor='white',
        linewidth=0.8,
        alpha=0.7,
        zorder=10
    )

# e) Renderiza o Circos
fig = circos.plotfig()
plt.title("Distribuição dos pontos espalhados em setores 0 a 8 (Circos)")
plt.show()
