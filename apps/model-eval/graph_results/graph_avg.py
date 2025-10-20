# Von KI generiert
import matplotlib.pyplot as plt

filename = "test_sf.csv"

# Read and process file
lines = []
with open(filename, "r") as f:
    for line in f:
        line = line.strip()
        if not line:  # skip blank lines
            continue
        try:
            values = [float(x) for x in line.split(",") if x.strip()]
            if values:
                lines.append(values)
        except ValueError:
            print(f"Skipping malformed line: {line}")

# Compute average for each column index
max_len = max(len(row) for row in lines)
avg_values = []
for col in range(max_len):
    col_values = [row[col] for row in lines if len(row) > col]
    avg_values.append(sum(col_values) / len(col_values))

# Plot the average
plt.figure(figsize=(10, 6))
plt.plot(avg_values, marker="o", label="Average", color="blue")

plt.title("Average Values from results.csv")
plt.xlabel("Index")
plt.ylabel("Average Value")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
