from setuptools import find_packages, setup

setup(
    name="ocdsmetricsanalysis",
    version="0.1.0",
    author="Open Data Services",
    author_email="code@opendataservices.coop",
    url="https://github.com/OpenDataServices/ocds-metrics-analysis",
    project_urls={
        "Documentation": "https://ocds-metrics-analysis.readthedocs.io/en/latest/",
        "Issues": "https://github.com/OpenDataServices/ocds-metrics-analysis/issues",
        "Source": "https://github.com/OpenDataServices/ocds-metrics-analysis",
    },
    description="",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest",
            "black==22.12.0",
            "isort",
            "flake8",
            "mypy",
            "sphinx",
            "sphinx_rtd_theme",
        ],
    },
    classifiers=[],
)
