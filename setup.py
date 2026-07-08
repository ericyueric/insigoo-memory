"""
insigoo-memory — 公益组织的 AI 知识管家
自动建、自动理、能提醒、能给建议
"""
from setuptools import setup, find_packages

setup(
    name="insigoo-memory",
    version="0.4.0",
    description="公益组织 AI 知识管家",
    author="insigoo 因思阁",
    packages=find_packages(exclude=["benchmarks", "benchmarks.*", "test_fixtures", "test_fixtures.*"]),
    entry_points={
        "console_scripts": [
            "insigoo-memory=insigoo_memory.cli:main",
        ],
    },
    python_requires=">=3.10",
)
