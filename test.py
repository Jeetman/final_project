import json,csv
data = []
with open('books.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        data.append(row)
        book_title = row['Book Title']
        isbn = row['ISBN']
        author = row['Author']
        genre = row['Genre 1']
        genre2 = row['Genre 2']
        genre3 = row['Genre 3']
        genre4 = row['Genre 4']
        genreAll = genre + "," + genre2 + "," + genre3 + "," + genre4
        print(genreAll)

json_data = json.dumps(data)
