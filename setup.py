import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lambdacalc",
    version="0.0.1",
    author="Andrew Fichman",
    description="Lambda Calculus parser/reducer in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/heavyairship/LambdaCalc",
    packages=['lambdacalc'],
    package_dir={'lambdacalc': 'lambdacalc'},
    package_data={'lambdacalc': ['stdlib/*.l']},
    python_requires='>=3.6',
)
