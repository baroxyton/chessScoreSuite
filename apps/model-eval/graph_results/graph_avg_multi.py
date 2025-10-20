# Von KI generiert
import matplotlib.pyplot as plt

# # List of CSV files to process
# filenames = [
#     "results.csv.stockfish",
#     "results.csv.recursive_best",
#     "results.csv.avg_best",
# ]
#
#

# filenames = [
#     "results_recursivebest_avgeval.csv",
#     "results_avgplayer_avgeval.csv",
#     "results_sf_avgeval.csv",
#     "results_avgbest_evgeval.csv",
# ]
#
#


# filenames = ["results.csv", "rb_vs_dav.csv"]

#filenames = [
#    "results/results_avgbest_evgeval.csv",
#    "results/results_avgplayer_avgeval.csv",
#    "results/results_recursivebest_avgeval.csv",
#    "results/results_sf_avgeval.csv",
#]
filenames = ["test1.csv", "test2.csv",  "test3.csv"]
#filenames = ["test_sf.csv", "test_sf2.csv", "test_sf3.csv", "test_sf4.csv", "test_sf5.csv"]
#filenames = ["gentest1.csv","gentest2.csv", "gentest3.csv"]


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

# Process and plot each file
for filename in filenames:
    data = read_csv_values(filename)
    avg_values = average_per_column(data)
    plt.plot(avg_values, marker="o", label=filename)

plt.title("Average Values from Multiple CSVs")
plt.xlabel("Index")
plt.ylabel("Average Value")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
