#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.

import pathlib

import pytest

from foodx_backup_source._version import DEFAULT_RELEASE_ID, acquire_version


def test_clean(mocker):
    mock_here = mocker.create_autospec(pathlib.Path)

    mocker.patch(
        "foodx_backup_source._version.pathlib.Path.absolute",
        return_value=mock_here,
    )
    mock_here.is_file.return_value = True

    mock_handle = mock_here.open.return_value.__enter__.return_value
    mock_handle.read.return_value = "  3.14.159\n"

    result = acquire_version()

    assert result == "3.14.159"


def test_missing_file(mocker):
    mock_here = mocker.create_autospec(pathlib.Path)

    mocker.patch(
        "foodx_backup_source._version.pathlib.Path.absolute",
        return_value=mock_here,
    )
    mock_here.is_file.return_value = False

    result = acquire_version()

    assert result == DEFAULT_RELEASE_ID


def test_empty_file(mocker):
    mock_here = mocker.create_autospec(pathlib.Path)

    mocker.patch(
        "foodx_backup_source._version.pathlib.Path.absolute",
        return_value=mock_here,
    )
    mock_here.is_file.return_value = True

    mock_handle = mock_here.open.return_value.__enter__.return_value
    mock_handle.read.return_value = ""

    with pytest.raises(RuntimeError, match=r"^Unable to acquire version"):
        acquire_version()
