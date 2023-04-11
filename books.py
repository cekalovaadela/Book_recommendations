import pandas as pd
import PySimpleGUI as sg
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from os import listdir
from os.path import isfile, join
from load_sql import Loader

class Book:

    def recommend_book():

        # Load sql data to DataFrames and save them in folder "data"
        Loader.load_sql_to_df()

        path = '.\\data'

        # Find all files in dir 'path' and unpickle them to dfs
        allfiles = [f for f in listdir(path) if isfile(join(path, f))]

        dfs = {file.strip('.pickle'):pd.read_pickle(f'.\\data\\{file}') for file in allfiles}

        books = dfs['books_df']
        books.drop(['image_URL_S', 'image_URL_M', 'image_URL_L'], axis=1, inplace=True)
        user_ratings = dfs['user_ratings_df']

        # Dropping incorrect ISBN format in books df
        books['correct_ISBN'] = books['ISBN'].str.isnumeric()
        books.drop(books[books['correct_ISBN'] == False].index, inplace=True)
        books.drop(['correct_ISBN'], axis=1, inplace=True)

        books['correct_len'] = (books['ISBN'].str.len() == 10) | (books['ISBN'].str.len() == 13)
        books.drop(books[books['correct_len'] == False].index, inplace=True)
        books.drop(['correct_len'], axis=1, inplace=True)

        # Checking a correct ISBN format in user_ratings df
        user_ratings['correct_ISBN'] = user_ratings['ISBN'].str.isnumeric()
        user_ratings.drop(user_ratings[user_ratings['correct_ISBN'] == False].index, inplace=True)
        user_ratings.drop(['correct_ISBN'], axis=1, inplace=True)

        user_ratings['correct_len'] = (user_ratings['ISBN'].str.len() == 10) | (user_ratings['ISBN'].str.len() == 13)
        user_ratings.drop(user_ratings[user_ratings['correct_len'] == False].index, inplace=True)
        user_ratings.drop(['correct_len'], axis=1, inplace=True)

        # Ensuring reasonable rating
        user_ratings['book_rating'] = pd.to_numeric(user_ratings['book_rating'])
        user_ratings = user_ratings[user_ratings['book_rating'].isin([1,2,3,4,5,6,7,8,9])]

        # Group the 'grouped_rating' df by 'ISBN' and join the 'book_rating' values in the 'book_rating' column separated by a comma
        user_ratings = user_ratings.astype(str)
        grouped_rating = user_ratings.groupby('ISBN')['book_rating'].apply(lambda x: ', '.join(x)).reset_index()

        # Calculating average rating for each book
        user_ratings['book_rating'] = user_ratings['book_rating'].astype(float)
        try:
            avg_rating = user_ratings.groupby(['ISBN'])['book_rating'].mean()
        except:
            avg_rating = 0

        # Merging dfs together and dropping rows NaN values
        grouped_rating = grouped_rating.merge(avg_rating, on='ISBN', how='left')
        books = books.merge(grouped_rating, on='ISBN', how='left')
        books = books[books['book_rating_x'].notnull()]

        # Creating a new column 'tag' that contains: title, author, year of publication, publisher, and an average rating
        books = books.astype(str)
        books['tag'] = books['book_title'] + ', ' + books['book_author'] +  ', ' + books['year_of_publication'] +  ', ' + books['publisher'] +  ', ' + books['book_rating_y']

        # Reducing the size of the dataset because of computational demand
        books = books.head(10000)

        # Extract the book titles and tags into separate lists
        titles = books['book_title'].tolist()
        tags = books['tag'].str.strip().str.split(",").tolist()

        # Create a bag of words representation of the book tags
        def create_bow(tag_list):
            bow = {}
            if not isinstance(tag_list, float):
                for tag in tag_list:
                    bow[tag] = 1
            return bow
            

        # Create a list of bags of words representations of the book tags
        bags_of_words = [create_bow(book_tags) for book_tags in tags]

        # Create a dataframe to store the bags of words representation of the book tags
        tag_df = pd.DataFrame(bags_of_words, index=titles).fillna(0)

        # Calculate the cosine similarity matrix between the books
        cos_similarity = cosine_similarity(tag_df)

        # Create a dataframe with the cosine similarity scores
        similarity_df = pd.DataFrame(cos_similarity, index=tag_df.index, columns=tag_df.index)

        print(books[books['book_author'].str.contains('Shakespeare')])
        
        layout = [
            [sg.Text('Please enter your favorite book!')],
            [sg.Text('Name of the book:', size =(15, 1)), sg.InputText()],
            [sg.Submit(), sg.Cancel()]
        ]
        
        window = sg.Window('Book recommendations', layout)
        event, values = window.read()

        if event == 'Cancel' or sg.WINDOW_CLOSED:
            value = 'NaN'
            print('The action was cancelled!')
            window.close()
        elif event == 'Submit':
            window.close()
        else:
            print('Error in input!')
            window.close()

        # The input data looks like a simple list 
        book = values[0]

        # Ask the user for a book they like
        # book = input(f'\nEnter a book you like: ')

        # Find the index of the book in the similarity dataframe
        book_index = similarity_df.index.get_loc(book)

        # Get the top 10 most similar books to the book
        top_10_bow = similarity_df.iloc[book_index].sort_values(ascending=False)[1:11]


        # Create a TfidfVectorizer object to transform the book tags into a Tf-idf representation
        tfidf = TfidfVectorizer()
        tfidf_matrix = tfidf.fit_transform(books['tag'])

        # Calculate the cosine similarity between the books
        cos_similarity_tfidf = cosine_similarity(tfidf_matrix)

        # Create a df with the cosine similarity scores
        cos_similarity_tfidf_df = pd.DataFrame(cos_similarity_tfidf, index=books['book_title'], columns=books['book_title'])

        # Find the index of the book in the similarity dataframe
        book_index = cos_similarity_tfidf_df.index.get_loc(book)

        # Get the top 10 most similar books to the book
        top_10_tfidf = cos_similarity_tfidf_df.iloc[book_index].sort_values(ascending=False)[1:11]

        # Print the top 10 most similar books to the book using the PySimpleGUI
        frame_layout = [[sg.Multiline("", size=(80, 20), autoscroll=True,
        reroute_stdout=True, reroute_stderr=True, key='-OUTPUT-')]]

        layout = [
            [sg.Frame(f"Top recommendations to {book}:", frame_layout)],
            [sg.Push(), sg.Button("Show results")],
        ]
        window = sg.Window("Book recommendations", layout, finalize=True)

        while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED:
                break
            elif event == "Show results":
                print(f'Top 10 similar (BoW) books to {book}:\n')
                print(top_10_bow)
                print(f'\n\nTop 10 similar (TF-IDF) books to {book}:\n')
                print(top_10_tfidf)

        window.close()