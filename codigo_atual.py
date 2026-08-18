import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pycirclize import Circos

# --- Utils ---
def pretty_breaks(vmin: float, vmax: float, n: int = 5):
    """Gera ~n marcadores esteticamente agradáveis dentro do intervalo [vmin, vmax]."""
    if not np.isfinite(vmin) or not np.isfinite(vmax):
        return np.linspace(0.0, 1.0, n)
    if vmin == vmax:
        if vmin == 0:
            vmin, vmax = -1, 1
        else:
            vmin *= 0.9
            vmax *= 1.1
    if vmin > vmax:
        vmin, vmax = vmax, vmin
    raw = (vmax - vmin) / max(n - 1, 1)
    if raw == 0:
        raw = abs(vmax) if vmax != 0 else 1.0
    mag = 10 ** np.floor(np.log10(raw))
    nice_steps = np.array([1, 2, 2.5, 5, 10]) * mag
    step = nice_steps[np.searchsorted(nice_steps, raw, side="left")]
    if step < raw:
        step *= 10
    start = np.ceil(vmin / step) * step
    end = np.floor(vmax / step) * step
    ticks = np.arange(start, end + step, step)
    # Filtra os ticks para garantir que estejam dentro de [vmin, vmax]
    ticks = ticks[(ticks >= vmin) & (ticks <= vmax)]
    # Se não houver ticks suficientes, usa linspace como fallback
    if len(ticks) < n:
        ticks = np.linspace(vmin, vmax, n)
    return ticks

# --- Carregar e processar dados ---
data = pd.read_csv("wfg4_dwu-dec.csv", header=None)
#data = pd.read_csv("plano_4D.csv", header=None)
points = data.values
num_points, num_dims = points.shape
min_value, max_value = data.min().min(), data.max().max()

# --- Parte 1: Lógica do Diagrama de Pontos ---
result_matrix = np.zeros((num_points, num_dims + 1))
for i in range(num_points):
    point = points[i]
    norm = np.linalg.norm(point)
    result_matrix[i, 0] = norm
    if norm != 0:
        result_matrix[i, 1:] = np.arccos(point / norm)
    else:
        result_matrix[i, 1:] = np.nan

angles = result_matrix[:, 1:]
min_angle_indices = np.nanargmin(angles, axis=1)
min_angles = angles[np.arange(num_points), min_angle_indices]
norms = result_matrix[:, 0]
classification = np.column_stack((min_angle_indices, min_angles, norms))

# --- Configuração do Circos ---
max_angle = np.arccos(1 / np.sqrt(num_dims))
sector_names = [f"{i+1}" for i in range(num_dims)]
sectors = {name: max_value for name in sector_names}
spaces = [5] * (num_dims - 1) + [15]
circos = Circos(sectors=sectors, space=spaces)

# --- Parte 2: Plotagem do Diagrama de Pontos (exterior) ---
min_angle_val = np.nanmin(min_angles)
max_angle_val = np.nanmax(min_angles)
min_norm_val = np.nanmin(norms)
max_norm_val = np.nanmax(norms)

for i, sector in enumerate(circos.sectors):
    sector.text(sector.name, r=110, size=12)
    scatter_track = sector.add_track((70, 100), r_pad_ratio=0.1)
    scatter_track.axis()
    
    # Ticks horizontais para o diagrama de pontos (baseado em max_angle)
    horizontal_tick_interval = max_angle / 5
    tick_values = np.arange(0, max_angle + horizontal_tick_interval / 2, horizontal_tick_interval)
    tick_positions = (tick_values / max_angle) * max_value
    scatter_track.xticks(
        tick_positions,
        [f"{v:.2f}" for v in tick_values],  # Mantém 2 casas decimais para o scatter
        label_size=6,
        line_kws=dict(color="black")
    )

    # Ticks verticais somente no setor 1
    if sector.name == '1':
        y_ticks = pretty_breaks(float(min_norm_val), float(max_norm_val), n=5)
        scatter_track.yticks(
            y=y_ticks,
            labels=[f"{v:.1f}" for v in y_ticks],
            vmin=float(min_norm_val),
            vmax=float(max_norm_val),
            label_size=6,
            line_kws=dict(color="black"),
            side="left"
        )

    idx = np.where(classification[:, 0] == i)[0]
    if len(idx) > 0:
        x = classification[idx, 1]
        y = classification[idx, 2]
        x_scaled = (x / max_angle) * max_value
        x_scaled = np.clip(x_scaled, 0, max_value - 1e-9)
        track_height = 100 - 1
        y_scaled = ((y - min_norm_val) / (max_norm_val - min_norm_val)) * track_height
        jitter_strength = 0.02 * max_angle
        x_jitter = np.random.uniform(-jitter_strength, jitter_strength, size=len(x_scaled))
        y_jitter = np.random.uniform(-1.0, 1.0, size=len(y_scaled))
        x_scaled = np.clip(x_scaled + (x_jitter / max_angle) * max_value, 0, max_value - 1e-9)
        y_scaled = np.clip(y_scaled + y_jitter, 0, track_height)
        scatter_track.scatter(x_scaled, y_scaled, s=8, color="blue", marker="o", alpha=0.5)

# --- Parte 3: Lógica do Diagrama de Cordas (interior) ---
for sector in circos.sectors:
    chord_track = sector.add_track((40, 55))  # Reduzido para aumentar o espaço
    # Ticks horizontais para o diagrama de cordas usando pretty_breaks
    chord_tick_positions = pretty_breaks(min(0, min_value), max_value, n=6)
    chord_track.xticks(
        chord_tick_positions,
        [f"{v:.1f}" if v % 1 != 0 else f"{int(v)}" for v in chord_tick_positions],  # Inteiros quando possível, senão 1 casa decimal
        label_size=6,
        line_kws=dict(color="black")
    )

# Criar as conexões (cordas) entre todas as combinações de dimensões para cada ponto
for k in range(num_points):
    for j in range(num_dims - 1):
        for m in range(j + 1, num_dims):
            circos.link_line(
                (str(j + 1), data.iloc[k, j]),
                (str(m + 1), data.iloc[k, m]),
                r1=55,  # Ajustado para a borda externa da trilha
                r2=55,  # Ajustado para a borda externa da trilha
                lw=0.3,
                color='red'
            )

# --- Finalização ---
fig = circos.plotfig()
plt.savefig("combined_plot_integer_ticks_with_zero_scaled.png", dpi=200, bbox_inches="tight")
