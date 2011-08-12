from setuptools import setup, find_packages

version = '0.0.1'

setup(
    name='router',
    version=version,
    description=('A WSGI routing middleware.'),
    author='David Zuwenden',
    author_email='dhain@zognot.org',
    url='http://zognot.org/',
    license='MIT',
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    requires=['webob'],
    test_suite='router.test',
    tests_require=['mock'],
)
