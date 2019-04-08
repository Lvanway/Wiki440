"""
    Routes
    ~~~~~~
"""
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from wiki.core import Processor
from wiki.web.forms import EditorForm
from wiki.web.forms import LoginForm
from wiki.web.forms import SearchForm
from wiki.web.forms import URLForm
from wiki.web.forms import ContactForm
from wiki.web import current_wiki
from wiki.web import current_users
from wiki.web.user import protect

from history.history import add_history
from history.history import get_history
from history.history import view_history
from history.history import revert_to_index
from history.history import move_history
from history.history import delete_history

from contacts.contacts import ContactManager

import os
import json


bp = Blueprint('wiki', __name__)


@bp.route('/')
@protect
def home():
    page = current_wiki.get('home')
    if page:
        return display('home')
    return render_template('home.html')


@bp.route('/index/')
@protect
def index():
    pages = current_wiki.index()
    return render_template('index.html', pages=pages)


@bp.route('/<path:url>/')
@protect
def display(url):
    page = current_wiki.get_or_404(url)
    return render_template('page.html', page=page)


@bp.route('/comment/')
@protect
def comment():
    file = open("comment.txt", "r")
    lines = file.readlines()
    file.close()
    return render_template("comment.html", lines=lines)


@bp.route('/result/', methods=['POST'])
@protect
def result():
    article = request.form["article"]
    name = request.form["name"]
    file = open("comment.txt", "a")
    file.write(article + "," + name + "\n")
    file.close()
    return render_template("result.html", article=article, name=name)


@bp.route('/autocomplete/<query>/', methods=['GET'])
@protect
def autocomplete(query):
    result = "";
    if(current_wiki.search(query, 1)):
        url = current_wiki.search(query, 1)[0].url
        name = current_wiki.search(query, 1)[0].title
        result = "<a href='/" + url + "'>" + name + "</a>"

    return result


@bp.route('/<path:url>/history/', methods=['GET'])
@protect
def history(url):
    page = current_wiki.get_or_404(url)
    if not os.path.exists('./history/content/' + url + '.json'):
        add_history(url, 'WikiBot', 'History created!', page.html, page.content, 'edit')
    changes = get_history(url)
    return render_template('history.html', page=page, changes=changes)


@bp.route('/<path:url>/history/view/<int:index>/')
@protect
def view(url, index):
    index = str(index)
    html = view_history(url, index)
    return html


@bp.route('/<path:url>/history/revert/<int:index>')
@protect
def revert(url, index):
    index = str(index)
    data = revert_to_index(url, index)
    add_history(url, 'WikiBot', 'Reverted to index: ' + index, data[0], data[1], 'revert')
    return redirect(url_for('wiki.display', url=url))


@bp.route('/contactform/', methods=['GET', 'POST'])
def contact_form():
    form = ContactForm()
    if form.validate_on_submit():
        manager = ContactManager('user')
        manager.add_contact(form.first_name.data, form.last_name.data, form.email.data)
        return render_template('home.html')
    return render_template('contactform.html', form=form)


@bp.route('/contactdisplay/')
def display_contacts():
    with open('./user/contacts.json', 'r') as json_file:
        contacts = json.load(json_file)
        return render_template('contactdisplay.html', contacts=contacts)


@bp.route('/admin/', methods=['GET', 'POST'])
def admin():
    form = LoginForm()
    flash('Please log in to view this page', 'warning')
    with open('./user/users.json', 'r') as json_file:
        users = json.load(json_file)
        if form.validate_on_submit():
            user = current_users.get_user(form.name.data)
            if user.get("roles")[0] == 'admin':
                return render_template('admin.html', permission=True, users=users)
            else:
                return render_template('admin.html', permission=False, users=users)
        return render_template('login.html', form=form)


