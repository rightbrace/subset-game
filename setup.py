from setuptools import setup
import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setup(name="subset",
      version="0.1.2",
      description="A cli-based word game",
      long_description_content_type="text/markdown",
      long_description=long_description,
      url="https://github.com/rightbrace/subset-game.git",
      author="Josef Duchesne",
      author_email="josefduchesne@outlook.com",
      license="MIT",
      packages=setuptools.find_packages(),
      #scripts=["bin/subset"],
      entry_points = {
        "console_scripts":[
            "subset = subset.app:main"
        ]
      },
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

