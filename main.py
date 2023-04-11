import PySimpleGUI as sg
from enum import Enum
from books import Book
from movies import Movie


class Type(Enum):
    BOOKS = 1
    MOVIES = 2

def main():

    selectedType = Type.BOOKS

    layout = [[sg.Text('Choose what you want to search for!')],
              [sg.Checkbox('Books', default = True, key=('-CHECKBOX-', 1), metadata=True, enable_events=True)],
              [sg.Checkbox('Movies', default = False, key=('-CHECKBOX-', 2), metadata=False, enable_events=True)],
              [sg.Button('Go'), sg.Button('Exit')]]

    window = sg.Window('Checkboxes', layout, font="_ 14")
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        # if a checkbox is clicked, flip the vale and the image
        if event[0] in ('-CHECKBOX-', '-TEXT-'):
            index = event[1]
            cbox_key = ('-CHECKBOX-', index)
            # print(cbox_key)
            value = True
            window[cbox_key].metadata = value
            window[cbox_key].update(value)
            if index == 1:
                cbox_key2 = ('-CHECKBOX-', 2)
                selectedType = Type.BOOKS
                window[cbox_key2].metadata = not value
                window[cbox_key2].update(not value)
            elif index == 2:
                cbox_key1 = ('-CHECKBOX-', 1)
                selectedType = Type.MOVIES
                window[cbox_key1].metadata = not value
                window[cbox_key1].update(not value)

        if event == 'Go':
            print(selectedType)
            window.close()
            if selectedType == Type.BOOKS:
                Book.recommend_book()
            elif selectedType == Type.MOVIES:
                Movie.recommend_movie()
            else:
                print('Error')

    



if __name__ == '__main__':
    main()



