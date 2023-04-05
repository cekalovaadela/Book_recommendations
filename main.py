import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from os import listdir
from os.path import isfile, join
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from load_sql import Loader

# Load sql data to DataFrames and save them in folder "data"
# Loader.load_sql_to_df()

pd.set_option('display.max_columns', 10)

path = '.\\data'

# Find all files in dir 'path' and unpickle them to dfs
allfiles = [f for f in listdir(path) if isfile(join(path, f))]
print(allfiles)

dfs = {file.strip('.pickle'):pd.read_pickle(f'.\\data\\{file}') for file in allfiles}
print(dfs.keys())

books = dfs['books_df']
books.drop(['image_URL_S', 'image_URL_M', 'image_URL_L'], axis=1, inplace=True)
print(books)
users = dfs['users_df']
ratings = dfs['ratings_df']
user_ratings = dfs['user_ratings_df']

# print(books[['ISBN', 'book_title', 'book_author', 'year_of_publication', 'publisher']].head())
# print(users.head())
# print(ratings.head())
# print(user_ratings)

print(books.isnull().sum())
print(users.isnull().sum())
print(ratings.isnull().sum())
print(user_ratings.isnull().sum())

print(books.shape)
print(users.shape)
print(ratings.shape)
print(user_ratings.shape)

books = dfs['books_df'].head(20000)
users = dfs['users_df'].head(20000)
ratings = dfs['ratings_df'].head(20000)
user_ratings = dfs['user_ratings_df'].head(20000)

print(books.shape)
print(users.shape)
print(ratings.shape)
print(user_ratings.shape)

# Preprocess book data
books.drop_duplicates(subset=['ISBN'], inplace=True)
books.dropna(subset=['book_title'], inplace=True)
books['book_title'] = books['book_title'].apply(lambda x: x.lower())

# Calculate TF-IDF vectors for book titles
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(books['book_title'])

# Compute cosine similarity between book titles
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Preprocess user data
print(users.shape)
# users.drop_duplicates(subset=['user_id'], inplace=True)
# users.dropna(subset=['age'], inplace=True)
# print(users.shape)

# Join user data with book ratings data
user_ratings2 = pd.merge(ratings, users, on='user_id')
print(user_ratings)
print(user_ratings2)

# Get user's preferred book
preferred_book_title = input("Enter a book title that you like: ").lower()
preferred_book = books[books['book_title'] == preferred_book_title].iloc[0]
preferred_book_index = books.index[books['book_title'] == preferred_book_title][0]

# Compute cosine similarity between preferred book and all other books
sim_scores = list(enumerate(cosine_sim[preferred_book_index]))
sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

# Get top 10 similar books
top_books = [books.iloc[i[0]] for i in sim_scores[1:11]]

# Print recommended books
print("Books similar to " + preferred_book_title + ":")
for book in top_books:
    print(book['book_title'] + " by " + book['book_author'])


############

# # Preprocess the book data
# books['title_author'] = books['book_title'] + ' ' + books['book_author']
# print(books)
# tfidf = TfidfVectorizer()
# tfidf_matrix = tfidf.fit_transform(books['title_author'])
# # print(tfidf_matrix)
# similarity_matrix = cosine_similarity(tfidf_matrix)
# # print(similarity_matrix)

# print(books.loc[books['ISBN'] == '0195153448'])
# print(user_ratings.loc[user_ratings['ISBN'] == '0195153448'])
# # Recommend books based on user profile
# book_index = books[books['ISBN'] == user_ratings['ISBN'].values[0]].index
# print(book_index)
# similar_books = list(enumerate(similarity_matrix[book_index][0]))
# sorted_similar_books = sorted(similar_books,key=lambda x:x[1],reverse=True)[1:]
# # print(sorted_similar_books)
# recommendations = []
# for i in range(5):
#     book = books.iloc[sorted_similar_books[i][0]]
#     recommendations.append({'title': book['book_title'], 'author': book['book_author'], 'score': sorted_similar_books[i][1]})

# print(recommendations)



########

# books = dfs['books_df']
# books.drop(['image_URL_S', 'image_URL_M', 'image_URL_L'], axis=1, inplace=True)
# users = dfs['users_df']
# ratings = dfs['ratings_df']
# user_ratings = dfs['user_ratings_df']

# # print(books[['ISBN', 'book_title', 'book_author', 'year_of_publication', 'publisher']].head())
# # print(users.head())
# # print(ratings.head())
# # print(user_ratings)

# # print(books.isnull().sum())
# # print(users.isnull().sum())
# # print(ratings.isnull().sum())
# # print(user_ratings.isnull().sum())

# print(books.shape)
# print(users.shape)
# print(ratings.shape)
# print(user_ratings.shape)

# # Join user data with book ratings data
# user_ratings = pd.merge(ratings, users, on='user_id')
# books = pd.merge(books, user_ratings, on='ISBN')
# print(books)
# print(books.shape)
# books = books[books.book_rating != 0]
# print(books.shape)

# books = books.head(20000)

# # Changing the 'book_title' to all lower letters
# books['book_title'] = books['book_title'].apply(lambda x: x.lower())

# # Calculate TF-IDF vectors for book titles
# tfidf = TfidfVectorizer(stop_words='english')
# tfidf_matrix = tfidf.fit_transform(books['book_title'])

# # Compute cosine similarity between book titles
# cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)


# # Get user's preferred book
# preferred_book_title = input("Enter a book title that you like: ").lower()
# preferred_book = books[books['book_title'] == preferred_book_title].iloc[0]
# preferred_book_index = books.index[books['book_title'] == preferred_book_title][0]

# # Compute cosine similarity between preferred book and all other books
# sim_scores = list(enumerate(cosine_sim[preferred_book_index]))
# sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

# # Get top 10 similar books
# top_books = [books.iloc[i[0]] for i in sim_scores[1:11]]

# # Print recommended books
# print("Books similar to " + preferred_book_title + ":")
# for book in top_books:
#     print(book['book_title'] + " by " + book['book_author'])