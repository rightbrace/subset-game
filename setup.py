from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(name="subset",
      version="0.1.0",
      description="A cli-based word game",
      long_description_content_type="text/markdown"
      long_description=long_description
      url="https://github.com/rightbrace/subset-game.git",
      author="Josef Duchesne",
      author_email="josefduchesne@outlook.com",
      license="MIT",
      packages=setuptools.find_packages(),
      scripts=["bin/subset"],
      zip_safe=False,
      install_requires=[
          "colorama"
      ],
      include_package_data=True,
      classifiers = [
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires=">=3.5"
      )

