from setuptools import setup



VERSION="0.1"


with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pynternode',

    packages = ['pynternode'] ,
    version = VERSION , 
    long_description = long_description , 
    install_requires = ['pexpect'] , 
    description = 'Simple and robust async mode interaction with nodejs' ,
    author = 'Andrew Gree' ,
    url = 'https://github.com/grandrew/pynternode',
    author_email = 'realgrandrew@gmail.com' ,
    keywords=['nodejs', 'node' , 'v8', 'binding' , 'automation', 'interoperability'],
    classifiers = [
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'License :: OSI Approved :: BSD License' , 
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7'
          ] 
)
