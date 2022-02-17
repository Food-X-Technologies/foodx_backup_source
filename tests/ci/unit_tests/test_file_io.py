#  Copyright (c) 2022 Food-X Technologies
#
#  This file is part of foodx_backup_source.
#
#  You should have received a copy of the MIT License along with
#  foodx_backup_source. If not, see <https://opensource.org/licenses/MIT>.

import pathlib

import pytest

from foodx_backup_source._file_io import (
    discover_backup_definitions,
    load_backup_definitions,
)

DATA_DIR = pathlib.Path(__file__).parent / "data"


class TestDiscoverBackupDefinitions:
    def test_clean(self, mocker):
        mocker.patch.object(
            pathlib.Path,
            "iterdir",
            return_value=[
                DATA_DIR / "dependencies_d1.yml",
                DATA_DIR / "dependencies_d1.yaml",
            ],
        )
        mocker.patch.object(pathlib.Path, "is_file", return_value=True)

        results = discover_backup_definitions(DATA_DIR)

        assert {
            (DATA_DIR / "dependencies_d1.yml"),
            (DATA_DIR / "dependencies_d2.yaml"),
        } & results

    def test_no_dependencies(self, mocker):
        mocker.patch.object(
            pathlib.Path, "iterdir", return_value=[DATA_DIR / "d1.yml"]
        )
        mocker.patch.object(pathlib.Path, "is_file", return_value=True)

        results = discover_backup_definitions(DATA_DIR)

        assert not results

    def test_no_yml(self, mocker):
        mocker.patch.object(
            pathlib.Path,
            "iterdir",
            return_value=[DATA_DIR / "dependencies_d1.txt"],
        )
        mocker.patch.object(pathlib.Path, "is_file", return_value=True)

        results = discover_backup_definitions(DATA_DIR)

        assert not results

    def test_no_yaml(self, mocker):
        mocker.patch.object(
            pathlib.Path,
            "iterdir",
            return_value=[DATA_DIR / "dependencies_d1.txt"],
        )
        mocker.patch.object(pathlib.Path, "is_file", return_value=True)

        results = discover_backup_definitions(DATA_DIR)

        assert not results

    def test_not_file(self, mocker):
        mocker.patch.object(
            pathlib.Path,
            "iterdir",
            return_value=[DATA_DIR / "dependencies_d1.yml"],
        )
        mocker.patch.object(pathlib.Path, "is_file", return_value=False)

        results = discover_backup_definitions(DATA_DIR)

        assert not results


class TestLoadBackupDefinitions:
    @pytest.mark.asyncio
    async def test_clean(self):
        this_files = {
            DATA_DIR / "dependencies_d1.yaml",
            DATA_DIR / "dependencies_d2.yaml",
        }
        result = await load_backup_definitions(this_files)

        assert {"r1", "r2"} & {x.name for x in result}
        assert {"main", "master"} & {
            x.configuration.backup.branch_name for x in result
        }
