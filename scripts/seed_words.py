import requests
import csv

with open("resources/HumorDataset_Means.csv") as csvfile:
    reader = csv.reader(csvfile)
    # each row is an array with fields in order
    for row in reader:
        request_body = {
                "word_name": row[1],
                "student_fname": "",
                "student_lname": "",
                "student_email": "seed",
                "seed": "1"
                }

        response = requests.post("http://0.0.0.0:50000/submit", data=request_body)

        print(response.status_code)
