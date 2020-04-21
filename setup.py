import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="evaluator",
    author="Bryan Martin",
    author_email="bryan@martinpdx.com",
    description="a small parsing application",
    long_description=long_description,
    url="https://github.com/bryan-martin/nlight",
    packages=setuptools.find_packages(),
    install_requires=[
        "pytest",
    ],
    include_package_data=True,
)