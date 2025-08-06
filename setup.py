from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="claude-agent-environment",
    version="1.0.0",
    author="David Keegan",
    author_email="",
    description="Multi-repository development workflow manager for Claude AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/claude-agent-environment",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "cae=claude_agent_environment.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "claude_agent_environment": ["claude_template.md", "cae_config.example.json"],
    },
    install_requires=[],
)