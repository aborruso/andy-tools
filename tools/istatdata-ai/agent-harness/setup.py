from setuptools import find_namespace_packages, setup

setup(
    name="cli-anything-istatdata-ai",
    version="1.0.0",
    description="CLI harness for the IstatData AI assistant (ISTAT Data Browser)",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    package_data={"cli_anything.istatdata_ai": ["skills/*.md", "tests/fixtures/*.json"]},
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=["click>=8.0"],
    entry_points={
        "console_scripts": [
            "cli-anything-istatdata-ai=cli_anything.istatdata_ai.istatdata_ai_cli:main",
            "istat-ask=cli_anything.istatdata_ai.istatdata_ai_cli:main",
        ]
    },
)
