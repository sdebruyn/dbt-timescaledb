#!/usr/bin/env python
from setuptools import find_namespace_packages, setup

package_name = "dbt-timescaledb"
# make sure this always matches dbt/adapters/{adapter}/__version__.py
package_version = "1.7.0"
description = """The TimescaleDB adapter plugin for dbt"""

setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=description,
    author="Sam Debruyn",
    author_email="dbt.sam@debruyn.dev",
    url="https://github.com/sdebruyn/dbt-timescaledb",
    packages=find_namespace_packages(include=["dbt", "dbt.*"]),
    include_package_data=True,
    install_requires=[
        "dbt-core~=1.7.0.",
    ],
)
