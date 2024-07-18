import os
import re
import tomllib
import pandas as pd
from pathlib import Path
from functools import partial
from dataclasses import dataclass
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective
from docutils import nodes
from typing import Optional
from typing import ClassVar
from sphinx.util import logging

logger = logging.getLogger(__name__)


TECH_STACK_FA_ICON_MAP = {
    'Azure': '<i class="fa-solid fa-cloud"></i>',
    'Azure AD': '<i class="fa-solid fa-address-book"></i>',
    'Bash': '<i class="fa-solid fa-terminal"></i>',
    'Celery': '<i class="fa-solid fa-sliders"></i>',
    'Crowdstrike': '<i class="fa-solid fa-database"></i>',
    'Dash': '<i class="fa-solid fa-chart-line"></i>',
    'Dask': '<i class="fa-solid fa-sitemap"></i>',
    'Docker': '<i class="fa-brands fa-docker"></i>',
    'Elasticsearch': '<i class="fa-brands fa-searchengin"></i>',
    'Energyworx': '<i class="fa-solid fa-lightbulb"></i>',
    'FastAPI': '<i class="fa-solid fa-microchip"></i>',
    'Flask': '<i class="fa-solid fa-microchip"></i>',
    'GCP': '<i class="fa-solid fa-cloud"></i>',
    'Git': '<i class="fa-brands fa-git-alt"></i>',
    'GoGS': '<i class="fa-solid fa-gear"></i>',
    'Groovy': '<i class="fa-solid fa-code"></i>',
    'KVM': '<i class="fa-solid fa-server"></i>',
    'Keras': '<i class="fa-solid fa-brain"></i>',
    'Latex': '<i class="fa-regular fa-file-lines"></i>',
    'Matplotlib': '<i class="fa-solid fa-brush"></i>',
    'Numpy': '<i class="fa-solid fa-list-ol"></i>',
    'OpenCV': '<i class="fa-solid fa-eye"></i>',
    'Pandas': '<i class="fa-solid fa-receipt"></i>',
    'PowerBI': '<i class="fa-solid fa-paint-roller"></i>',
    'Python': '<i class="fa-brands fa-python"></i>',
    'Pytorch': '<i class="fa-solid fa-fire"></i>',
    'R': '<i class="fa-brands fa-r-project"></i>',
    'RedHat': '<i class="fa-brands fa-redhat"></i>',
    'RShiny': '<i class="fa-solid fa-wand-magic-sparkles"></i>',
    'SQL': '<i class="fa-solid fa-person-digging"></i>',
    'Scipy': '<i class="fa-solid fa-magnifying-glass-chart"></i>',
    'Spark': '<i class="fa-solid fa-magnifying-glass-chart"></i>',
    'Sphinx': '<i class="fa-solid fa-book"></i>',
    'Splunk': '<i class="fa-solid fa-database"></i>',
    'Statsmodels': '<i class="fa-solid fa-brain"></i>',
    'TKinter': '<i class="fa-solid fa-table-columns"></i>',
    'VBA': '<i class="fa-solid fa-code"></i>',
    'Xarray': '<i class="fa-solid fa-layer-group"></i>',
}


def as_date(date_str: str) -> pd.Timestamp:
    end_of_time = (pd.Timestamp.today() + pd.Timedelta('1d')).isoformat()
    return pd.Timestamp(date_str.replace('Now', end_of_time))


def extract_from_toml(filepath: str, field: str) -> list[dict]:
    """Extracts specific field from ``.toml`` file"""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Filepath '{filepath}' does not exist")
    if not filepath.endswith('toml'):
        raise TypeError(f"Filepath '{filepath}' is not a TOML file")
    return tomllib.loads(Path(filepath).read_text(encoding='utf-8')).get(field, [])


def parse_meta(meta: dict[str, str]):
    """
    Convert RST meta values to Python objects
    """
    meta_good = {}
    for key, value in meta.items():
        key = key.lower()
        if value.lower() == "true":
            meta_good[key] = True
        elif value.lower() == "false":
            meta_good[key] = False
        elif "date" in key.lower():
            meta_good['date'] = pd.Timestamp(value).strftime("%d/%m/%Y")
        elif "," in value:
            meta_good[key] = list(map(str.strip, value.split(',')))
        else:
            meta_good[key] = value
    return meta_good


