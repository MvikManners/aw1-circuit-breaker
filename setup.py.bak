from setuptools import setup, find_packages

setup(
    name="aw1-breaker",
    version="2.0.1",
    author="Manners Vela Ikhutseng",
    author_email="mvik1982@gmail.com",
    description="Sovereign out-of-band AST execution circuit breaker for autonomous AI agent tool calls.",
    long_description=open("README.md", encoding="utf-8").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/MvikManners/aw1-circuit-breaker",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[],  # ZERO RUNTIME DEPENDENCIES (Standard Library Only)
    extras_require={
        "server": ["flask>=2.0.0", "requests>=2.25.0"],
        "dev": ["pytest>=7.0.0", "black"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
)
