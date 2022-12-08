from setuptools import setup, find_packages


version = "1.2.1"

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
    long_description_content_type='text/x-rst',
    # Get more strings from
    # https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="plone caching",
    author="Mauro Amico",
    author_email="mauro.amico@gmail.com",
    url="https://github.com/collective/collective.purgebyid",
    license="gpl",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=[
        "collective",
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        # -*- Extra requirements: -*-
        "plone.uuid",
    ],
    extras_require={"test": ["plone.app.testing", "plone.api", "plone.app.contenttypes"]},
    entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
