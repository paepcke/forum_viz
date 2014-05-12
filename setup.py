import multiprocessing
from setuptools import setup, find_packages

# NOTE: scikit-learn depends on a number of packages,
#       not all of which are available via PIP. 
#       Run: sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose
#       to install the prerequisites.

setup(
    name = "forum_viz",
    version = "0.1",
    packages = find_packages(),

    # Dependencies on other packages:
    # Couldn't get numpy install to work without
    # an out-of-band: sudo apt-get install python-dev
    setup_requires   = [],
    install_requires = ['pymysql_utils>=0.33',
			'configparser>=3.3.0',
			#'json_to_relation>=0.3',
			'numpy>=1.8.1',
			'scipy>=0.14.0',
			'scikit-learn>=0.14'
			],
    tests_require    = ['sentinels>=0.0.6', 'nose>=1.0'],

    # Unit tests; they are initiated via 'python setup.py test'
    test_suite       = 'nose.collector', 

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
     #   '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
     #   'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author = "Jagadish Venkatraman and Akshay Agrawal",
    author_email = "paepcke@cs.stanford.edu",
    description = "(OpenEdX) Forum summarizations",
    license = "BSD",
    keywords = "OpenEdx, Forum",
    url = "https://github.com/Stanford-Online/forum-viz",   # project home page, if any
)
