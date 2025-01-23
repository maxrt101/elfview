import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="elfview",
    version="0.1.0",
    author="maxrtx",
    description="Setup for elfview",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maxrt101/elfview",
    packages=['elfview'],
    entry_points={
        'console_scripts': [
            'elfview = elfview.main:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.11',
)