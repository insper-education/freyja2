from setuptools import setup

setup(
    name="Freyja 2",
    version="1.0",
    packages=["freyja", "freyja.tools"],
    include_package_data=True,
    install_requires=["click", "pyyaml"],
    entry_points="""
        [console_scripts]
        freyja=freyja.cli:cli
    """,
)
