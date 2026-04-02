import unittest

from agentworld.plugins import PluginRegistry
from agentworld.protocol import validate_pack_config


class DummyRulePack:
    name = "dummy_rule"
    version = "0.1"

    def config_schema(self):
        return {"required": ["policies"], "properties": {"policies": {"type": "object"}}}

    def build(self, config):
        return config


class PluginTests(unittest.TestCase):
    def test_registry(self):
        reg = PluginRegistry()
        reg.register("rule", DummyRulePack())
        meta = reg.list_meta()
        self.assertEqual(meta["rule"][0].name, "dummy_rule")

    def test_pack_schema_validate(self):
        schema = {"required": ["enabled"], "properties": {"enabled": {"type": "boolean"}}}
        issues = validate_pack_config(schema, {"enabled": "yes"})
        self.assertTrue(any(i.level == "error" for i in issues))


if __name__ == "__main__":
    unittest.main()
