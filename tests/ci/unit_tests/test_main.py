#  Copyright (c) 2022 Food-X Technologies
#
#  This file is part of backup_source.
#
#  You should have received a copy of the MIT License along with
#  backup_source. If not, see <https://opensource.org/licenses/MIT>.

import pathlib
import typing

import click
import pytest
from click.testing import CliRunner

import foodx_backup_source._main
from foodx_backup_source._file_io import BackupDefinitions
from foodx_backup_source._main import DEFAULT_OUTPUT_PATH, _gather, main
from foodx_backup_source.schema import ApplicationDefinition, DependencyFile


@pytest.fixture()
def mock_gather(mocker):
    return mocker.patch("foodx_backup_source._main._gather")


@pytest.fixture()
def mock_runner():
    return CliRunner()


@pytest.fixture()
def mock_path(mocker):
    def mock_convert(
        value: typing.Any,
        param: typing.Optional["Parameter"],
        ctx: typing.Optional["Context"],
    ) -> typing.Any:
        # don't do any checking on the parameter
        return pathlib.Path(value)

    mocker.patch.object(click.Path, "convert", side_effect=mock_convert)


@pytest.fixture()
def mock_definitions(load_yaml_content):
    content_text = """
---
context:
  dependencies:
    r1:
      backup:
        repo_url: "https://this.host/path"
        branch_name: master
      docker:
        image_name: r1-image
        tag_prefix: pp-
      release:
        ref: "3.1.4"
"""
    data = DependencyFile.parse_obj(load_yaml_content(content_text))
    definitions: BackupDefinitions = list()
    for name, configuration in data.context.dependencies.items():
        this_element = ApplicationDefinition(
            name=name, configuration=configuration
        )
        definitions.append(this_element)

    return definitions


class TestGather:
    @pytest.mark.asyncio
    async def test_clean(self, mock_definitions, mocker):
        mock_snapshot = mocker.patch("foodx_backup_source._main.do_snapshot")
        mocker.patch("foodx_backup_source._main.tarfile.open")
        mocker.patch("foodx_backup_source._main.discover_backup_definitions")
        mocker.patch(
            "foodx_backup_source._main.load_backup_definitions",
            return_value=mock_definitions,
        )
        mocker.patch(
            "foodx_backup_source._main._isoformat_now", return_value="today"
        )
        mock_hash_file = mocker.patch(
            "foodx_backup_source._main.create_hash_file"
        )
        arguments = {
            "project_name": "this_project",
            "project_directory": pathlib.Path("some/project"),
            "output_directory": pathlib.Path("some/output"),
            "token": None,
        }

        await _gather(**arguments)

        mock_hash_file.assert_called_once_with(
            pathlib.Path("some/output/this_project-today.tar.gz")
        )
        mock_snapshot.assert_called_once()


class TestMain:
    def test_default(self, mock_gather, mock_runner, mock_path):
        arguments = [
            "this_project",
            "some/path",
        ]

        result = mock_runner.invoke(main, arguments)

        assert result.exit_code == 0
        mock_gather.assert_awaited_once_with(
            arguments[0],
            pathlib.Path(arguments[1]),
            DEFAULT_OUTPUT_PATH,
            None,
        )

    def test_token_file_stdin(
        self, mock_gather, mock_runner, mock_path, mocker
    ):
        arguments = [
            "this_project",
            "some/path",
            "--token-file",
            "-",
        ]

        result = mock_runner.invoke(main, arguments, input="deadb33f")

        assert result.exit_code == 0
        mock_gather.assert_awaited_once_with(
            mocker.ANY,
            mocker.ANY,
            mocker.ANY,
            "deadb33f",
        )

    def test_token_file_whitespace(
        self, mock_gather, mock_runner, mock_path, mocker
    ):
        arguments = [
            "this_project",
            "some/path",
            "--token-file",
            "-",
        ]

        result = mock_runner.invoke(main, arguments, input=" deadb33f\n")

        assert result.exit_code == 0
        mock_gather.assert_awaited_once_with(
            mocker.ANY,
            mocker.ANY,
            mocker.ANY,
            "deadb33f",
        )

    def test_output(self, mock_gather, mock_runner, mock_path, mocker):
        arguments = [
            "this_project",
            "some/path",
            "--output-dir",
            "output/dir",
        ]

        result = mock_runner.invoke(main, arguments)

        assert result.exit_code == 0
        mock_gather.assert_awaited_once_with(
            mocker.ANY,
            mocker.ANY,
            pathlib.Path("output/dir"),
            mocker.ANY,
        )
