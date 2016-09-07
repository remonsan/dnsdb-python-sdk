from setuptools import setup, find_packages

PACKAGE = "dnsdb"
NAME = "dnsdb python sdk"
DESCRIPTION = "DnsDB Python SDK"
AUTHOR = "DnsDB Team"
AUTHOR_EMAIL = "team@dnsdb.io"
URL = "https://dnsdb.io"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="Apache License, Version 2.0",
    url=URL,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2.7',
    ],
    zip_safe=False,
)