def get_meta_from_source(rst_source: str):
    """
    Extracts the meta info from ``.rst`` source file
    """
    attr_pattern = re.compile(r":([A-Za-z_-]+):\s*([\w_/ ,-]+)")
    return parse_meta(dict(attr_pattern.findall(rst_source)))


# Dataclasses -----------------------------------------------------------------
@dataclass
class ExperienceProject:
    description: str
    tech_stack: list[str]
    url: Optional[str] = ''
    lang: ClassVar[str] = 'english'

    def to_html(self, indent: int = 0):
        return '\n'.join((
            f'{" " * indent}<li class="cv-item-inner">',
            f'{" " * indent}  <a href="{self.url}">' if self.url else '',
            f'{" " * indent}  {self.description}',
            f'{" " * indent}  </a>' if self.url else '',
            self.to_html_tech_stack(indent+2),
            f'{" " * indent}</li>'
        ))

    def to_html_tech_stack(self, indent: int = 0):

        def tech_to_html(tech: str, indent: int = 0):
            return (
                f'{" " * indent}<span class="cv-tech-stack-tag">'
                f'{" " * indent}{TECH_STACK_FA_ICON_MAP.get(tech, "")}'
                f'{" " * indent}{tech}'
                f'{" " * indent}</span>'
            )

        if not self.tech_stack:
            return ''

        return '\n'.join((
            f'{" " * indent}<p class="cv-tech-stack">',
            '\n'.join(tech_to_html(tech, indent+2) for tech in self.tech_stack),
            f'{" " * indent}</p>'
        ))


@dataclass
class CVExperience:
    position: str
    employer: str
    start: str
    end: str
    description: Optional[str] = ''
    projects: list[ExperienceProject] = None
    lang: ClassVar[str] = 'english'

    def __post_init__(self):
        self.projects = self.projects or []

    def to_html(self, indent: int = 0):
        return '\n'.join((
            f'{" " * indent}<li class="cv-item">',
            f'{" " * indent}  <div class="cv-item-main">',
            self.to_html_title(indent+4),
            f'{" " * indent}    <span class="cv-when">{self.start} - {self.end}</span>',
            f'{" " * indent}  </div>',
            f'{" " * indent}  <div class="cv-item-info">',
            f'{" " * indent}  <p>{self.description}</p>' if self.description else '',
            self.to_html_projects(indent+2),
            f'{" " * indent}  </div>',
            f'{" " * indent}</li>'
        ))

    def to_html_title(self, indent: int = 0):
        ligature = 'at' if self.lang == 'english' else 'para'
        return (
            f'{" " * indent}<p class="cv-job">'
            f'<span class="cv-job-position">{self.position}</span>'
            f' {ligature} '
            f'<span class="cv-job-employer">{self.employer}</span>'
            f'{" " * indent}</p>'
        )

    def to_html_projects(self, indent: int = 0):
        if not self.projects:
            return ''
        return '\n'.join((
            f'{" " * indent}<ul class="cv-experience-projects">',
            '\n'.join(proj.to_html(indent+2) for proj in self.projects),
            f'{" " * indent}</ul>'
        ))


@dataclass
class CVEvent:
    title: str
    institution: str
    when: str
    url: Optional[str] = ''
    lang: ClassVar[str] = 'english'

    def to_html(self, indent: int = 0):
        return '\n'.join((
            f'{" " * indent}<li class="cv-item">',
            f'{" " * indent}  <div class="cv-item-main">',
            f'{" " * indent}    <a href="{self.url}">' if self.url else '',
            f'{" " * indent}    {self.title}',
            f'{" " * indent}    </a>' if self.url else '',
            f'{" " * indent}    <span class="cv-when">{self.when}</span>',
            f'{" " * indent}  </div>',
            f'{" " * indent}  <div class="cv-item-info">',
            f'{" " * indent}  <p>{self.institution}</p>',
            f'{" " * indent}  </div>',
            f'{" " * indent}</li>'
        ))


