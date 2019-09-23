import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyfpl",
    version="0.1.2",
    author="C. H. Joyner",
    author_email="c.joyner.uk@gmail.com",
    description="python api for fantasy.premierleague.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['requests', 'numpy', 'pandas'],
    include_package_data=True
)
