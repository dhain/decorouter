from setuptools import setup, find_packages

version = '0.0.1'

setup(
    name='decorouter',
    version=version,
    description=('A WSGI routing apparatus.'),
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
    packages=find_packages(),
    requires=['webob'],
    test_suite='decorouter.test',
    tests_require=['mock'],
)
