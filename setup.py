from setuptools import find_namespace_packages
from setuptools import setup

version = "1.3.0"

long_description = (
    open("README.rst").read() + "\n" + "Contributors\n"
    "============\n"
    + "\n"
    + open("CONTRIBUTORS.rst").read()
    + "\n"
    + open("CHANGES.rst").read()
    + "\n"
)

setup(
    name="collective.purgebyid",
    version=version,
    description="p.a.caching add-on for a better purging policy",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # Get more strings from
    # https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="plone caching",
    author="Mauro Amico",
    author_email="mauro.amico@gmail.com",
    url="https://github.com/collective/collective.purgebyid",
    license="gpl",
    packages=find_namespace_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.9",
    install_requires=[
        # -*- Extra requirements: -*-
        "Zope",
        "Products.CMFCore",
        "plone.uuid",
        "plone.resource",
        "plone.transformchain",
        "z3c.caching",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            "plone.api",
            "plone.app.contenttypes",
            "plone.testing",
        ]
    },
    entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
