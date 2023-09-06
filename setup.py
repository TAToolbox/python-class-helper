from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
setup(
    name='classhelper',
    version='1.0.0',
    description='Making life easier for class repo maintainers',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/TAToolbox/python-class-helper',
    author='Ouroboros Analytics',
    author_email='justin@ouroboros-analytics.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Intended Audience :: TA's, Instructors",
        'Topic :: Education :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=['docs']),
    python_requires='>=3.4*, <4',
    install_requires=['altgraph==0.16.1', 'astroid==2.2.5', 'autopep8==1.4.4', 'Click==7.0', 'colorama==0.4.1', 'future==0.17.1', 'gitdb2==2.0.5', 'GitPython==3.1.34', 'importlib-metadata==0.22', 'isort==4.3.21', 'lazy-object-proxy==1.4.2', 'mccabe==0.6.1', 'more-itertools==7.2.0',
                      'pefile==2019.4.18', 'pycodestyle==2.5.0', 'pylint==2.3.1', 'PyQt5==5.13.0', 'PyQt5-sip==4.19.18', 'pyqt5-tools==5.13.0.1.5', 'python-dotenv==0.10.3', 'pywin32-ctypes==0.2.0', 'six==1.12.0', 'smmap2==2.0.5', 'typed-ast==1.4.0', 'wrapt==1.11.2', 'zipp==0.6.0'],
    project_urls={
        'Bug Reports': 'https://github.com/TAToolbox/python-class-helper/issues',
        'Source': 'https://github.com/TAToolbox/python-class-helper/',
    },
)
