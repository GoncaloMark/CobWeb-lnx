from setuptools import setup, find_packages

setup(
    name='CobWeb',
    version='1.0.0',
    author='Gonçalo Marques (_lnx)',
    author_email='gmgoncalo7@gmail.com',
    description='CobWeb is a Python library for web scraping. The library consists of two classes: Spider and Scraper.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/GoncaloMark/Amara-CobWeb',
    packages=find_packages(),
    install_requires = open('requirements.txt').readlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
