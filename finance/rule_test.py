import unittest
from finance.rule import RuleGroupBuilder


class TestRuleGroupBuilder(unittest.TestCase):
    def test_build_succ(self):
        builder = RuleGroupBuilder()
        builder.rule("tag3", "usd", {"tag02": 2, "tag1": 5, "tag2": 6})
        builder.rule("tag1", "usd", {"tag01": 1, "tag02": 2})
        builder.rule("tag2", "usd", {"tag01": 3, "tag1": 4})
        builder.rule("tag4", "usd", {"tag01": 3, "tag1": 4})
        builder.rule("tag5", "usd", {"tag3": 3, "tag4": 4})
        rule_group = builder.build()
        self.assertEquals(["tag1", "tag2", "tag4", "tag3", "tag5"],
                          [r.tag for r in rule_group.rules])

    def test_build_fail(self):
        with self.assertRaises(Exception):
            builder = RuleGroupBuilder()
            builder.rule("tag3", "usd", {"tag02": 2, "tag1": 5, "tag2": 6})
            builder.rule("tag1", "usd", {"tag01": 1, "tag3": 2})
            builder.rule("tag2", "usd", {"tag01": 3, "tag1": 4})
            builder.build()
