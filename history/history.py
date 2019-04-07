import os
from config import CONTENT_DIR
from datetime import datetime
import json
from flask import flash


def add_history(url, author, message, html, markdown, action):
    # sanitize inputs
    author = str(author)
    message = str(message)
    html = str(html)
    markdown = str(markdown)
    action = str(action)

    new_history = False

    if not os.path.exists('./history/content/' + url + '.json'):
        new_history = True
        with open('./history/content/' + url + '.json', 'w') as json_file:
            json_file.write('{}')
            json_file.close()

    with open('./history/content/' + url + '.json', 'r+') as json_file:
        history = json.load(json_file)

        # increment primary key
        key = 0
        for k in history.keys():
            if int(k) > key:
                key = int(k)
        key = key + 1

        # only add history of edit changed the file
        if new_history:
            history[str(key)] = {
                'author': author,
                'datetime': datetime.now().strftime('%m/%d/%Y %H:%M:%S'),
                'message': message,
                'html': html,
                'markdown': markdown,
                'action': action
            }

            json_file.seek(0)
            json_file.truncate(0)
            json.dump(history, json_file, indent=4, separators=[',', ': '])

        elif markdown == history[str(key-1)]["markdown"] and action == 'revert':
            flash('Cannot revert back to an identical version!', 'failure')

        elif markdown == history[str(key-1)]["markdown"] and action == 'edit':
            flash('Edit was identical so history was not updated!', 'failure')

        else:

            history[str(key)] = {
                'author': author,
                'datetime': datetime.now().strftime('%m/%d/%Y %H:%M:%S'),
                'message': message,
                'html': html,
                'markdown': markdown,
                'action': action
            }

            json_file.seek(0)
            json_file.truncate(0)
            json.dump(history, json_file, indent=4, separators=[',', ': '])


def get_history(url):
    with open('./history/content/' + url + '.json', 'r') as json_file:
        return json.load(json_file)


def view_history(url, index):
    with open('./history/content/' + url + '.json', 'r') as json_file:
        history = json.load(json_file)
        return history[index]["html"]


def revert_to_index(url, index):
    with open('./history/content/' + url + '.json', 'r') as json_file:
        history = json.load(json_file)
        with open(CONTENT_DIR + url + '.md', 'r+') as md_file:
            md_file.seek(0)
            md_file.truncate(0)
            md_file.write(history[index]["markdown"])
        return history[index]["html"], history[index]["markdown"]


def move_history(oldurl, newurl):
    if os.path.exists('./history/content/' + oldurl + '.json'):
        os.rename('./history/content/' + oldurl + '.json', './history/content/' + newurl + '.json')


def delete_history(url):
    if os.path.exists('./history/content/' + url + '.json'):
        os.remove('./history/content/' + url + '.json')
