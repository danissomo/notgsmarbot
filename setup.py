from setuptools import setup, find_packages
import os


ENV = os.getenv("ENV", "prod")

config_file = "config.yaml" if ENV == "prod" else "config.local.yaml"

if os.path.exists(config_file):
    with open(config_file, "r") as src, open(
        "notgsmarbot/files/config.yaml", "w"
    ) as dst:
        dst.write(src.read())


def read_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


setup(
    name="notgsmarbot",
    version="0.2.0",
    packages=find_packages(),
    install_requires=read_requirements("requirements.txt"),
    author="Daniil",
    author_email="dan.2k64@gmail.com",
    description="Telegram bot for render specs from kimovil.com",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/danissomo/notgsmarbot",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    package_data={
        "notgsmarbot": ["files/*"],
    },
    entry_points={
        "console_scripts": [
            "notgsmarbot = notgsmarbot.notgsmar:main", 
        ],
    },
)
