import engines
import chess

openings = []

file = open("openings.txt", "r")
for line in file:
    if line.strip() == "":
        continue
    openings.append(line.strip())
file.close()
