#!/usr/bin/env python
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['-s']
        self.test_suite = True

    def run_tests(self):
        import pytest
        pytest.main(self.test_args)

requires = [
    'six>=1.9.0',
    'voluptuous>=0.8.7',
    'typedtuple>=0.1.0',
]

setup(
    name='hieratic',
    version='0.0.7',
    description='hierarchical resource implementation.',
    author='Satoshi Ebihara',
    author_email='kiri@succhiello.net',
    url='https://github.com/succhiello/hieratic',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
    ],
    packages=find_packages(),
    install_requires=requires,
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    entry_points={
        'hieratic.engine': [
            'memory = hieratic.engine.memory',
        ],
    },
)
