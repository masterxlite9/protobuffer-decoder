from setuptools import setup, find_packages

setup(
    name="protobuf_decoder",
    version="0.1.0",
    author="Manus",
    author_email="contact@example.com",
    description="A simple Protobuf decoder and encoder library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/example/protobuf_decoder",  # Replace with actual URL if available
    packages=find_packages(where="."), # find packages in the current directory
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Choose an appropriate license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