@dataclass
class CVSideProjectCollaborator:
    name: str
    url: Optional[str] = ''
    lang: ClassVar[str] = 'english'

    def __post_init__(self):
        if re.match(r'^(\w-.])+@(\w-+\.)+(\w){2,4}$', self.url):
            self.url = f'mailto:{self.url}'
        else:
            self.url = self.url

    def to_html(self, indent: int = 0):
        return '\n'.join((
            f'{" " * indent}<li class="cv-item-inner">',
            f'{" " * indent}  <a href="{self.url}">' if self.url else '',
            f'{" " * indent}  {self.name}',
            f'{" " * indent}  </a>' if self.url else '',
            f'{" " * indent}</li>'
        ))


@dataclass
class CVSideProject:
    title: str
    description: str
    url: Optional[str]
    collaborators: Optional[list[CVSideProjectCollaborator]] = None
    lang: ClassVar[str] = 'english'

    def __post_init__(self):
        self.collaborators = self.collaborators or []
        self.lang = self.lang or 'english'

    def to_html(self, indent: int = 0):
        return '\n'.join((
            f'{" " * indent}<li class="cv-item">',
            f'{" " * indent}  <div class="cv-item-main">',
            f'{" " * indent}    <a href="{self.url}">' if self.url else '',
            f'{" " * indent}    <p class="cv-side-project-title">{self.title}</p>',
            f'{" " * indent}    </a>' if self.url else '',
            f'{" " * indent}  </div>',
            f'{" " * indent}  <div class="cv-item-info">',
            f'{" " * indent}    <p class="cv-side-project-description">{self.description}</p>',
            self.to_html_collaborators(indent+2),
            f'{" " * indent}  </div>',
            f'{" " * indent}</li>',
        ))

    def to_html_collaborators(self, indent: int = 0):
        if not self.collaborators:
            return ''
        label = 'Collaborators' if self.lang == 'english' else 'Colaboradores'
        return '\n'.join((
            f'{" " * indent}<p class="cv-side-project-collaborators">{label}:</p>',
            f'{" " * indent}<ul class="cv-side-project-collaborators">',
            '\n'.join(coll.to_html(indent+2) for coll in self.collaborators),
            f'{" " * indent}</ul>'
        ))


@dataclass
class CVAptitude:
    name: str
    score: int
    lang: ClassVar[str] = 'english'

    def __post_init__(self):
        self.score = max(0, min(10, int(self.score)))

    def to_html(self):
        return (
            f'<li class="cv-aptitude">'
            f'<p>{self.name}</p>'
            '<div class="progress-bar">'
            f'<span class="progress" style="max-width:{self.score * 10}%;"></span>'
            '<span></span>'
            '</div>'
            '</li>'
        )


# Nodes -----------------------------------------------------------------------
class CVNode(nodes.Admonition, nodes.Element):

    def __init__(self, *args, lang: str = 'english', **kwargs):
        super(nodes.Admonition, self).__init__(*args, **kwargs)
        super(nodes.Element, self).__init__()
        self.lang = lang or 'english'


class CVAptitudes(CVNode):
    dataclass = CVAptitude

    @classmethod
    def process_items(cls, items: list[dict], reverse=True):
        processed_items = [cls.dataclass(x['name'], x['score']) for x in items]
        return sorted(processed_items, key=lambda x: x.score, reverse=reverse)


class CVSideProjects(CVNode):
    dataclass = CVSideProject

    @classmethod
    def process_items(cls, items: list[dict], reverse=True):
        processed_items = [
            cls.dataclass(
                x['title'],
                x['description'],
                x.get('url', ''),
                collaborators=[
                    CVSideProjectCollaborator(y['name'], y.get('url', ''))
                    for y in x.get('collaborators', [])
                ],
            ) for x in items
        ]
        return sorted(processed_items, key=lambda x: x.title, reverse=reverse)


