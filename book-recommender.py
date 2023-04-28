# <snippet_1>
import csv
import json
import random
import heapq

from azure.cognitiveservices.personalizer import PersonalizerClient
from azure.cognitiveservices.personalizer.models import RankableAction, RewardRequest, RankRequest
from msrest.authentication import CognitiveServicesCredentials

import datetime, json, os, time, uuid, random

key = "9a506bda75c644d2ad1870de72c4e070"
endpoint = "https://book-recommender-2.cognitiveservices.azure.com/"

# Instantiate a Personalizer client
client = PersonalizerClient(endpoint, CognitiveServicesCredentials(key))
# Open the CSV file
actions_and_features = {}
# book_titles = []
# book_authors = []
book_attr = []

unique_genre_file = "genres.csv" 
genre_list = []
with open(unique_genre_file, newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        genre_list.append(row[0])

# Open the CSV file
unique_genre_set = set()
with open('data_trim.csv') as csv_file:
    # Read the data from the CSV file as a dictionary
    csv_reader = csv.DictReader(csv_file)
    # Initialize an empty dictionary to store the book information
    books = {}
    # Loop through each row of the CSV file
    for row in csv_reader:
        # Create a dictionary to store the book information
        book_info = {
            "title": row['Book Title'],
           # "year": row['Year'],
            "Author": row['Author']
        }
        # attributes = []
        # if row['Attribute 1'] is not None and row['Attribute 1'] != '':
        #     attributes.append(row['Attribute 1'])
        # if row['Attribute 2'] is not None and row['Attribute 2'] != '':
        #     attributes.append(row['Attribute 2'])
        # if row['Attribute 3'] is not None and row['Attribute 3'] != '':
        #     attributes.append(row['Attribute 3'])
        
        genre = {}
        # genre_list = []
        for genre_ in genre_list:
          genre[genre_] = False

        if row['Genre 1'] is not None and row['Genre 1'] != '':
            genre[row['Genre 1']] = True
            genre_list.append(row['Genre 1'])
            unique_genre_set.add(row['Genre 1'])
        if row['Genre 2'] is not None and row['Genre 2'] != '':
            genre[row['Genre 2']] = True
            genre_list.append(row['Genre 2'])
            unique_genre_set.add(row['Genre 2'])
        if row['Genre 3'] is not None and row['Genre 3'] != '':
            genre[row['Genre 3']] = True
            genre_list.append(row['Genre 3'])
            unique_genre_set.add(row['Genre 3'])
        if row['Genre 4'] is not None and row['Genre 4'] != '':
            genre[row['Genre 4']] = True
            genre_list.append(row['Genre 4'])
            unique_genre_set.add(row['Genre 4'])

        book_data = {
            "book_info": book_info,
            "genre": genre
            # "genre": set(genre_list)
            # "attributes": attributes
        }
        book_attr.append(row['Book Title'])
        book_attr.append(row['Author'])
        #book_attr.append(row['ISBN'])
        books[row['ISBN']] = book_data
    actions_and_features = books

    # json_books = json.dumps(books, indent=4)
    # # Print the JSON object
    # print(json_books)


# print('length: ', len(unique_genre_set))
# genre_list = list(unique_genre_set)

def get_actions():
    res = []
    for action_id, feat in actions_and_features.items():
        action = RankableAction(id=action_id, features=[feat])
        res.append(action)
    return res


# with open('genres.csv', mode='w', newline='') as file:
#     writer = csv.writer(file)
#     for genre in unique_genre_set:
#         writer.writerow([genre])


# user_profiles = []
# for i in range(40):
#     user_profiles.append({'genre': set(random.sample(genre_list, k=9))})



# print(user_profiles)
# user_profiles_path = 'user_profiles.csv'
# with open(user_profiles_path, 'w', newline='') as csvfile:
#     writer = csv.writer(csvfile)
#     for user_profile in user_profiles:
#         writer.writerow(list(user_profile['genre']))

user_profiles = []
user_profiles_path = 'user_profiles.csv'
with open(user_profiles_path, 'r') as f:
    for line in f:
        genres = line.strip().split(',')
        # user_genre = {}
        # for genr in genres:
        #     user_genre[genr] = True
        # profile = {'genre': user_genre}
        profile = {'genre_preferences':set(genres)}
        user_profiles.append(profile)
# print('>>>>>>>><<<<<<<<<<<')
# print(user_profiles)


def get_context(user_idx):

    # search_term = {'book_info': random.choice(book_attr)}
    # res = [user_profiles[user_idx], search_term]
    res = [user_profiles[user_idx]]
    return res

def get_random_users(k = 5):
    return random.sample(range(len(user_profiles)), k)
    # return random.choices(user_profiles, k=k)


def get_reward_score(user, actionid, context):
    reward_score = 0.0
    action = actions_and_features[actionid]
    # print(user)
    # print(action)
    # print(context)

    selected_genre = set([k for k,v in action['genre'].items() if v == True])
    # selected_genre = action['genre']
    # print(selected_genre)
    for ctx in context:
        # print("inside context")
        # print(ctx)
        if 'genre_preferences' in ctx:

            context_genre = ctx['genre_preferences']
            
            matching_genres = selected_genre.intersection(context_genre)
            # print(context_genre)
            # print(selected_genre)
            # print(matching_genres)
            if len(matching_genres) >= 1:
                reward_score = 1.0
            # elif len(matching_genres) == 2:
            #     reward_score = 0.9
            # elif len(matching_genres) >= 3:
            #     reward_score = 1.0
            # reward_score = len(matching_genres)/len(selected_genre)

            # print("matching_genres:", matching_genres)
            # print("reward_score: ",reward_score)
            
        # if 'book_info' in ctx:
        #     if actionid == ctx['book_info'] or action['book_info']['title'] == ctx['book_info'] or action['book_info']['Author'] == ctx['book_info']:
        #         reward_score = 1.0
                #print("found a perfect match")

    return reward_score
    

def run_personalizer_cycle(actions):
    
    user_idx_list = get_random_users(5)
    for user_idx in user_idx_list:
        user = user_profiles[user_idx]
        # print("------------")
        # print("User:", user, "\n")
        context = get_context(user_idx)
        # print("Context:", context, "\n")
        # print("Actions: ", actions[0], "\n")
        
        rank_request = RankRequest(actions=actions, context_features=context)
        response = client.rank(rank_request=rank_request)
        # print("Rank API response:", response, "\n")

        ranked_actions = [(action.id, action.probability) for action in response.ranking]
        top_actions = heapq.nlargest(5, ranked_actions, key=lambda x: x[1])
        # print(top_actions)
        # print(ranked_actions)
        
        eventid = response.event_id
        actionid = response.reward_action_id
        # print("Personalizer recommended action", actionid, "and it was shown as the featured product.\n")
        
        reward_score = get_reward_score(user, actionid, context)
        client.events.reward(event_id=eventid, value=reward_score)     
        # print("\nA reward score of", reward_score , "was sent to Personalizer.")
        print(reward_score)
        # print("------------\n")

continue_loop = True
actions = get_actions()
while continue_loop:

    run_personalizer_cycle(actions)
    
    br = input("Press Q to exit, or any other key to run another loop: ")
    if(br.lower()=='q'):
        continue_loop = False
# </snippet_2>

# <snippet_multi>
for i in range(0,12000):
    run_personalizer_cycle(actions)
    if i%400 == 0:
        print('--------------------------------------------------------------------------------------------------------')
        print(i)
        print('--------------------------------------------------------------------------------------------------------')
# </snippet_multi>
