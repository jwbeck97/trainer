from gretel_client.projects.models import read_model_config

from gretel_trainer.relational.model_config import (
    make_synthetics_config,
    make_transform_config,
)


def test_synthetics_config_prepends_workflow():
    config = make_synthetics_config("users", "synthetics/amplify")
    assert config["name"] == "synthetics-users"


def test_synthetics_config_handles_noncompliant_table_names():
    config = make_synthetics_config("hello--world", "synthetics/amplify")
    assert config["name"] == "synthetics-hello__world"


def test_transforms_config_prepends_workflow(mutagenesis):
    config = make_transform_config(mutagenesis, "atom", "transform/default")
    assert config["name"] == "transforms-atom"


def test_transforms_config_adds_passthrough_policy(mutagenesis):
    def get_policies(config):
        # default blueprint uses `transforms` model key
        return config["models"][0]["transforms"]["policies"]

    original = read_model_config("transform/default")
    original_policies = get_policies(original)

    xform_config = make_transform_config(mutagenesis, "atom", "transform/default")
    xform_config_policies = get_policies(xform_config)

    assert len(xform_config_policies) == len(original_policies) + 1
    assert xform_config_policies[1:] == original_policies
    assert xform_config_policies[0] == {
        "name": "ignore-keys",
        "rules": [
            {
                "name": "ignore-key-columns",
                "conditions": {"field_name": ["molecule_id", "atom_id"]},
                "transforms": [
                    {
                        "type": "passthrough",
                    }
                ],
            }
        ],
    }