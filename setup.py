from setuptools import setup

setup(name="subset",
      version="0.1",
      description="A cli-based word game",
      url="https://github.com/rightbrace/subset-game.git",
      author="Josef Duchesne",
      author_email="josefduchesne@outlook.com",
      license="MIT",
      packages=["subset"],
      scripts=["bin/subset"],
      zip_safe=False,
      install_requires=[
          "colorama"
      ],
      include_package_data=True)

