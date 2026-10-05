import os
from setuptools import setup, find_packages

readme = '/home/LavetoLab/README.md'
desc = 'AW-1 Sovereign Agent Security & Circuit Breaker Standard'
if os.path.exists(readme):
    with open(readme, 'r', encoding='utf-8') as f:
        desc = f.read()

setup(
    name='aw1-breaker',
    version='2.0.0',
    description='AW-1 Sovereign Agent Security Standard',
    long_description=desc,
    long_description_content_type='text/markdown',
    author='Laveto Labs',
    author_email='command@laveto.net',
    url='https://p20.laveto.net/wisdom/docs',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=['flask>=2.0.0', 'requests>=2.25.0'],
)
