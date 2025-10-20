# Von KI generiert
import matplotlib.pyplot as plt

filename = "results.csv"

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

# Plot all lines in the same figure
plt.figure(figsize=(10, 6))
for idx, values in enumerate(lines, start=1):
    plt.plot(values, marker="o", label=f"Line {idx}")

plt.title("Results from results.csv")
plt.xlabel("Index")
plt.ylabel("Value")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

