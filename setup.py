import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name="privatelib",
    version="0.0.1",
    author="akashpalrecha",
    author_email="akashpalrecha@gmail.com",
    description="My personal code library",
    long_description=long_description,
    url="https://github.com/akashpalrecha/privatelib",
    packages=setuptools.find_packages(),
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    ],
)