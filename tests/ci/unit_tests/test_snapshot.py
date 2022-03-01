#  Copyright (c) 2022 Food-X Technologies
#
#  This file is part of foodx_backup_source.
#
#  You should have received a copy of the MIT License along with
#  foodx_backup_source. If not, see <https://opensource.org/licenses/MIT>.

import pathlib
import tempfile

import git
import pytest

from foodx_backup_source._snapshot import _create_tarfile, do_snapshot
from foodx_backup_source.schema import (
    ApplicationDefinition,
    ApplicationDependency,
)


@pytest.fixture()
def mock_definition() -> ApplicationDefinition:
    x = ApplicationDefinition(
        name="n1",
        configuration=ApplicationDependency.parse_obj(
            {
                "backup": {
                    "repo_url": "https://some.where",
                    "branch_name": "some_branch_name",
                },
                "docker": {"image_name": "some-image", "tag_prefix": "p-"},
                "release": {"ref": "abc123"},
            }
        ),
    )

    return x


class TestCreateTarfile:
    def test_clean(self):
        with tempfile.TemporaryDirectory() as d:
            dd = pathlib.Path(d)
            tarfile = dd / "some.tar.gz"
            r = dd / "working"
            this_repo = git.Repo.clone_from(
                "https://github.com/Food-X-Technologies"
                "/foodx_devops_tools.git",
                r,
            )

            _create_tarfile("something", "HEAD", tarfile, this_repo)

            expected_hashfile = dd / "some.tar.gz.sha256"
            assert expected_hashfile.is_file()


class TestDoSnapshot:
    @pytest.mark.asyncio
    async def test_clean(self, mock_definition, mocker):

        with tempfile.TemporaryDirectory() as d:
            mock_archive = pathlib.Path(d)

            mocker.patch("foodx_backup_source._snapshot._create_tarfile")
            mocker.patch("foodx_backup_source._snapshot.git.Repo.clone_from")

        result = await do_snapshot(mock_definition, mock_archive, None)

        assert result == mock_archive / "n1-abc123.tar.gz"
