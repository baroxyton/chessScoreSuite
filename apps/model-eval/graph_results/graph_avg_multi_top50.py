# Von KI generiert
import matplotlib.pyplot as plt

filenames = ["results.csv", "rb_vs_dav.csv"]


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


def average_per_column_top_25(lines):
    """
    For each column index, sort the values, keep only the top 25%,
    and average them.
    """
    max_len = max(len(row) for row in lines)
    averages = []
    for col in range(max_len):
        col_values = [row[col] for row in lines if len(row) > col]
        if not col_values:
            averages.append(float("nan"))
            continue
        col_values.sort()
        #col_values.reverse()
        start_index = int(len(col_values) * 0.8)  # start at 75% mark
        top_quarter = col_values[start_index:]
        averages.append(sum(top_quarter) / len(top_quarter))
    return averages


plt.figure(figsize=(10, 6))

# Process and plot each file
for filename in filenames:
    data = read_csv_values(filename)
    avg_values = average_per_column_top_25(data)
    plt.plot(avg_values, marker="o", label=filename)

plt.title("Top 25% Average Values from Multiple CSVs")
plt.xlabel("Index")
plt.ylabel("Average of Top 25%")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

