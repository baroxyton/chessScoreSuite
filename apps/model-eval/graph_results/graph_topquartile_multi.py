# Von KI generiert
import matplotlib.pyplot as plt

# filenames = [
#     "results/results_avgbest_evgeval.csv",
#     "results/results_avgplayer_avgeval.csv",
#     "results/results_recursivebest_avgeval.csv",
#     "results/results_sf_avgeval.csv",
# ]
#
#
#filenames = ["test1.csv", "test2.csv", "test3.csv"]

filenames = ["test_sf.csv", "test_sf2.csv", "test_sf3.csv"]

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


def quartile_averages_per_column(lines):
    """
    For each column index:
    - Sort the values
    - Compute average of bottom 25%
    - Compute average of top 25%
    Returns two lists: (worst_quartile_avgs, best_quartile_avgs)
    """
    max_len = max(len(row) for row in lines)
    worst_avgs = []
    best_avgs = []
    for col in range(max_len):
        col_values = [row[col] for row in lines if len(row) > col]
        if not col_values:
            worst_avgs.append(float("nan"))
            best_avgs.append(float("nan"))
            continue
        col_values.sort()
        qsize = max(1, len(col_values) // 4)  # at least 1 element
        worst_quarter = col_values[:qsize]
        best_quarter = col_values[-qsize:]
        worst_avgs.append(sum(worst_quarter) / len(worst_quarter))
        best_avgs.append(sum(best_quarter) / len(best_quarter))
    return worst_avgs, best_avgs


plt.figure(figsize=(10, 6))

# Process and plot each file
for filename in filenames:
    data = read_csv_values(filename)
    worst_q, best_q = quartile_averages_per_column(data)

    plt.plot(worst_q, marker="o", linestyle="--", label=f"{filename} (Worst Q)")
    plt.plot(best_q, marker="o", linestyle="-", label=f"{filename} (Best Q)")

plt.title("Best & Worst Quartile Averages per File")
plt.xlabel("Index")
plt.ylabel("Average Value")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
