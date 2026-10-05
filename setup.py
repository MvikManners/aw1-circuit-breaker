from setuptools import setup, find_packages

setup(
    name="aw1-breaker",
    version="2.0.0",
    description="AW-1 Sovereign Agent Security & Circuit Breaker Standard",
    long_description=open("/home/LavetoLab/README.md").read() if open("/home/LavetoLab/README.md") else "AW-1 Sovereign Defense Standard",
    long_description_content_type="text/markdown",
    author="Laveto Labs",
    author_email="command@laveto.net",
    url="https://p20.laveto.net/wisdom/docs",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=[
        "flask>=2.0.0",
        "requests>=2.25.0",
    ],
)
