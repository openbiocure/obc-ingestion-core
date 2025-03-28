from setuptools import setup, find_packages

setup(
    name="herpai-lib",
    version="0.1.0",
    description="HerpAI Core Library, Accelerating the discovery of a functional cure for HSV-1 and HSV-2 using AI.",
    author="OpenBioCure Contributors",
    author_email="openbiocure@gmail.com",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "sqlalchemy>=2.0.0",
        "pyyaml>=6.0",
        "aiosqlite>=0.17.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=4.0.0",
            "black",
            "isort",
            "mypy",
        ],
    },
)
