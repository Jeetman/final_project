import json,csv
data = []
with open('books.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        data.append(row)

json_data = json.dumps(data)

print(json_data)