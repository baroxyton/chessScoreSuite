# Von KI generiert
import matplotlib.pyplot as plt

# List of CSV files to process
filenames = ["test4.csv", "test1.csv", "test3.csv", "test2.csv"]
# Custom labels for each file (must match the order of filenames)
custom_labels = [
    "Average Player",
    "Recursive Best",
    "Average Best",
    "Stockfish",
]


def read_csv_values(filename):
    """Read CSV into list of lists of floats, skip blank/malformed lines."""
    lines = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                values = [float(x) for x in line.split(",") if x.strip()]
                if values:
                    lines.append(values)
            except ValueError:
                print(f"Skipping malformed line in {filename}: {line}")
    return lines


def fraction_per_column(lines):
    """Return fraction of rows that still have a value at each index."""
    max_len = max(len(row) for row in lines)
    fractions = []
    n_rows = len(lines)
    for col in range(max_len):
        count = sum(1 for row in lines if len(row) > col)
        fractions.append(count / n_rows)
    return fractions


plt.figure(figsize=(10, 6))

# Process and plot each file with custom labels
for filename, label in zip(filenames, custom_labels):
    data = read_csv_values(filename)
    fractions = fraction_per_column(data)

    # Cut off after index 16 (keep indices 0-16, which is 17 data points)
    fractions = fractions[:17]

    plt.plot(fractions, marker="o", label=label)

    # --- Compute average ending index ---
    avg_end = sum(len(row) for row in data) / len(data)

    # If avg_end > 16 (cutoff), cap it for plotting
    end_index = min(int(round(avg_end)), len(fractions) - 1)

    # y-value at that index
    y_value = fractions[end_index]

    # Add a dot + label on the curve
    plt.scatter(end_index, y_value, marker="x", s=100)
    plt.text(
        end_index, y_value, f"avg={avg_end:.1f}", fontsize=8, ha="left", va="bottom"
    )

plt.title("Fraction of still ongoing games vs Move Count")
plt.xlabel("Move Count")
plt.ylabel("Fraction of games still ongoing")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
