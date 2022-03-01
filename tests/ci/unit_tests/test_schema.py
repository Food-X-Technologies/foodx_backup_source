#  Copyright (c) 2022 Food-X Technologies
#
#  This file is part of foodx_backup_source.
#
#  You should have received a copy of the MIT License along with
#  foodx_backup_source. If not, see <https://opensource.org/licenses/MIT>.

import pydantic
import pytest

from foodx_backup_source.schema import DependencyFile


def test_clean(load_yaml_content):
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

    assert data.context.dependencies["r1"].backup.branch_name == "master"


def test_bad_url(load_yaml_content):
    content_text = """
---
context:
  dependencies:
    r1:
      backup:
        repo_url: "git://some.where"
        branch_name: master
      docker:
        image_name: r1-image
        tag_prefix: pp-
      release:
        ref: "3.1.4"
"""
    with pytest.raises(pydantic.ValidationError):
        DependencyFile.parse_obj(load_yaml_content(content_text))
