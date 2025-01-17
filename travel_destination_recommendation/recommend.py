import numpy as np

def get_topics_user_score():
    """Collect initial user score"""

    print('''Rate on a scale of 0-10.
    0 is not important and 10 is very important''')

    topics = ['a forest/mountain setting', 'visiting palaces/castles',
              'a coastal/water setting', 'historical sites',
              'an urban setting']

    user_scores = [float(input(f"How important is {topic}: ")) / 10
                   for topic in topics]
    print('\n')
    return np.array(user_scores).reshape(1, -1)


def recommend_nn(nn_model, cities, user_scores):
    """
    Gives the 50 nearest neighbors from user rating on five topics.
    The number of neighbors is determined prior to this function
    during the instantiation of the nn_model.
    """
    distances, closest = nn_model.kneighbors(user_scores)
    # distances and closest are both a list of a list [[#,#,...]]

    destinations = []
    for index in closest[0]:
        destination = (cities.iloc[index]['city'],
                       cities.iloc[index]['country'])
        destinations.append(destination)
    distances = [distance for distance in distances[0]]
    return list(zip(destinations, distances))


def get_random_recs(closest):
    """Generates 10 random recommendations from
       top 50 recommended destinations"""
    return np.random.choice(np.array(closest)[:, 0], 10, replace=False)


def get_city_scores(cities_df, city):
    """
    Retrieve the topic scores for a specific city.
    """
    topics = ['forest_mountain', 'palaces',
              'island_water', 'historical_ww2', 'urban']
    city_score = cities_df.loc[cities_df['city'] == city,
                               topics].values.tolist()
    return city_score


def update_user_score(user_score, cities, random_recs, city_rating):
    """
    Finds the new user score by averging the original user input with a
    positive or negative score if the user liked (1) or disliked (-1) a
    city. If the user has not been to the city, it is not included in
    the average calculation.
    """
    user_score = user_score.tolist()
    # city takes form ('city', 'country')
    for ind, city in enumerate(random_recs):
        rating = int(city_rating[ind])
        if rating != 0:
            city_score = get_city_scores(cities, city[0])
            if rating == -1:
                for i, score in enumerate(city_score[0]):
                    score = -1 * score
                    city_score[0][i] = score
            user_score.extend(city_score)

    # generate new score
    new_score = []
    for i in range(5):
        new_score.append(np.mean([item[i] for item in user_score]))

    return np.array(new_score).reshape(1, -1)


def get_updated_n_recommendation(user_score, cities, random_recs,
                                 nn_model, ratings, visited_cities):
    """
    Give the n top recommended desitinations by distance with updated
    user score.Also remove destinations already known to have visited
    """
    user_score = update_user_score(user_score, cities, random_recs, ratings)
    updated_recs = recommend_nn(nn_model, cities, user_score)

    updated_city_recs = [rec[0] for rec in updated_recs]
    
    # find indices of visited cities
    indices_to_remove = []
    for updated_city in updated_city_recs:
        if updated_city in visited_cities:
            index = updated_city_recs.index(updated_city)
            indices_to_remove.append(index)

    # remove visited cities
    for index in sorted(indices_to_remove, reverse=True):
        del updated_recs[index]

    return updated_recs


def get_user_city_ratings(nn_model, cities, user_score,
                          visited, user_coll):
    """
    Asks user to rate 10 random cities.
    User Input Meanings:
        1  - visited and liked
        -1 - visited and disliked
        0  - has not visited
    """
    closest = recommend_nn(nn_model, cities, user_score)
    user_dict = {}

    random_recs = get_random_recs(closest)
    city_ratings = []

    for i, rec in enumerate(random_recs):
        rating = int(input(f"Rate {random_recs[i]}: "))
        city_ratings.append(rating)
        user_dict[str(rec)] = rating
        if rating != 0:
            visited.append(rec)

    # new closest
    closest = get_updated_n_recommendation(user_score, cities,
                                           random_recs, nn_model,
                                           city_ratings, visited)

    user_coll[len(user_coll)] = user_dict

    # user_coll.insert_one(user_dict)

    # user_df = pd.DataFrame(user_dict)
    # swap the columns with indexes
    # user_df = user_df.transpose()
    # pickle.dump(user_df, open('../data/user_df.pkl', 'wb'))

    return closest

def rate_recs(recommendations):
    """
    Asks the user to rate, by interest, their recommended destinations
    """
    interest = []
    print('If interested in visiting enter 1, else 0')
    for rec in recommendations:
        interest.append(int(input(str(rec[0]) + ': ')))
    satisfaction = {'satisfaction_score': sum(interest) / 5}
    # user_satisfaction.insert_one(satisfaction)
