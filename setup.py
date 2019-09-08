from setuptools import find_packages, setup
import os

NAME = "friendbot"
HERE = os.path.abspath(os.path.dirname(__file__))

version_ns = {}
with open(os.path.join(HERE, NAME, "__version__.py")) as f:
    exec(f.read(), {}, version_ns)

with open("README.md", "r") as fh:
    long_description = fh.read()

desc = "Markov-chain based chatbot which uses Slack messages as its corpus"

setup(
    name="friendbot",
    version=version_ns["__version__"],
    author="Nolan Cooper",
    author_email="nolancooper97@gmail.com",
    description=desc,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/barrelmaker97/friendbot",
    license="MIT",
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    python_requires=">=3.4",
    keywords="markov chatbot wsgi slack",
    install_requires=["flask", "markovify", "requests"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
