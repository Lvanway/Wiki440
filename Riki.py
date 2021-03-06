# -*- coding: utf-8 -*-
import os

from wiki import create_app

directory = os.getcwd()
app = create_app(directory)

# create initial history content dir
if not os.path.exists('./history/content/'):
    os.makedirs('./history/content/')

if not os.path.exists('./comment.txt'):
    open('./comment.txt', 'w').close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)