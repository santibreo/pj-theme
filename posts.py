import os
import re
from datetime import datetime
from dataclasses import dataclass
from docutils.parsers.rst import Directive, directives
#from sphinx.util.docutils import SphinxDirective
from docutils import nodes


###############################################################################
# Auxiliar Classes
###############################################################################
@dataclass(init=False)
class Post:
    path: str
    title: str = ""
    date: datetime = datetime(2000,1,1)
    group: str = ""
    meta = {}
    title_patttern: str = r"^[#=]+$"

    def __init__(self, post_path):
        # Path
        self.path = post_path
        # Date
        timestamp = os.stat(post_path).st_mtime
        self.date = datetime.fromtimestamp(timestamp)
        # Set title and meta
        self.parse_post_header()

    def parse_meta_values(self, key, value):
        """
        Parser for meta values
        """
        if value.lower() == "true":
            self.meta[key.lower()] = True
        elif value.lower() == "false":
            self.meta[key.lower()] = False
        elif "date" in key.lower():
            value_right = value.replace("-", "/")
            self.date = datetime.strptime(value_right, "%d/%m/%Y")
        else:
            self.meta[key.lower()] = value

    def parse_post_header(self):
        """
        Extracts the title from any .rst document
        """
        attr_pattern = r":([A-Za-z_-]+):\s*([A-Za-z0-9-/]+)"
        with open(self.path) as fff:
            lines = iter(fff.readlines())
            try:
                while not self.title:
                    line = next(lines).strip()
                    if re.match(self.title_patttern, line):
                        self.title = next(lines)
                    if meta_attr:=re.findall(attr_pattern, line):
                        self.parse_meta_values(*meta_attr[0])
            except StopIteration:
                raise TypeError(f"File {self.path} does not have a title")


###############################################################################
# Node
###############################################################################
class Posts(nodes.Admonition, nodes.Element):
    @staticmethod
    def get_posts(posts_path, reverse=True): # Reverse True -> Newest first
        posts = []
        main_dir = os.path.basename(posts_path)
        for parent_path, _, files in os.walk(posts_path):
            if (parent := os.path.basename(parent_path)) == main_dir:
                parent = ""
            for file in files:
                if not file.lower().endswith(".rst"):
                    continue
                file_path = os.path.join(parent_path, file)
                post = Post(file_path)
                # Group
                post.group = parent
                # Printing
                #print("=" * 50)
                #print(post.title)
                #print(post.date)
                #print(post.meta)
                #print("=" * 50)
                if not post.meta.get("draft"):
                    posts.append(post)
        return sorted(posts, key=lambda x: x.date.toordinal(), reverse=reverse)

def visit_Posts_node(self, node):
    self.visit_admonition(node)

def depart_Posts_node(self, node):
    self.depart_admonition(node)


###############################################################################
# Directive
###############################################################################
class PostsDirective(Directive):
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = dict(
        opposite=directives.flag,
    )

    def run(self):
        #posts = self.get_posts(self.options["path"])
        posts_node = Posts(self.arguments[0])
        self.state.nested_parse(self.content, self.content_offset,
                                posts_node)
        return [posts_node]


###############################################################################
# Handlers
###############################################################################
def process_posts_nodes(app, doctree, fromdocname):
    for posts_node in doctree.traverse(Posts):
        output = '<ul class="posts-list">'
        posts_path = os.path.join(app.confdir, posts_node.rawsource)
        posts = posts_node.get_posts(
            posts_path,
        )
        for post in posts:
            if not post.title:
                continue
            # Post tag + title
            post_id = ''
            if post.group:
                post_id = f'<span class="post-group">{post.group}</span>'
            post_id += f'<span class="post-title">{post.title}</span>'
            # Post date
            post_date = ('<span class="post-date">'
                         f'{post.date.strftime("%d/%m/%Y")}</span>')
            # Post link
            post_link = app.project.path2doc(post.path) + ".html"
            # All together
            output += (f'<li><a href="{post_link}">{post_id}{post_date}</a>'
                       '</li>')
        output += "</ul>"
        posts_node.replace_self(nodes.raw("", output, format="html"))

