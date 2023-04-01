import pathlib
import psycopg2
import pandas as pd
import os

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    database="book_recommender",
    user="postgres",
    password="postgreadelka5987"
)
cursor = conn.cursor()

# Execute SQL query to retrieve data from postgres tables
query_books = "SELECT * FROM books;"
cursor.execute(query_books)

# Fetch all rows and convert to DataFrame
book_data = cursor.fetchall()
books = pd.DataFrame(book_data, columns=['ISBN', 'book_title', 'book_author', 'year_of_publication', 'publisher', 'image_URL_S', 'image_URL_M', 'image_URL_L'])

# Preprocess book data
books.drop_duplicates(subset=['ISBN'], inplace=True)
books.dropna(inplace=True)

# Repeat the process for "users" and "book_ratings" tables
query_users = "SELECT * FROM users"
cursor.execute(query_users)
user_data = cursor.fetchall()
users = pd.DataFrame(user_data, columns=['user_id', 'user_location', 'age'])
# Preprocess user data
users.drop_duplicates(subset=['user_id'], inplace=True)
users.dropna(inplace=True)

query_ratings = "SELECT * FROM book_ratings"
cursor.execute(query_ratings)
ratings_data = cursor.fetchall()
ratings = pd.DataFrame(ratings_data, columns=['id', 'user_id', 'ISBN', 'book_rating'])


# Close database connection
cursor.close()
conn.close()

print(books[['ISBN', 'book_title', 'book_author', 'year_of_publication', 'publisher']].head())
print(users.head())
print(ratings.head())

path = pathlib.Path(__file__).parent.resolve()
print(path)
path_books = os.path.join(path, "data\\books_df.pickle")
print(path_books)