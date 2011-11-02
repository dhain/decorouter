import os
from setuptools import setup, find_packages

version = '0.0.2'
README = os.path.join(os.path.dirname(__file__), 'README.rst')
long_description = open(README).read() + '\n\n'

if __name__ == '__main__':
    setup(
        name='decorouter',
        version=version,
        description=('A WSGI routing apparatus.'),
        long_description=long_description,
        author='David Zuwenden',
        author_email='dhain@zognot.org',
        url='https://github.com/dhain/decorouter',
        license='MIT',
        classifiers=[
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        keywords='wsgi route',
        packages=find_packages(),
        requires=['webob'],
        test_suite='decorouter.test',
        tests_require=['mock'],
    )
