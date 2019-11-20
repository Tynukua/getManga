import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name = 'getmanga',
    version="0.1.5",
    author="Tynukua",
    author_email = 'tynuk.ua@gmail.com',
    description = 'package for load manga! :)',
    
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Tynukua/getManga',
    packages=setuptools.find_packages(),
    requires_python='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",] ,
    install_requires=[
        'aiohttp',
        'requests', 
        'beautifulsoup4']
    )