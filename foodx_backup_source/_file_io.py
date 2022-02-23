#  Copyright (c) 2022 Food-X Technologies
#
#  This file is part of foodx_backup_source.
#
#  You should have received a copy of the MIT License along with
#  foodx_backup_source. If not, see <https://opensource.org/licenses/MIT>.

"""Manage backup definitions file IO."""

import asyncio
import logging
import pathlib
import typing

import aiofiles
import deepmerge  # type: ignore
import ruamel.yaml

from .schema import ApplicationDefinition, DependencyFile

log = logging.getLogger(__name__)

BackupDefinitions = typing.List[ApplicationDefinition]
PathSet = typing.Set[pathlib.Path]

VALID_SUFFIXES = {".yml", ".yaml"}


async def _load_application_dependencies(file: pathlib.Path) -> dict:
    log.info(f"loading application dependencies from file, {file}")
    yaml_parser = ruamel.yaml.YAML(typ="safe")
    async with aiofiles.open(file, mode="r") as f:
        content = await f.read()
        content_data = yaml_parser.load(content)

        # apply ApplicationDependencies here to validate the content,
        # but don't keep the result because it's to be merged at a higher level
        DependencyFile.parse_obj(content_data)

    return content_data


def _merge_file_content(results: typing.List[dict]) -> DependencyFile:
    merged: dict = dict()
    for x in results:
        merged = deepmerge.always_merger.merge(merged, x)
    data: DependencyFile = DependencyFile.parse_obj(merged)

    return data


def discover_backup_definitions(directory_path: pathlib.Path) -> PathSet:
    """
    Identify application dependency files in the specified directory.

    Args:
        directory_path: Path to directory containing application dependency
                        files.

    Returns:
        Set of application dependency file paths.
    """
    files = {
        x
        for x in directory_path.iterdir()
        if x.is_file()
        and (x.suffix in VALID_SUFFIXES)
        and x.name.startswith("dependencies")
    }
    log.info(f"discovered dependency files, {files}")

    return files


async def load_backup_definitions(files: PathSet) -> BackupDefinitions:
    """
    Load application dependency definitions from the specified files.

    Merges the dependency definitions from multiple files into a single entity.

    Args:
        files: Set of application dependency file paths.

    Returns:
        List of application backup definitions.
    """
    results = await asyncio.gather(
        *[_load_application_dependencies(x) for x in files]
    )

    data = _merge_file_content(list(results))

    definitions: BackupDefinitions = list()
    for name, configuration in data.context.dependencies.items():
        this_element = ApplicationDefinition(
            name=name, configuration=configuration
        )
        definitions.append(this_element)

    return definitions
