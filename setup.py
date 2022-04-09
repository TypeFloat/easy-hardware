from setuptools import setup


setup(
    name="easy_hardware",
    version="1.0",
    author="TypeFloat",
    author_email="liuzekun_123@163.com",
    description="Help you use hardware easily with python.",
    url="https://github.com/TypeFloat/easy-hardware", 
    packages=["easyhardware"],
    python_requires=">=3.6",
    install_requires=["smbus>=1.1.post2"]
)