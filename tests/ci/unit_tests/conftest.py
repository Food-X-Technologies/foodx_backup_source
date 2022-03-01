#  Copyright (c) 2022 Food-X Technologies
#
#  This file is part of foodx_backup_source.
#
#  You should have received a copy of the MIT License along with
#  foodx_backup_source. If not, see <https://opensource.org/licenses/MIT>.

import pytest
import ruamel.yaml


@pytest.fixture()
def load_yaml_content():
    def _load(content_text: str) -> dict:
        yaml = ruamel.yaml.YAML(typ="safe")
        content = yaml.load(content_text)

        return content

    return _load
