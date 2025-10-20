# Von KI generiert
import argparse
import csv
import math
import os
import re


import matplotlib.pyplot as plt

FILENAME_RE = re.compile(r"recursive_(\d+)_avg_(\d+)\.csv$")


def detect_levels(results_dir):
    recursive_levels = set()
    avg_levels = set()
    for name in os.listdir(results_dir):
        match = FILENAME_RE.match(name)
        if match:
            recursive_levels.add(int(match.group(1)))
            avg_levels.add(int(match.group(2)))
    return sorted(recursive_levels), sorted(avg_levels)


def aggregate_csv(csv_path, move_target, max_prefix):
    samples = []
    with open(csv_path, newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            values = []
            for cell in row:
                if cell == "":
                    continue
                try:
                    values.append(float(cell))
                except ValueError:
                    continue
            stat = None
            if max_prefix > 0:
                prefix = values[:max_prefix]
                if prefix:
                    stat = max(prefix)
            else:
                index = move_target - 1
                if 0 <= index < len(values):
                    stat = values[index]
            if stat is not None:
                samples.append(stat)
    if not samples:
        return None
    return sum(samples) / len(samples)


def load_grid(results_dir, recursive_levels, avg_levels, move_target, max_prefix):
    grid = []
    for r_elo in recursive_levels:
        row = []
        for a_elo in avg_levels:
            filename = f"recursive_{r_elo}_avg_{a_elo}.csv"
            path = os.path.join(results_dir, filename)
            row.append(
                aggregate_csv(path, move_target, max_prefix)
                if os.path.isfile(path)
                else None
            )
        grid.append(row)
    return grid


def scale_grid(grid, slope, intercept):
    scaled = []
    for row in grid:
        scaled_row = []
        for value in row:
            if value is None or math.isnan(value):
                scaled_row.append(float("nan"))
            else:
                scaled_row.append(
                    max(0.0, slope * value + intercept)
                )
        scaled.append(scaled_row)
    return scaled


def plot_grid(grid, scaled, recursive_levels, avg_levels, output_path, title):
    valid_values = [
        value
        for row in scaled
        for value in row
        if value is not None and not math.isnan(value)
    ]
    if not valid_values:
        print("No numeric data to plot.")
        return
    min_val = min(valid_values)
    max_val = max(valid_values)
    if math.isclose(min_val, max_val):
        vmin = min_val - 0.5
        vmax = max_val + 0.5
    else:
        vmin, vmax = min_val, max_val
    fig, ax = plt.subplots()
    cax = ax.imshow(scaled, cmap="Greens", vmin=vmin, vmax=vmax)
    for y, row in enumerate(grid):
        for x, value in enumerate(row):
            label = "–" if value is None else f"{value:.2f}"
            ax.text(x, y, label, ha="center", va="center", color="black")
    ax.set_xticks(range(len(avg_levels)))
    ax.set_xticklabels([str(v) for v in avg_levels])
    ax.set_yticks(range(len(recursive_levels)))
    ax.set_yticklabels([str(v) for v in recursive_levels])
    ax.set_xlabel("Average player ELO")
    ax.set_ylabel("Recursive score ELO")
    ax.set_title(title)
    cbar = fig.colorbar(cax, ax=ax)
    cbar.set_label("Scaled score (m·x + b)")
    fig.tight_layout()
    if output_path:
        fig.savefig(output_path, bbox_inches="tight")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Render a colored grid from recursive-vs-avg CSV outputs."
    )
    parser.add_argument("results_dir", help="Directory containing the CSV grid files.")
    parser.add_argument(
        "--output",
        default="recursive_avg_grid.png",
        help="Path to save the rendered figure (omit to display).",
    )
    parser.add_argument(
        "--slope",
        type=float,
        default=1.0,
        help="Slope (m) applied to the average score.",
    )
    parser.add_argument(
        "--intercept",
        type=float,
        default=0.5,
        help="Intercept (b) applied after scaling.",
    )
    parser.add_argument(
        "--move-target",
        type=int,
        default=10,
        help="1-based move index used for averaging (ignored when --max-prefix > 0).",
    )
    parser.add_argument(
        "--max-prefix",
        type=int,
        default=0,
        help="If >0, average the per-game maxima across the first N moves.",
    )
    args = parser.parse_args()

    if args.move_target < 1:
        print("--move-target must be >= 1")
        return
    if args.max_prefix < 0:
        print("--max-prefix must be >= 0")
        return

    recursive_levels, avg_levels = detect_levels(args.results_dir)
    if not recursive_levels or not avg_levels:
        print("No matching CSV files found.")
        return
    grid = load_grid(
        args.results_dir,
        recursive_levels,
        avg_levels,
        args.move_target,
        args.max_prefix,
    )
    scaled = scale_grid(grid, args.slope, args.intercept)
    title = (
        f"Average max of first {args.max_prefix} moves"
        if args.max_prefix > 0
        else f"Average score at move {args.move_target}"
    )
    plot_grid(
        grid,
        scaled,
        recursive_levels,
        avg_levels,
        args.output,
        f"{title} grid",
    )


if __name__ == "__main__":
    main()
