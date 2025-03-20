from setuptools import setup, find_packages

setup(
    name="migraterator",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.25.1",
        "pyyaml>=6.0",
        "google-api-python-client>=2.0.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "migraterator=src.cli:cli",
        ],
    },
    python_requires=">=3.10",
    author="Your Name",
    author_email="your.email@example.com",
    description="Analyze infrastructure changes in PRs and provide migration guidance",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/migraterator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
) 