import csv
import sys

def process_csv(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as infile, \
         open(output_file, "w", newline="", encoding="utf-8") as outfile:
    
        reader = csv.DictReader(infile)
    
        fieldnames = ["Rank", "Score", "Id", "Name", "Level"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            level = int(row["Level"])
            extra = 0
            if level > 27:
                extra = level - 27
                level = 27
            row["Level"] = int((level + 2) / 3) + extra

            trimmed = {key: row[key] for key in fieldnames}
            writer.writerow(trimmed)

    print("Done! Output saved to", output_file)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python platoon_ranking_csv.py <input_file> <output_file>")
        sys.exit(1)

    process_csv(sys.argv[1], sys.argv[2])