@bp.route('/changerole/<string:name>')
def change_role(name):
    user = current_users.get_user(name)
    if user.get("roles")[0] == 'admin':
        user.set("roles", ['user'])
        user.save()
    else:
        user.set("roles", ['admin'])
        user.save()
    return redirect(url_for('wiki.admin'))


@bp.route('/create/', methods=['GET', 'POST'])
@protect
def create():
    form = URLForm()
    if form.validate_on_submit():
        return redirect(url_for(
            'wiki.edit', url=form.clean_url(form.url.data)))
    return render_template('create.html', form=form)


@bp.route('/edit/<path:url>/', methods=['GET', 'POST'])
@protect
def edit(url):
    page = current_wiki.get(url)
    form = EditorForm(obj=page)
    if form.validate_on_submit():
        if not page:
            page = current_wiki.get_bare(url)

            # added
            add_history(url, 'WikiBot', 'Page created!', '<p>No content to show!</p>',
                        'title: \ntags: \n\nNo content to show!', 'create')

        # added
        if not os.path.exists('./history/content/' + url + '.json'):
            add_history(url, 'WikiBot', 'History created!', page.hmtl, page.content, 'edit')

        form.populate_obj(page)
        page.save()
        flash('"%s" was saved.' % page.title, 'success')

        # added
        add_history(url, form.author._value(), form.message._value(), page.html, page.content, 'edit')

        return redirect(url_for('wiki.display', url=url))
    return render_template('editor.html', form=form, page=page)


@bp.route('/preview/', methods=['POST'])
@protect
def preview():
    data = {}
    processor = Processor(request.form['body'])
    data['html'], data['body'], data['meta'] = processor.process()
    print(data['html'])
    return data['html']


@bp.route('/move/<path:url>/', methods=['GET', 'POST'])
@protect
def move(url):
    page = current_wiki.get_or_404(url)
    form = URLForm(obj=page)
    if form.validate_on_submit():
        newurl = form.url.data
        current_wiki.move(url, newurl)
        move_history(url, newurl)
        add_history(newurl, 'WikiBot', 'Moved page to URL: ' + newurl, page.html, page.content, 'move')
        return redirect(url_for('wiki.display', url=newurl))
    return render_template('move.html', form=form, page=page)


@bp.route('/delete/<path:url>/')
@protect
def delete(url):
    page = current_wiki.get_or_404(url)
    current_wiki.delete(url)
    delete_history(url)
    flash('Page "%s" was deleted.' % page.title, 'success')
    return redirect(url_for('wiki.home'))


@bp.route('/tags/')
@protect
def tags():
    tags = current_wiki.get_tags()
    return render_template('tags.html', tags=tags)


@bp.route('/tag/<string:name>/')
@protect
def tag(name):
    tagged = current_wiki.index_by_tag(name)
    return render_template('tag.html', pages=tagged, tag=name)


@bp.route('/search/', methods=['GET', 'POST'])
@protect
def search():
    form = SearchForm()
    if form.validate_on_submit():
        results = current_wiki.search(form.term.data, form.ignore_case.data)
        return render_template('search.html', form=form,
                               results=results, search=form.term.data)
    return render_template('search.html', form=form, search=None)


@bp.route('/user/login/', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = current_users.get_user(form.name.data)
        login_user(user)
        user.set('authenticated', True)
        flash('Login successful.', 'success')
        return redirect(request.args.get("next") or url_for('wiki.index'))
    return render_template('login.html', form=form)


@bp.route('/user/logout/')
@login_required
def user_logout():
    current_user.set('authenticated', False)
    logout_user()
    flash('Logout successful.', 'success')
    return redirect(url_for('wiki.index'))


@bp.route('/user/')
def user_index():
    pass


@bp.route('/user/create/')
def user_create():
    pass


@bp.route('/user/<int:user_id>/')
def user_admin(user_id):
    pass


@bp.route('/user/delete/<int:user_id>/')
def user_delete(user_id):
    pass


"""
    Error Handlers
    ~~~~~~~~~~~~~~
"""


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

