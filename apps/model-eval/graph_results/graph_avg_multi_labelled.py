# Von KI generiert
import matplotlib.pyplot as plt

# List of CSV files to process
# filenames = ["test4.csv", "test1.csv", "test3.csv", "test2.csv"]

filenames = ["gentest1.csv", "gentest2.csv"]


filenames = [
    "results/results_avgplayer_avgeval.csv",
    "results/results_recursivebest_avgeval.csv",
    "results/results_avgbest_evgeval.csv",
    "results/results_sf_avgeval.csv",
]


# filenames = [
# "stockfish_eval/avg_vs_avg.csv",
# "stockfish_eval/rb_vs_avg.csv",
# "stockfish_eval/avb_vs_avg.csv",
# "stockfish_eval/sf_vs_avg.csv"
# ]
#
# Custom labels for each file (must match the order of filenames)
custom_labels = [
    "Average Player (Baseline)",
    "Recursive Best",
    "Average Best",
    "Stockfish",
]


# Alternative examples for different scenarios:
# filenames = ["results_recursivebest_avgeval.csv", "results_avgplayer_avgeval.csv", "results_sf_avgeval.csv"]
# custom_labels = ["Recursive Best", "Average Player", "Stockfish"]
# filenames = ["test_sf.csv", "test_sf2.csv", "test_sf3.csv", "test_sf4.csv", "test_sf5.csv"]
# custom_labels = ["SF Config 1", "SF Config 2", "SF Config 3", "SF Config 4", "SF Config 5"]


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


def average_per_column(lines):
    """Return average of each column index (ignoring missing values)."""
    max_len = max(len(row) for row in lines)
    averages = []
    for col in range(max_len):
        col_values = [row[col] for row in lines if len(row) > col]
        averages.append(sum(col_values) / len(col_values))
    return averages


plt.figure(figsize=(10, 6))

# Process and plot each file with custom labels
for filename, label in zip(filenames, custom_labels):
    data = read_csv_values(filename)
    avg_values = average_per_column(data)
    # Cut off after index 16 (keep indices 0-16, which is 17 data points)
    avg_values = avg_values[:13]
    plt.plot(avg_values, marker="o", label=label)

plt.title("Winning chance over time vs Average Player engine")
plt.xlabel("Move Count")
plt.ylabel("Winning chance difference Δp compared to start")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
