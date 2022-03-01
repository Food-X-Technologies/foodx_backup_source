#  Copyright (c) 2022 Food-X Technologies
#
#  This file is part of foodx_backup_source.
#
#  You should have received a copy of the MIT License along with
#  foodx_backup_source. If not, see <https://opensource.org/licenses/MIT>.

"""Azure Cloud related functions."""

import json
import logging
import subprocess
import typing

log = logging.getLogger(__name__)


class AzureKeyvaultError(Exception):
    """Problem accessing a keyvault or keyvault secret."""


def get_kv_secret(
    secret_name: str, keyvault_fqdn: str, subscription: str
) -> typing.Optional[str]:
    """
    Acquire the value of a secret from the specified keyvault.

    Args:
        secret_name: Name of keyvault secret to acquire current value.
        keyvault_fqdn: FQDN of keyvault from which to acquire secret.
        subscription: Name or GUID of subscription where keyvault is deployed.

    Returns:
        Secret value or None if secret is empty or keyvault exists,
        but secret is not defined.
    Raises:
        AzureKeyvaultError: if a problem occurs accessing the keyvault.
    """
    try:
        logging.info(
            f"accessing keyvault, {keyvault_fqdn} (subscription {subscription})"
        )
        logging.info(f"acquiring azure keyvault secret, {secret_name}")

        command = [
            "az",
            "keyvault",
            "secret",
            "show",
            "--subscription",
            f"{subscription}",
            "--id",
            f"https://{keyvault_fqdn}/secrets/{secret_name}",
        ]
        result = subprocess.run(
            command, capture_output=True, check=True, text=True
        )

        acquired_json = json.loads(result.stdout)
        acquired_value = (
            acquired_json["value"] if acquired_json["value"] else None
        )

        return acquired_value
    except subprocess.SubprocessError as e:
        raise AzureKeyvaultError(
            f"acquire keyvault secret failed, {str(e)}"
        ) from e
