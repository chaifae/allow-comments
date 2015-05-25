import os
import urllib

from google.appengine.ext import ndb

import jinja2
import webapp2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


DEFAULT_COMMENT_SECTION = 'comments_default'

def comments_key(comment_section_name=DEFAULT_COMMENT_SECTION):
    return ndb.Key('Comments Section', comment_section_name)

class Comment(ndb.Model):
    author = ndb.StringProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(Handler):
    def get(self):
        self.render("main.html")

class NotesHandler(Handler):
    def get(self, note):
        error = self.request.get('error')
        note_file = note + ".html"
        arguments = {}
        arguments['note'] = note
        arguments['comment_section_name'] = note
        arguments['error'] = error
        arguments['comments'] = self.get_comments(note)
        self.render(note_file, **arguments)

    def get_comments(self, note):
        return Comment.query(ancestor = comments_key(note)).order(-Comment.date)

    def post(self, note):
        content = self.request.get('content')
        author = self.request.get('author')

        error = ""
        if content == "" or content == None:
            error += "1"
        if author == "" or author == None:
            error += "2"
# The error will display in the url, 1 for no content, 2 for no author,
# and 12 for an empty comment. The template grabs the error code and
# displays a different message for the user based on the code.
        if error != "":
            self.redirect('./' + note + "?error=" + error + "#error")
            return

        comment = Comment(parent=comments_key(note))

        if type(content) != unicode:
            content = unicode(content, 'utf-8')

        comment.content = content
        comment.author = author
        comment.put()

        self.redirect('./' + note)



app = webapp2.WSGIApplication([('/', MainPage),
                               webapp2.Route(r'/<note>', handler=NotesHandler)
                               ],
                              debug=True)