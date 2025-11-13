"""
Setup configuration for the ML Pipeline project.

This makes the project installable via pip, enabling clean imports
and easier dependency management.
"""

from setuptools import setup, find_packages

setup(
    name="ml-pipeline",
    version="0.1.0",
    description="Production-ready End-to-End ML Pipeline with MLOps best practices",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "scikit-learn>=1.3.2",
        "xgboost>=2.0.3",
        "pandas>=2.1.4",
        "numpy>=1.26.2",
        "mlflow>=2.9.2",
        "prefect>=2.14.11",
        "fastapi>=0.109.0",
        "uvicorn>=0.25.0",
        "pydantic>=2.5.3",
        "pydantic-settings>=2.1.0",
        "great-expectations>=0.18.8",
        "evidently>=0.4.13",
        "psycopg2-binary>=2.9.9",
        "sqlalchemy>=2.0.25",
        "prometheus-client>=0.19.0",
        "prometheus-fastapi-instrumentator>=6.1.0",
        "python-dotenv>=1.0.0",
        "PyYAML>=6.0.1",
        "requests>=2.31.0",
        "click>=8.1.7",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-cov>=4.1.0",
            "httpx>=0.26.0",
            "black>=23.12.1",
            "flake8>=7.0.0",
            "isort>=5.13.2",
            "mypy>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ml-pipeline=ml_pipeline.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
