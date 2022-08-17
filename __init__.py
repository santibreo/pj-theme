import os
from distutils.dir_util import copy_tree
from sphinx_pjnotes_theme.posts import (
    Posts,
    PostsDirective,
    process_posts_nodes,
    visit_Posts_node,
    depart_Posts_node
)
from sphinx_pjnotes_theme.aptitudes import (
    Aptitudes,
    AptitudesDirective,
    process_aptitudes_nodes
)

__version_info__ = (1, 0, 0)
__version__ = ".".join(map(str, __version_info__))


def get_path():
    """
    Shortcut for users whose theme is next to their conf.py.
    """
    # Theme directory is defined as our parent directory
    return os.path.abspath(os.path.dirname(__file__))


def update_context(app, pagename, templatename, context, doctree):
    """
    Includes `pjnotes_version` in the context
    """
    context["pjnotes_version"] = __version__


def copy_custom_files(app, exc=None):
    if app.builder.format == 'html' and not exc:
        html_staticdir = os.path.join(app.builder.outdir, '_static')
        source_staticdir = os.path.join(app.builder.srcdir, '_static')
        pjno_staticdir = os.path.join(get_path(), "_static")
        copy_tree(pjno_staticdir, html_staticdir)
        copy_tree(source_staticdir, html_staticdir)

def setup(app):
    # add_html_theme is new in Sphinx 1.6+
    if hasattr(app, "add_html_theme"):
        theme_path = os.path.abspath(os.path.dirname(__file__))
        app.add_html_theme("pjnotes_theme", theme_path)
    # Posts Nodes
    app.add_node(
        Posts,
        html=(visit_Posts_node, depart_Posts_node),
    )
    app.add_directive('posts', PostsDirective, override=True)
    # Aptitudes Nodes
    app.add_node(
        Aptitudes,
        html=(visit_Posts_node, depart_Posts_node),
    )
    app.add_directive('aptitudes', AptitudesDirective, override=True)
    app.connect("html-page-context", update_context)
    app.connect("doctree-resolved", process_posts_nodes)
    app.connect("doctree-resolved", process_aptitudes_nodes)
    app.connect('builder-inited', copy_custom_files)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True
    }
