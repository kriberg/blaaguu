from flask import Flask, render_template, abort
from datetime import datetime
from UserDict import UserDict
from markdown import markdown
from git import Repo
import os

with open('secretkey.txt', 'r') as f:
    secretkey = f.read().strip()

class PostHandler(UserDict):
    def __init__(self):
        UserDict.__init__(self)
        self.repo = Repo('../blaagposts')
        self.fetch_posts()

    def fetch_posts(self):
        self.repo.git.pull()
        blobs = self.repo.heads.master.commit.tree.blobs
        for b in blobs:
            if not b.name.lower().endswith('.md'):
                continue
            self[self.slug(b.name)] = (self.unslug(b.name),
                    markdown(b.data_stream.read()))

    def slug(self, s):
        return s.replace('.md','').replace(' ', '-').title()

    def unslug(self, s):
        return s.replace('.md', '').replace('-', ' ').title()


ph = PostHandler()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', ph=ph)

@app.route('/{0}'.format(secretkey))
def reload():
    with open('reload-blaag', 'a') as f:
        os.utime(f.name, None)
    return 'reloaded'

@app.route('/<post>')
def post(post):
    if not post in ph:
        abort(404)
    return render_template('post.html',
            post=ph[post])

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
