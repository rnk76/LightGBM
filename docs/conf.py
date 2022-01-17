#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# LightGBM documentation build configuration file, created by
# sphinx-quickstart on Thu May  4 14:30:58 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute.
"""Sphinx configuration file."""
import datetime
import os
import sys
from pathlib import Path
from re import compile
from shutil import copytree
from subprocess import PIPE, Popen
from typing import Any, List

import sphinx
from docutils.nodes import reference
from docutils.parsers.rst import Directive
from docutils.transforms import Transform
from sphinx.application import Sphinx
from sphinx.errors import VersionRequirementError

CURR_PATH = Path(__file__).absolute().parent
LIB_PATH = CURR_PATH.parent / 'python-package'
sys.path.insert(0, str(LIB_PATH))

INTERNAL_REF_REGEX = compile(r"(?P<url>\.\/.+)(?P<extension>\.rst)(?P<anchor>$|#)")


class InternalRefTransform(Transform):
    """Replaces '.rst' with '.html' in all internal links like './[Something].rst[#anchor]'."""

    default_priority = 210
    """Numerical priority of this transform, 0 through 999."""

    def apply(self, **kwargs: Any) -> None:
        """Apply the transform to the document tree."""
        for section in self.document.traverse(reference):
            if section.get("refuri") is not None:
                section["refuri"] = INTERNAL_REF_REGEX.sub(r"\g<url>.html\g<anchor>", section["refuri"])


class IgnoredDirective(Directive):
    """Stub for unknown directives."""

    has_content = True

    def run(self) -> List:
        """Do nothing."""
        return []


# -- General configuration ------------------------------------------------

os.environ['LIGHTGBM_BUILD_DOC'] = '1'
C_API = os.environ.get('C_API', '').lower().strip() != 'no'
RTD = bool(os.environ.get('READTHEDOCS', ''))

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = '2.1.0'  # Due to sphinx.ext.napoleon, autodoc_typehints
if needs_sphinx > sphinx.__version__:
    message = f'This project needs at least Sphinx v{needs_sphinx}'
    raise VersionRequirementError(message)

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

autodoc_default_flags = ['members', 'inherited-members', 'show-inheritance']
autodoc_default_options = {
    "members": True,
    "inherited-members": True,
    "show-inheritance": True,
}
# mock out modules
autodoc_mock_imports = [
    'dask',
    'dask.distributed',
    'datatable',
    'graphviz',
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'scipy.sparse',
    'sklearn'
]
# hide type hints in API docs
autodoc_typehints = "none"

# Generate autosummary pages. Output should be set with: `:toctree: pythonapi/`
autosummary_generate = ['Python-API.rst']

# Only the class' docstring is inserted.
autoclass_content = 'class'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'LightGBM'
copyright = f'{datetime.datetime.now().year}, Microsoft Corporation'
author = 'Microsoft Corporation'

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = str(CURR_PATH / 'logo' / 'LightGBM_logo_grey_text.svg')

# The name of an image file (relative to this directory) to use as a favicon of
# the docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = str(CURR_PATH / '_static' / 'images' / 'favicon.ico')

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
# The short X.Y version.
version = (CURR_PATH.parent / 'VERSION.txt').read_text(encoding='utf-8').strip().replace('rc', '-rc')
# The full version, including alpha/beta/rc tags.
release = version

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'default'

# -- Configuration for C API docs generation ------------------------------

if C_API:
    extensions.extend([
        'breathe',
    ])
    breathe_projects = {
        "LightGBM": str(CURR_PATH / 'doxyoutput' / 'xml')
    }
    breathe_default_project = "LightGBM"
    breathe_domain_by_extension = {
        "h": "c",
    }
    breathe_show_define_initializer = True
    c_id_attributes = ['LIGHTGBM_C_EXPORT']

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    'includehidden': False,
    'logo_only': True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'LightGBMdoc'

# -- Options for LaTeX output ---------------------------------------------

# The name of an image file (relative to this directory) to place at the top of
# the title page.
latex_logo = str(CURR_PATH / 'logo' / 'LightGBM_logo_black_text_small.png')