class CVEvents(CVNode):
    dataclass = CVEvent

    @classmethod
    def process_items(cls, items: list[dict], reverse=True):
        processed_items = [
            cls.dataclass(
                x['title'],
                x['institution'],
                x['when'],
                x.get('url', ''),
            ) for x in items
        ]
        return sorted(
            processed_items,
            key=lambda x: (as_date(x.when), x.title),
            reverse=reverse
        )


class CVEducations(CVEvents):
    pass


class CVCertifications(CVEvents):
    pass


class CVExperiences(CVNode):
    dataclass = CVExperience

    @classmethod
    def process_items(cls, items: list[dict], reverse=True):
        processed_items = [
            cls.dataclass(
                x['position'],
                x['employer'],
                x['start'],
                x['end'],
                x.get('description', ''),
                projects=[
                    ExperienceProject(
                        y['description'],
                        y.get('tech-stack', ''),
                        y.get('url', '')
                    )
                    for y in x.get('projects', [])
                ],
            ) for x in items
        ]
        return sorted(
            processed_items,
            key=lambda x: (as_date(x.end), as_date(x.start), x.position),
            reverse=reverse
        )


# def visit_Posts_node(self, node):
#    self.visit_admonition(node)
#
# def depart_Posts_node(self, node):
#    self.depart_admonition(node)


# Directives ------------------------------------------------------------------
class CVTomlDirective(SphinxDirective):
    required_arguments = 1
    optional_arguments = 1
    has_content = False
    final_argument_whitespace = False
    option_spec = dict(
        fields=lambda x: map(str.strip, str.split(x, ',')),
        reverse=directives.flag,
    )

    node_class = None
    """Subclasses must set this to the appropriate admonition node class."""

    def run(self):
        if self.node_class is None:
            raise self.error('node_class is not defined. Cannot create node')
        cv_chunk_node = self.node_class(self.arguments[0])
        self.state.nested_parse(
            self.content, self.content_offset, cv_chunk_node
        )
        return [cv_chunk_node]


class CVChunkDirective(SphinxDirective):
    required_arguments = 1
    optional_arguments = 1
    has_content = False
    final_argument_whitespace = False
    option_spec = dict(
        reverse=directives.flag,
    )

    node_class = CVEvents
    """Subclasses must set this to the appropriate admonition node class."""

    def run(self):
        if self.node_class is None:
            raise self.error('node_class is not defined. Cannot create node')
        rst_source = (Path(self.env.srcdir) / f"{self.env.docname}.rst").read_text()
        meta = get_meta_from_source(rst_source)
        lang = meta.get('language', '')
        cv_chunk_node = self.node_class(self.arguments[0], lang=lang)
        self.state.nested_parse(
            self.content, self.content_offset, cv_chunk_node
        )
        return [cv_chunk_node]


class CVAptitudesDirective(CVChunkDirective):
    node_class = CVAptitudes


class CVSideProjectsDirective(CVChunkDirective):
    node_class = CVSideProjects


class CVExperiencesDirective(CVChunkDirective):
    node_class = CVExperiences


class CVEducationsDirective(CVChunkDirective):
    node_class = CVEducations


class CVCertificationsDirective(CVChunkDirective):
    node_class = CVCertifications


# Handlers --------------------------------------------------------------------
def create_cv_node_processor(
    node_class: type, node_name: str, css_class: str = ''
):

    css_class = css_class or f"cv-{node_name}"

    def process_nodes(app, doctree, fromdocname):
        for node in doctree.traverse(node_class):
            tomlpath = os.path.join(app.confdir, node.rawsource)
            toml_content = extract_from_toml(tomlpath, node_name)
            if not toml_content:
                logger.warning(f"{tomlpath} does not contain '{node_name}' section")
                continue
            node_class.dataclass.lang = node.lang
            instances = node_class.process_items(toml_content, reverse=True)
            output = f'<ul class={css_class}>'
            for instance in instances:
                output += instance.to_html()
            output += "</ul>"
            logger.info(f"Loaded {len(instances)} {node_name}(s) from {tomlpath}")
            node.replace_self(nodes.raw("", output, format="html"))

    return process_nodes
