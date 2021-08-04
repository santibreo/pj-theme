import os
import json
from dataclasses import dataclass
from docutils.parsers.rst import Directive, directives
#from sphinx.util.docutils import SphinxDirective
from docutils import nodes


###############################################################################
# Auxiliar Classes
###############################################################################
@dataclass(init=False)
class Aptitude:
    name: str
    score: int

    def __init__(self, name, score):
        # Name
        self.name = name
        # Score
        self.score = max(0, min(10, int(score)))

###############################################################################
# Node
###############################################################################
class Aptitudes(nodes.Admonition, nodes.Element):
    @staticmethod
    def get_aptitudes(apts_path, reverse=True): # Reverse True -> Newest first
        if not os.path.isfile(apts_path) or not apts_path.endswith('json'):
            raise ValueError(f"appts_path must be a json and not {apts_path}")
        apts = [
            Aptitude(x, y) for x, y in json.load(open(apts_path)).items()
        ]
        return sorted(apts, key=lambda x: x.score, reverse=reverse)

#def visit_Posts_node(self, node):
#    self.visit_admonition(node)
#
#def depart_Posts_node(self, node):
#    self.depart_admonition(node)
#

###############################################################################
# Directive
###############################################################################
class AptitudesDirective(Directive):
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = dict(
        opposite=directives.flag,
    )

    def run(self):
        #posts = self.get_posts(self.options["path"])
        appts_node = Aptitudes(self.arguments[0])
        self.state.nested_parse(self.content, self.content_offset,
                                appts_node)
        return [appts_node]


###############################################################################
# Handlers
###############################################################################
def process_aptitudes_nodes(app, doctree, fromdocname):
    for appts_node in doctree.traverse(Aptitudes):
        output = '<ul class="cv-aptitudes">'
        appts_path = os.path.join(app.confdir, appts_node.rawsource)
        appts = appts_node.get_aptitudes(appts_path)
        for appt in appts:
            # All together
            output += (
                f'<li class="cv-aptitude">'
                f'<p style="width:{appt.score * 10}%;">{appt.name}</p>'
                '<span></span>'
                '</li>'
            )
        output += "</ul>"
        appts_node.replace_self(nodes.raw("", output, format="html"))

