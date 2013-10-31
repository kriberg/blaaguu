from flask import Flask, render_template, abort
from datetime import datetime
from UserDict import UserDict
from markdown import markdown
from git import Repo
import json
import os

with open('secretkey.txt', 'r') as f:
    secretkey = f.read().strip()
with open('projects.json', 'r') as f:
    projects = json.loads(f.read())

class PostHandler(UserDict):
    repo = Repo('../blaagposts')
    def __init__(self):
        UserDict.__init__(self)
        self.fetch_posts()

    def parse_date(self, date):
        return datetime.strptime(date,
                "%a %b %d %H:%M:%S %Y")

    def fetch_posts(self):
        self.repo.git.pull()
        blobs = self.repo.heads.master.commit.tree.blobs
        posts = []
        for b in blobs:
            if not b.name.lower().endswith('.md'):
                continue
            dates = filter(lambda l: l.startswith('Date: '),
                    self.repo.git.log(b.name).splitlines())
            dates = [t[5:-5].strip() for t in dates]
            posted = self.parse_date(dates[-1])
            last_updated = self.parse_date(dates[0])
            post_data = {'title': self.unslug(b.name),
                    'slug': self.slug(b.name),
                    'posted': posted,
                    'last_updated': last_updated,
                    'text': markdown(b.data_stream.read())}
            posts.append((posted, post_data))
            self[self.slug(b.name)] = post_data
        self.posts = sorted(posts, key=lambda x: x[0])
        self.posts.reverse()

    def slug(self, s):
        return s.replace('.md','').replace(' ', '-').title()

    def unslug(self, s):
        return s.replace('.md', '').replace('-', ' ').title()


ph = PostHandler()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
            ph=ph,
            projects=projects)

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
