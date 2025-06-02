import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pycirclize import Circos

# --- Parte 1: cálculo da norma e ângulos ---

data = pd.read_csv("wfg4_dwu-dec.csv", header=None)
points = data.values

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

# --- Parte 2: construir matriz com menor ângulo e índice ---

angles = result_matrix[:, 1:]  # ângulos
min_angle_indices = np.nanargmin(angles, axis=1)
min_angles = angles[np.arange(num_points), min_angle_indices]
norms = result_matrix[:, 0]

classification = np.column_stack((min_angle_indices, min_angles, norms))

# Imprimir a matriz classification para cada ponto
print("Matriz Classification (Índice do menor ângulo, Menor ângulo, Norma):")
for i in range(num_points):
    print(f"Ponto {i+1}: Índice={int(classification[i, 0])}, Ângulo={classification[i, 1]:.4f}, Norma={classification[i, 2]:.4f}")

# --- Parte 3: plotagem no Circos ---

sector_names = [f"{i+1}" for i in range(num_dims)]
sector_angle = 360 / num_dims  # Ângulo por setor (40° para 9 dimensões)
sectors = {name: sector_angle for name in sector_names}
circos = Circos(sectors, space=5)

# Ajustar a escala com base nos valores reais
min_angle = np.nanmin(min_angles)  # 0.9428 rad
max_angle = np.nanmax(min_angles)  # 1.0583 rad
min_norm = np.nanmin(norms)  # 11.6001
max_norm = np.nanmax(norms)  # 12.9843

for i, sector in enumerate(circos.sectors):
    sector.text(sector.name, r=110, size=12)
    track = sector.add_track((70, 100), r_pad_ratio=0.1)  # Ampliar track_height para 30
    track.axis()

    # Ticks horizontais (ângulos, X-axis)
    tick_angles = np.linspace(min_angle, max_angle, 5)  # 5 ticks no intervalo dos ângulos
    tick_positions = ((tick_angles - min_angle) / (max_angle - min_angle)) * sector_angle
    tick_labels = [f"{x:.2f}" for x in tick_angles]  # Mostrar ângulos em radianos
    track.xticks(tick_positions, labels=tick_labels)

    # Ticks verticais (normas, Y-axis)
    track_height = 100 - 70  # Intervalo radial ajustado (30 unidades)
    norm_ticks = np.linspace(min_norm, max_norm, 5)  # 5 ticks no intervalo das normas
    norm_tick_positions = ((norm_ticks - min_norm) / (max_norm - min_norm)) * track_height
    norm_tick_labels = [f"{x:.2f}" for x in norm_ticks]  # Mostrar normas com 2 casas decimais
    track.yticks(norm_tick_positions, norm_tick_labels, vmin=0, vmax=track_height, side="right", line_kws=dict(color="black", lw=1), text_kws=dict(color="black", size=10))

    idx = np.where(classification[:, 0] == i)[0]
    if len(idx) > 0:
        x = classification[idx, 1]  # Menor ângulo
        y = classification[idx, 2]  # Norma

        # Escalar X para o intervalo do setor, baseado em [min_angle, max_angle]
        x_scaled = ((x - min_angle) / (max_angle - min_angle)) * sector_angle
        x_scaled = np.clip(x_scaled, 0, sector_angle - 1e-6)

        # Escalar Y para o intervalo radial, baseado em [min_norm, max_norm]
        y_scaled = ((y - min_norm) / (max_norm - min_norm)) * track_height

        # Aumentar jitter para melhor separação
        jitter_strength = 0.1 * sector_angle  # Aumentado de 0.05 para 0.1
        x_jitter = np.random.uniform(-jitter_strength, jitter_strength, size=len(x_scaled))
        y_jitter = np.random.uniform(-1.0, 1.0, size=len(y_scaled))  # Aumentado de 0.5
        x_scaled = np.clip(x_scaled + x_jitter, 0, sector_angle - 1e-6)
        y_scaled = np.clip(y_scaled + y_jitter, 0, track_height)

        # Plotar com marcadores menores e transparência
        track.scatter(x_scaled, y_scaled, s=8, color="blue", marker="o", alpha=0.5)

fig = circos.plotfig()
plt.show()
