import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

pd.set_option('display.max_columns', 10)

# Load the movies.csv into a Pandas df
movies = pd.read_csv('.\\ml-25m\\movies.csv')
movie_range = range(0,10000)
# movies = movies.loc[movies['movieId'].isin(movie_range)]
print(movies)

# Load the genome-tags.csv and genome-scores.csv in to Pandas dataframes
genome_tags = pd.read_csv('.\\ml-25m\\genome-tags.csv')
print(genome_tags)
genome_scores = pd.read_csv('.\\ml-25m\\genome-scores.csv')
# genome_scores = genome_scores.loc[genome_scores['movieId'].isin(movie_range)] 
print(genome_scores)


##### BAG OF WORDS
# # Extract the movie titles and genres into separate lists
# titles = movies['title'].tolist()
# genres = movies['genres'].str.split("|").tolist()
# print(genres[0:10])

# # Function that calculates the bag of words
# def create_bow(genre_list):
#     bow = {}
#     for genre in genre_list:
#         bow[genre] = 1
#     return bow

# # Create a list of bags of words representations of the movie genres
# bags_of_words = [create_bow(movie_genres) for movie_genres in genres]
# print(bags_of_words[0:10])

# # Create a df to store the bags of words representation of the movie genres
# genre_df = pd.DataFrame(bags_of_words, index=titles).fillna(0)
# print(genre_df)

# # Calculate the cosine similarity matrix between the movies
# cos_similarity_bow = cosine_similarity(genre_df)
# # print(cos_similarity)

# # Create a df with the cosine similarity scores
# cos_similarity_bow_df = pd.DataFrame(cos_similarity_bow, index=genre_df.index, columns=genre_df.index)

# ### Uncomment to pickle (save) the df and then load it
# # # Pickle df
# # cos_similarity_df.to_pickle('cos_similarity_df.pickle')

# # # Load pickled df
# # cos_similarity_df = pd.read_pickle('cos_similarity_df.pickle')


# # Ask a user for an input - the movie he/she likes
# movie = input('Enter a movie: ')

# # Find the index of the movie in the similarity dataframe
# movie_index = cos_similarity_bow_df.index.get_loc(movie)

# # Get the top 10 most similar movies to the movie
# top_10 = cos_similarity_bow_df.iloc[movie_index].sort_values(ascending=False)[1:11]

# # Print the top 10 most similar movies to the movie
# print(f'Top 10 similar movies to {movie}:')
# print(top_10)


##### TF-IDF
# # Combine the genres for each movie into a signle string
# genres_combined = movies['genres'].str.replace("|", " ")

# # Create a TfidfVectorizer object to transform the movie genres into a Tf-idf representation
# tfidf = TfidfVectorizer()
# tfidf_matrix = tfidf.fit_transform(genres_combined)

# # Calculate the cosine similarity between the movies
# cos_similarity_tfidf = cosine_similarity(tfidf_matrix)

# # Create a df with the cosine similarity scores
# cos_similarity_tfidf_df = pd.DataFrame(cos_similarity_tfidf, index=movies['title'], columns=movies['title'])

# # Find the index of the movie in the similarity dataframe
# movie_index = cos_similarity_tfidf_df.index.get_loc(movie)

# # Get the top 10 most similar movies to the movie
# top_10 = cos_similarity_tfidf_df.iloc[movie_index].sort_values(ascending=False)[1:11]

# # Print the top 5 most similar movies to the movie
# print(f'Top 10 similar movies to {movie}:')
# print(top_10)



##### GENOME SCORES & GENOME TAGS
# Merge the genome_scores df with the genome_tags df to get the relevance score for each tag
genome_merged = genome_scores.merge(genome_tags, on='tagId', how='left')
print(genome_merged)
print(genome_merged[genome_merged['movieId'] == 1])

# Filter the genome_merged df to only include the tags with relevance > 0.5 for each movie
top_tags = genome_merged[genome_merged['relevance'] > 0.5]
top_tags.reset_index(drop=True, inplace=True)
print(top_tags)
print(top_tags[top_tags['movieId'] == 1])

# Group the 'top_tags' df by 'movieId' and join the 'tag' values in the 'tag' column separated by a comma
grouped_tags = top_tags.groupby('movieId')['tag'].apply(lambda x: ', '.join(x)).reset_index()
print(grouped_tags)

# Merge the 'movies' df with the 'grouped_tags' df
final_df = movies.merge(grouped_tags, on='movieId', how='left')
print(final_df)

# Select only the desired columns in the final dataframe
final_df = final_df[['movieId', 'title', 'genres', 'tag']]
print(final_df.shape)
final_df.dropna()
print(final_df.shape)
print(final_df.head(50))

# Some movies don't have a tag so let's add genres of the movie to tag
def add_genres_to_tag(row):
    if pd.isnull(row['tag']):
        return row['genres'].replace("|", ",")
    else:
        return row['tag'] + "," + row['genres'].replace("|", ",")
    
final_df['tag'] = final_df.apply(lambda row: add_genres_to_tag(row), axis=1)
print(final_df['tag'][0])


# Extract the movie titles and tags into separate lists
titles = final_df['title'].tolist()
tags = final_df['tag'].str.strip().str.split(",").tolist()

# Create a bag of words representation of the movie tags
def create_bow(tag_list):
    bow = {}
    if not isinstance(tag_list, float):
        for tag in tag_list:
            bow[tag] = 1
    return bow
     

# Create a list of bags of words representations of the movie tags
bags_of_words = [create_bow(movie_tags) for movie_tags in tags]

# Create a dataframe to store the bags of words representation of the movie tags
tag_df = pd.DataFrame(bags_of_words, index=titles).fillna(0)

# Calculate the cosine similarity matrix between the movies
cosine_similarity = cosine_similarity(tag_df)

# Create a dataframe with the cosine similarity scores
similarity_df = pd.DataFrame(cosine_similarity, index=tag_df.index, columns=tag_df.index)

# Ask the user for a movie they like
movie = input('Enter a movie you like: ')

# Find the index of the movie in the similarity dataframe
movie_index = similarity_df.index.get_loc(movie)

# Get the top 10 most similar movies to the movie
top_10 = similarity_df.iloc[movie_index].sort_values(ascending=False)[1:11]

# Print the top 10 most similar movies to the movie
print(f'Top 10 similar movies to {movie}:')
print(top_10)