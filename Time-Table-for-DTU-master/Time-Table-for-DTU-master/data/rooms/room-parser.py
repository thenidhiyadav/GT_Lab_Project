import csv
import re

with open("rooms.txt") as f:
    rooms = f.readlines()

# CSV file writter
out = csv.writer(open("rooms.csv", "w"), delimiter=',',quoting=csv.QUOTE_ALL)

row = [rooms, 1]
headerRow = ["campus", "name", "capacity"]
out.writerow(headerRow)

for room in rooms:
    # campus
    campus_id_length = 10
    
    if re.search('G', room[:1], re.IGNORECASE):
        campus = 'DTU'
        campus_id_length = 1
    elif re.search('Technical Wing', room[:campus_id_length], re.IGNORECASE):
        campus = 'DTU'
    elif re.search('Lecturer Wing', room[:campus_id_length], re.IGNORECASE):
        campus = 'DTU'
    elif re.search('SPS', room[:campus_id_length], re.IGNORECASE):
        campus = 'DTU'
    elif re.search('Inclined Wing', room[:campus_id_length], re.IGNORECASE):
        campus = 'DTU'
    else:
        campus = 'Unknown'
        campus_id_length = 0
    
    # Name
    name = room[campus_id_length:].rsplit(' (')[0]
    
    # Capacity - The last number is the capacity
    numbers = re.findall('\d+', room)
    capacity = numbers[len(numbers) - 1]
    
    row = [campus, name, capacity]
    out.writerow(row)