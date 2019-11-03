from setuptools import setup, find_packages, Command
from codecs import open
from os import path, system
import re

package_name = "pytchat"

root_dir = path.abspath(path.dirname(__file__))

def _requirements():
    return [name.rstrip() for name in open(path.join(root_dir, 'requirements.txt')).readlines()]

def _test_requirements():
    return [name.rstrip() for name in open(path.join(root_dir, 'requirements_test.txt')).readlines()]


with open(path.join(root_dir, package_name, '__init__.py')) as f:
    init_text = f.read()
    version = re.search(r'__version__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    license = re.search(r'__license__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    author = re.search(r'__author__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    author_email = re.search(r'__author_email__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    url = re.search(r'__url__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)

assert version
assert license
assert author
assert author_email
assert url

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        #system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')
        system('rmdir /Q  pytchat.egg-info')


setup(
    name=package_name,
    packages=find_packages(),
    version=version,
    url=url,
    author=author,
    author_email=author_email,
    long_description=long_description,
    long_description_content_type='text/markdown',
    license=license,
    install_requires=_requirements(),
    tests_require=_test_requirements(),
    description="a python library for fetching youtube live chat.",
    classifiers=[
        'Natural Language :: Japanese',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',        
        'License :: OSI Approved :: MIT License',
    ],
    keywords='youtube livechat asyncio',
    cmdclass={
        'clean': CleanCommand,
    }
)