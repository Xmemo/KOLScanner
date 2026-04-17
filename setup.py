from setuptools import find_packages, setup


setup(
    name="signal-qa",
    version="0.1.0",
    description="Signal quality audit toolkit for exported Telegram channel history",
    package_dir={"": "src"},
    packages=find_packages("src"),
)

