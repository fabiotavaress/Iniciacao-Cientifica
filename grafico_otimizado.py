import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pycirclize import Circos
import logging

# --- Configuração global ---
np.random.seed(42)
logging.basicConfig(level=logging.INFO)

# --- Funções auxiliares ---
def pretty_breaks(vmin: float, vmax: float, n: int = 5) -> np.ndarray:
    if not np.isfinite(vmin) or not np.isfinite(vmax):
        return np.linspace(0.0, 1.0, n)
    if vmin == vmax:
        vmin, vmax = (vmin * 0.9, vmin * 1.1) if vmin != 0 else (-1, 1)
    if vmin > vmax:
        vmin, vmax = vmax, vmin
    raw = (vmax - vmin) / max(n - 1, 1)
    mag = 10 ** np.floor(np.log10(raw or 1.0))
    nice_steps = np.array([1, 2, 2.5, 5, 10]) * mag
    step = nice_steps[np.searchsorted(nice_steps, raw, side="left")]
    step = step if step >= raw else step * 10
    ticks = np.arange(np.ceil(vmin / step) * step, np.floor(vmax / step) * step + step, step)
    ticks = ticks[(ticks >= vmin) & (ticks <= vmax)]
    return ticks if len(ticks) >= n else np.linspace(vmin, vmax, n)

def compute_classification(points: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(points, axis=1)
    angles = np.full_like(points, np.nan)
    nonzero = norms != 0
    angles[nonzero] = np.arccos(points[nonzero] / norms[nonzero, None])
    min_idx = np.nanargmin(angles, axis=1)
    min_val = angles[np.arange(len(points)), min_idx]
    return np.column_stack((min_idx, min_val, norms))

def setup_circos(num_dims: int, max_value: float) -> Circos:
    sector_names = [str(i + 1) for i in range(num_dims)]
    sectors = {name: max_value for name in sector_names}
    spaces = [5] * (num_dims - 1) + [15]
    return Circos(sectors=sectors, space=spaces)

def plot_scatter_tracks(circos: Circos, classification: np.ndarray, max_angle: float, max_value: float, min_norm: float, max_norm: float):
    for i, sector in enumerate(circos.sectors):
        sector.text(sector.name, r=110, size=12)
        track = sector.add_track((70, 100), r_pad_ratio=0.1)
        track.axis()

        tick_vals = np.linspace(0, max_angle, 6)
        tick_pos = (tick_vals / max_angle) * max_value
        track.xticks(tick_pos, [f"{v:.2f}" for v in tick_vals], label_size=6, line_kws=dict(color="black"))

        if sector.name == '1':
            y_ticks = pretty_breaks(min_norm, max_norm, n=5)
            track.yticks(y=y_ticks, labels=[f"{v:.1f}" for v in y_ticks], vmin=min_norm, vmax=max_norm, label_size=6, line_kws=dict(color="black"), side="left")

        idx = np.where(classification[:, 0] == i)[0]
        if len(idx):
            x = classification[idx, 1]
            y = classification[idx, 2]
            x_scaled = np.clip((x / max_angle) * max_value, 0, max_value - 1e-9)
            y_scaled = ((y - min_norm) / (max_norm - min_norm)) * (100 - 1)
            x_jitter = np.random.uniform(-0.02 * max_angle, 0.02 * max_angle, size=len(x))
            y_jitter = np.random.uniform(-1.0, 1.0, size=len(y))
            x_scaled = np.clip(x_scaled + (x_jitter / max_angle) * max_value, 0, max_value - 1e-9)
            y_scaled = np.clip(y_scaled + y_jitter, 0, 99)
            track.scatter(x_scaled, y_scaled, s=8, color="blue", marker="o", alpha=0.5)

def plot_chord_tracks(circos: Circos, data: pd.DataFrame, min_value: float, max_value: float):
    for sector in circos.sectors:
        track = sector.add_track((55, 55))
        ticks = pretty_breaks(min(0, min_value), max_value, n=6)
        labels = [f"{v:.1f}" if v % 1 else f"{int(v)}" for v in ticks]
        track.xticks(ticks, labels, label_size=6, line_kws=dict(color="black"))

        # Régua horizontal
        track.line(
            x=[ticks[0], ticks[-1]],
            y=[0, 0],
            lw=0.8,
            color="gray"
        )


    for k in range(len(data)):
        for j in range(data.shape[1] - 1):
            for m in range(j + 1, data.shape[1]):
                circos.link_line((str(j + 1), data.iloc[k, j]), (str(m + 1), data.iloc[k, m]), r1=55, r2=55, lw=0.3, color='red')

# --- Execução principal ---
def main():
    #data = pd.read_csv("wfg4_dwu-dec.csv", header=None)
    data = pd.read_csv("plano_4D.csv", header=None)
    points = data.values
    num_points, num_dims = points.shape
    min_value, max_value = data.min().min(), data.max().max()

    classification = compute_classification(points)
    norms = classification[:, 2]
    min_norm, max_norm = np.nanmin(norms), np.nanmax(norms)
    max_angle = np.arccos(1 / np.sqrt(num_dims))

    circos = setup_circos(num_dims, max_value)
    plot_scatter_tracks(circos, classification, max_angle, max_value, min_norm, max_norm)
    plot_chord_tracks(circos, data, min_value, max_value)

    fig = circos.plotfig()
    filename = f"circos_plot_{num_dims}D_{num_points}pts.svg"
    plt.savefig(filename, format = "svg", bbox_inches="tight")
    logging.info(f"Figura salva como {filename}")

if __name__ == "__main__":
    main()
