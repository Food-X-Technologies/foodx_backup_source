#  Copyright (c) 2022 Food-X Technologies
#
#  This file is part of foodx_backup_source.
#
#  You should have received a copy of the MIT License along with
#  foodx_backup_source. If not, see <https://opensource.org/licenses/MIT>.

import json
import subprocess
import unittest.mock
from urllib.parse import urlparse

import pytest

from foodx_backup_source.azure import AzureKeyvaultError, get_kv_secret

DEFAULT_SECRET_VALUE = "some-secret-value"


class MockSubprocessRun:
    def __init__(
        self, returncode=0, secret_value=DEFAULT_SECRET_VALUE, stderr=""
    ):
        self._returncode = returncode
        self._stderr = stderr
        self._secret_value = secret_value

        self.command = list()
        self.kwargs = dict()

    def __call__(self, command, **kwargs):
        self.command = command
        self.kwargs = kwargs

        if isinstance(command, list) and (len(command) == 8):
            keyvault_url = command[7]
        else:
            pytest.fail(f"badly specified command, {command}")

        url_object = urlparse(keyvault_url)
        secret_name = url_object.path.split("/")[-1]

        if self._returncode != 0:
            raise subprocess.SubprocessError()

        mock_response = unittest.mock.MagicMock(subprocess.CompletedProcess)
        mock_response.returncode = self._returncode
        mock_response.stdout = json.dumps(
            {
                "attributes": {
                    "created": "2021-09-09T16:47:44+00:00",
                    "enabled": True,
                    "expires": None,
                    "notBefore": None,
                    "recoveryLevel": "Recoverable+Purgeable",
                    "updated": "2021-09-09T16:47:44+00:00",
                },
                "contentType": None,
                "id": f"{keyvault_url}/12345abcdef",
                "kid": None,
                "managed": None,
                "name": f"{secret_name}",
                "tags": {},
                "value": f"{self._secret_value}",
            }
        )
        mock_response.stderr = self._stderr

        return mock_response


@pytest.fixture()
def mock_subprocess_run(mocker):
    def _do_run(
        returncode=0,
        stderr="",
        secret_value=DEFAULT_SECRET_VALUE,
        side_effect=None,
    ):
        this_side_effect = MockSubprocessRun(
            returncode=returncode, secret_value=secret_value, stderr=stderr
        )
        if side_effect is not None:
            this_side_effect = side_effect

        mock_run = mocker.patch(
            "foodx_backup_source.azure.subprocess.run",
            side_effect=this_side_effect,
        )

        return mock_run

    return _do_run


class TestGetKvSecret:
    def test_clean(self, mock_subprocess_run):
        mock_subprocess_run()

        result = get_kv_secret("this-secret", "kv.some.where", "my_sub")

        assert result == "some-secret-value"

    def test_clean_empty(self, mock_subprocess_run):
        mock_subprocess_run(secret_value="")

        result = get_kv_secret("this-secret", "kv.some.where", "my_sub")

        assert result is None

    def test_exit_nonzero(self, mock_subprocess_run):
        mock_subprocess_run(returncode=1, stderr="some error")

        with pytest.raises(
            AzureKeyvaultError, match=r"^acquire keyvault secret failed"
        ):
            get_kv_secret("this-secret", "kv.some.where", "my_sub")