def generate_doxygen_xml(app: Sphinx) -> None:
    """Generate XML documentation for C API by Doxygen.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        The application object representing the Sphinx process.
    """
    doxygen_args = [
        f"INPUT={CURR_PATH.parent / 'include' / 'LightGBM' / 'c_api.h'}",
        f"OUTPUT_DIRECTORY={CURR_PATH / 'doxyoutput'}",
        "GENERATE_HTML=NO",
        "GENERATE_LATEX=NO",
        "GENERATE_XML=YES",
        "XML_OUTPUT=xml",
        "XML_PROGRAMLISTING=YES",
        r'ALIASES="rst=\verbatim embed:rst:leading-asterisk"',
        r'ALIASES+="endrst=\endverbatim"',
        "ENABLE_PREPROCESSING=YES",
        "MACRO_EXPANSION=YES",
        "EXPAND_ONLY_PREDEF=NO",
        "SKIP_FUNCTION_MACROS=NO",
        "PREDEFINED=__cplusplus",
        "SORT_BRIEF_DOCS=YES",
        "WARN_AS_ERROR=YES",
    ]
    doxygen_input = '\n'.join(doxygen_args)
    doxygen_input = bytes(doxygen_input, "utf-8")
    (CURR_PATH / 'doxyoutput').mkdir(parents=True, exist_ok=True)
    try:
        # Warning! The following code can cause buffer overflows on RTD.
        # Consider suppressing output completely if RTD project silently fails.
        # Refer to https://github.com/svenevs/exhale
        # /blob/fe7644829057af622e467bb529db6c03a830da99/exhale/deploy.py#L99-L111
        process = Popen(["doxygen", "-"],
                        stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate(doxygen_input)
        output = '\n'.join([i.decode('utf-8') for i in (stdout, stderr) if i is not None])
        if process.returncode != 0:
            raise RuntimeError(output)
        else:
            print(output)
    except BaseException as e:
        raise Exception(f"An error has occurred while executing Doxygen\n{e}")


def generate_r_docs(app: Sphinx) -> None:
    """Generate documentation for R-package.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        The application object representing the Sphinx process.
    """
    commands = f"""
    export TAR=/bin/tar
    cd {CURR_PATH.parent}
    export R_LIBS="$CONDA_PREFIX/lib/R/library"
    sh build-cran-package.sh || exit -1
    R CMD INSTALL --with-keep.source lightgbm_*.tar.gz || exit -1
    cp -R \
        {CURR_PATH.parent / "R-package" / "pkgdown"} \
        {CURR_PATH.parent / "lightgbm_r" / "pkgdown"}
    cd {CURR_PATH.parent / "lightgbm_r"}
    Rscript -e "roxygen2::roxygenize(load = 'installed')" || exit -1
    Rscript -e "pkgdown::build_site( \
            lazy = FALSE \
            , install = FALSE \
            , devel = FALSE \
            , examples = TRUE \
            , run_dont_run = TRUE \
            , seed = 42L \
            , preview = FALSE \
            , new_process = TRUE \
        )
        " || exit -1
    cd {CURR_PATH.parent}
    """
    try:
        # Warning! The following code can cause buffer overflows on RTD.
        # Consider suppressing output completely if RTD project silently fails.
        # Refer to https://github.com/svenevs/exhale
        # /blob/fe7644829057af622e467bb529db6c03a830da99/exhale/deploy.py#L99-L111
        process = Popen(['/bin/bash'],
                        stdin=PIPE, stdout=PIPE, stderr=PIPE,
                        universal_newlines=True)
        stdout, stderr = process.communicate(commands)
        output = '\n'.join([i for i in (stdout, stderr) if i is not None])
        if process.returncode != 0:
            raise RuntimeError(output)
        else:
            print(output)
    except BaseException as e:
        raise Exception(f"An error has occurred while generating documentation for R-package\n{e}")


def setup(app: Sphinx) -> None:
    """Add new elements at Sphinx initialization time.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        The application object representing the Sphinx process.
    """
    first_run = not (CURR_PATH / '_FIRST_RUN.flag').exists()
    if first_run and RTD:
        (CURR_PATH / '_FIRST_RUN.flag').touch()
    if C_API:
        app.connect("builder-inited", generate_doxygen_xml)
    else:
        app.add_directive('doxygenfile', IgnoredDirective)
    if RTD:  # build R docs only on Read the Docs site
        if first_run:
            app.connect("builder-inited", generate_r_docs)
        app.connect("build-finished",
                    lambda app, _: copytree(CURR_PATH.parent / "lightgbm_r" / "docs",
                                            Path(app.outdir) / "R"))
    app.add_transform(InternalRefTransform)
    add_js_file = getattr(app, 'add_js_file', False) or app.add_javascript
    add_js_file("js/script.js")
