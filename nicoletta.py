#!/usr/bin/env python
# Stupidly minimalistic static site generator

from ast import literal_eval
import codecs
from collections import namedtuple
from datetime import datetime
from glob import glob
import os
from string import Template
import sys

from markdown import markdown
from yaml import load

def parse_post(path):
    with codecs.open(path, "r", "utf8") as in_file:
        data, text = in_file.read().split('\n\n', 1)
        meta = load(data)
        meta['text'] = text
        meta['link'] = os.path.splitext(path[6:])[0]+'.html'
        return namedtuple('Post', meta)(**meta)


def main():
    # Convention over configuration:
    # * posts are all in posts/* (recursive)
    #   and we keep the folder structure, and everything is markdown
    # * templates are all in templates/*.tmpl

    # Data to be used in all templates:
    tpl_data = load(codecs.open('conf').read())
    # Templates
    templates = {}
    for tpl in glob(os.path.join('templates', '*.tmpl')):
        templates[os.path.basename(tpl)] = Template(codecs.open(tpl, 'r', 'utf-8').read())

    def render(template, *context, **extra):
        return templates['page.tmpl'].safe_substitute(*context, **extra)

    def render_post(post):
        return templates['post.tmpl'].safe_substitute(post.__dict__, text=markdown(post.text))

    posts = []
    for root, dirs, files in os.walk('posts'):
        for src in [os.path.join(root, f) for f in files]:
            posts.append(parse_post(src))
            dest = os.path.splitext(os.path.join('output', src[6:]))[0]+'.html'
            with codecs.open(dest, "w+", "utf8") as outf:
                outf.write(render('page.tmpl', tpl_data, content = render_post(posts[-1])))

    # And now the index page:
    posts.sort(key=lambda item:item.date, reverse=True)
    with codecs.open(os.path.join('output', 'index.html'), 'wb+', 'utf-8') as outf:
        # Because we are using a crap template system, we nest things a bit
        outf.write(render('page.tmpl', tpl_data,
            content = '<hr>'.join(render_post(post) for post in posts[:10])))

if __name__ == '__main__':
    main()
    if 'auto' in sys.argv:
        sys.argv.pop(sys.argv.index('auto'))
        os.system('livereload '+ ' '.join(sys.argv[1:])+' output')
