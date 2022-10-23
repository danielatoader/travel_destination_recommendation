import pickle
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from recommend import get_topics_user_score, get_user_city_ratings, rate_recs

def get_random_cities_to_rate(cities_df, nn_model, visited_cities=None):
    """
    Finds the five most recommended cities determined by user
    input and previously visited cities
    """
    if visited_cities is None:
        visited_cities = []

    user_score = get_topics_user_score()
    print('''For the following locations give:
            \t1 if you have visited and liked
            \t-1 if you have visited and disliked
            \t0 if you have never been''')

    user_dict = dict()
    closest = get_user_city_ratings(nn_model, cities_df,
                                    user_score, visited_cities, user_dict)
    user_df = pd.DataFrame(user_dict)
    # swap the columns with indexes
    user_df = user_df.transpose()

    pickle.dump(user_df, open('../data/user_df.pkl', 'wb'))

    return closest[0:5]

def get_recommendation():
    # Load cities and topic 
    cities_with_scores = pickle.load(open('../data/cities_with_topic_scores.pkl', 'rb'))
    topics = cities_with_scores.drop(['city', 'city_summary', 'country', 'city_url'], axis=1)

    # Fit model
    nearest_neighbor = NearestNeighbors(n_neighbors=50, metric='minkowski')
    nearest_neighbor.fit(topics)
    # nearest_neighbor = pickle.load(open('../models/nn_model.pkl', 'rb'))

    # Recommend and save to file
    recommendations = get_random_cities_to_rate(cities_with_scores, nearest_neighbor)

    pickle.dump(recommendations, open('../data/recommendations.pkl', 'wb'))

    with open('recs.txt', 'a') as f:
        f.write(str(recommendations) + '\n')
    
    return recommendations   

if __name__  == '__main__':
    user_topic_ratings = [10, 2, 5, 10, 0]
    recommentaions = get_recommendation()
