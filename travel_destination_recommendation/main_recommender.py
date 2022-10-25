import pickle
import numpy as np
from recommend import get_random_recs, get_updated_n_recommendation, recommend_nn

# Load cities and topic 
cities_df = pickle.load(open('../data/cities_with_topic_scores.pkl', 'rb'))
topics = cities_df.drop(['city', 'city_summary', 'country', 'city_url'], axis=1)

# Load NN model
nearest_neighbor = pickle.load(open('../models/nn_model.pkl', 'rb'))


def get_10_cities_to_rate(user_topic_ratings):
    """
    Asks user to rate 10 random cities.
    User Input Meanings:
        1  - visited and liked
        -1 - visited and disliked
        0  - has not visited
    """
    user_topic_scores = [float(topic_rating) / 10 for topic_rating in user_topic_ratings]
    user_topic_scores = np.array(user_topic_scores, dtype=np.float64).reshape(1, -1)

    # Get the 50 nearest neighbors from user rating on five topics.
    closest = recommend_nn(
                    nn_model=nearest_neighbor,
                    cities=cities_df,
                    user_scores=user_topic_scores)

    # Get 10 random recommendations
    # from the top 50 recommended destinations (nearest neighbors)
    random_recs = get_random_recs(closest)

    return random_recs


def recommend_cities(
        rated_cities,
        user_city_ratings=[1,1,0,-1,0,-1,1,-1,0,0],
        user_topic_ratings=[10,0,5,9,6],
        n_of_cities_to_recommend=5,
        visited_cities=None):
    """
    Finds the five most recommended cities determined by user
    input and previously visited cities

    Requires passing back the list of previously rated cities
    and a list with the values (actual ratings).
    """

    if visited_cities is None:
        visited_cities = []

    user_topic_scores = [float(topic_rating) / 10 for topic_rating in user_topic_ratings]
    user_topic_scores = np.array(user_topic_scores, dtype=np.float64).reshape(1, -1)

    user_dict = {}
    city_ratings = []

    for i, rec in enumerate(rated_cities):
        rating = int(user_city_ratings[i])
        city_ratings.append(rating)
        user_dict[str(rec)] = rating
        if rating != 0:
            visited_cities.append(rec)
    
    # Make new recommendation based on new user opinion
    # about the first 10 recommended cities.
    closest = get_updated_n_recommendation(
                        user_score=user_topic_scores,
                        cities=cities_df,
                        random_recs=rated_cities,
                        nn_model=nearest_neighbor,
                        ratings=city_ratings,
                        visited_cities=visited_cities)
    
    recommendations = closest[0:n_of_cities_to_recommend]
    
    return recommendations  

if __name__  == '__main__':
    # Topic (activity) user ratings
    user_topic_ratings = [10, 2, 5, 10, 0]

    # Get some cities to rate based on preffered topics (activities)
    cities_to_rate_based_on_topics = get_10_cities_to_rate(user_topic_ratings)

    # Here ask about the opinion on the given cities
    print("-----")
    print(f"Please give your opinion on following cities: {cities_to_rate_based_on_topics}")

    # Send back the city ratings to the recommend method
    # so new recommendations can be made based on their liked topics
    # but also on their opinions on the retrieved cities
    city_ratings = [0, 1, -1, 0, 0, 0, -1, 1, -1, 0]
    print("-----")
    print(f"Currently hardcoded city ratings in main: {city_ratings}")
    print("-----")

    # Get final recommendation
    number_of_cities_to_recommend = 5
    recommendations = recommend_cities(
                            rated_cities=cities_to_rate_based_on_topics,
                            user_city_ratings=city_ratings,
                            user_topic_ratings=user_topic_ratings,
                            n_of_cities_to_recommend=number_of_cities_to_recommend,
                            visited_cities=None)

    # Show final recommendations
    print(f"Here are your {number_of_cities_to_recommend} recommendations: {cities_to_rate_based_on_topics}")

    pickle.dump(recommendations, open('../data/recommendations.pkl', 'wb'))

    with open('recs.txt', 'a') as f:
        f.write(str(recommendations) + '\n')

    


