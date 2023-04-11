import pandas as pd
import PySimpleGUI as sg
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

class Movie:

    def recommend_movie():

        # Load the movies.csv into a Pandas df
        movies = pd.read_csv('.\\ml-25m\\movies.csv')
        movies = movies.head(25000)

        # Load the genome-tags.csv and genome-scores.csv in to Pandas dataframes
        genome_tags = pd.read_csv('.\\ml-25m\\genome-tags.csv')
        genome_scores = pd.read_csv('.\\ml-25m\\genome-scores.csv')

        # Merge the genome_scores df with the genome_tags df to get the relevance score for each tag
        genome_merged = genome_scores.merge(genome_tags, on='tagId', how='left')

        # Filter the genome_merged df to only include the tags with relevance > 0.5 for each movie
        top_tags = genome_merged[genome_merged['relevance'] > 0.5]
        top_tags.reset_index(drop=True, inplace=True)

        # Group the 'top_tags' df by 'movieId' and join the 'tag' values in the 'tag' column separated by a comma
        grouped_tags = top_tags.groupby('movieId')['tag'].apply(lambda x: ', '.join(x)).reset_index()

        # Merge the 'movies' df with the 'grouped_tags' df
        final_df = movies.merge(grouped_tags, on='movieId', how='left')

        # Select only the desired columns in the final dataframe
        final_df = final_df[['movieId', 'title', 'genres', 'tag']]

        # Some movies don't have a tag so let's add genres of the movie to tag
        def add_genres_to_tag(row):
            if pd.isnull(row['tag']):
                return row['genres'].replace("|", ",")
            else:
                return row['tag'] + "," + row['genres'].replace("|", ",")
            
        final_df['tag'] = final_df.apply(lambda row: add_genres_to_tag(row), axis=1)

        # Extract the movie titles and tags into separate lists
        titles = final_df['title'].tolist()
        tags = final_df['tag'].str.strip().str.split(",").tolist()


        ###USING BAG OF WORDS APPROACH WITH GENOME TAGS AND SCORES
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
        cos_similarity = cosine_similarity(tag_df)

        # Create a dataframe with the cosine similarity scores
        similarity_df = pd.DataFrame(cos_similarity, index=tag_df.index, columns=tag_df.index)

        print(movies[movies['title'].str.contains('Inception')])
        
        layout = [
            [sg.Text('Please enter your favorite movie!')],
            [sg.Text('Name of the movie:', size =(15, 1)), sg.InputText()],
            [sg.Submit(), sg.Cancel()]
        ]
        
        window = sg.Window('Movie recommendations', layout)
        event, value = window.read()
        if event == 'Cancel' or sg.WINDOW_CLOSED:
            value = 'NaN'
            print('The action was cancelled!')
            window.close()
        elif event == 'Submit':
            window.close()
        else:
            print('Error in input!')
            window.close()
        

        # Ask the user for a movie they like
        # movie = input('Enter a movie you like: ')
        movie = value[0]

        # Find the index of the movie in the similarity dataframe
        movie_index = similarity_df.index.get_loc(movie)

        # Get the top 10 most similar movies to the movie
        top_10 = similarity_df.iloc[movie_index].sort_values(ascending=False)[1:11]

        # Print the top 10 most similar movies to the movie using the PySimpleGUI
        frame_layout = [[sg.Multiline("", size=(80, 20), autoscroll=True,
        reroute_stdout=True, reroute_stderr=True, key='-OUTPUT-')]]

        layout = [
            [sg.Frame(f"Top recommendations to {movie}:", frame_layout)],
            [sg.Push(), sg.Button("Show results")],
        ]
        window = sg.Window("Movie recommendations", layout, finalize=True)

        while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED:
                break
            elif event == "Show results":
                print(f'Top 10 similar movies to {movie}:\n')
                print(top_10)


        window.close()