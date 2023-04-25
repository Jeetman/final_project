import requests

ISBN = "9780596000851"  # example ISBN

# make a request to the Library of Congress API to get the corresponding LCCN
response = requests.get(f"https://www.loc.gov/search/?q=isbn:{ISBN}&fo=json")
data = response.json()
lccn = data["results"][0]["lccn"][0]

# use the LCCN to get the corresponding subject categories
response = requests.get(f"https://www.loc.gov/lccn/{lccn}/classification")
subject_categories = response.text

print(subject_categories)
