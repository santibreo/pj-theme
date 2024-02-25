import os
from distutils.dir_util import copy_tree
from .posts import (
    Posts,
    PostsDirective,
    process_posts_nodes,
    visit_Posts_node,
    depart_Posts_node
)
from .cv import (
    CVExperiencesDirective,
    CVEducationsDirective,
    CVCertificationsDirective,
    CVSideProjectsDirective,
    CVAptitudesDirective,
    create_cv_node_processor,
)

__version_info__ = (1, 0, 3)
__version__ = ".".join(map(str, __version_info__))


LANGUAGE_FLAG_MAPPING = {
    "spanish": '🇪🇸',
    "español": '🇪🇸',
    "es": '🇪🇸',
    "english": '🇬🇧',
    "inglés": '🇬🇧',
    "en": '🇬🇧',
}


LANGUAGE_FILE_END_MAPPING = {
    "spanish": '-es',
    "español": '-es',
    "es": '-es',
    "english": '',
    "inglés": '',
    "en": '',
}


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
    context["language_flag_mapping"] = LANGUAGE_FLAG_MAPPING
    context["language_file_end_mapping"] = LANGUAGE_FILE_END_MAPPING


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
        app.add_html_theme("sphinx_pj_theme", theme_path)
    app.connect("html-page-context", update_context)
    # Posts Nodes
    app.add_node(
        Posts,
        html=(visit_Posts_node, depart_Posts_node),
    )
    app.add_directive('posts', PostsDirective, override=True)
    app.connect("doctree-resolved", process_posts_nodes)
    # CV Nodes
    for (class_name, directive_str, directive) in [
        ("experience", "cv-experiences", CVExperiencesDirective),
        ("education", "cv-educations", CVEducationsDirective),
        ("certification", "cv-certifications", CVCertificationsDirective),
        ("side-project", "cv-side-projects", CVSideProjectsDirective),
        ("aptitude", "cv-aptitudes", CVAptitudesDirective),
    ]:
        node_class = directive.node_class
        app.add_node(
            node_class,
            html=(visit_Posts_node, depart_Posts_node),
        )
        app.add_directive(directive_str, directive, override=True)
        process_func = create_cv_node_processor(node_class, class_name, directive_str)
        app.connect("doctree-resolved", process_func)

    # Copy static files
    app.connect('builder-inited', copy_custom_files)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True
    }
