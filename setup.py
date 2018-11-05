import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="farc",
    version="0.1.0",
    author="Dean Hall",
    author_email="dwhall256@gmail.com",
    description="Framework for Asyncio/Actor/AHSM Run-to-completion Concurrency",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dwhall/farc",
    packages=setuptools.find_packages(),
    classifiers=[
        # Python 3.4 (or later) because asyncio is required
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
