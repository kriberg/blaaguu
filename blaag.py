from flask import Flask, render_template, abort
from glob import glob
import subprocess
import shlex
from datetime import datetime
from markdown import markdown

app = Flask(__name__)

def get_posts():
    md_files = glob('../blaagposts/*.md')
    posts = []
    for f in md_files:
        filename = f.split('/')[-1]
        try:
            timestamp = datetime.fromtimestamp(int(subprocess.check_output(
                shlex.split('git log --pretty=format:%%ct --date=local --reverse -- %s' % filename),
                cwd='blaagposts')))
        except:
            timestamp = datetime.now()
        posts.append((timestamp, unslug(filename), filename.replace('.md', '')))
    posts.sort(reverse=True)
    return posts

def unslug(s):
    return s.replace('.md', '').replace('-', ' ').title()

@app.route('/')
def index():
    return render_template('index.html', posts=get_posts())

@app.route('/<post>')
def post(post):
    for entry in get_posts():
        if not post == entry[2]:
            continue
        with open('../blaagposts/%s.md' % entry[2]) as f:
            return render_template('post.html',
                    entry=entry,
                    post=markdown(f.read()))
    abort(404)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
