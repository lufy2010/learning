from typing import List, Dict, Tuple


class ValueSource:
    def get_value(self, tag) -> Tuple[str, float]:
        pass


class ValueTarget:
    def set_value(self, tag, uom, value):
        pass


class RuleFactor:
    def __init__(self, weight, tag) -> None:
        self.weight: float = weight
        self.tag: str = tag


class Rule:
    def __init__(self,  uom, tag, rule_factors: Dict[str, float]) -> None:
        self.tag = tag
        self.uom = uom
        self.rule_factors: Dict[str, RuleFactor] = {}
        for sub_tag, weight in rule_factors.items():
            self.rule_factors[sub_tag] = RuleFactor(weight, sub_tag)

    def apply(self, source: ValueSource, target: ValueTarget):
        total = 0.0
        uom = self.uom
        for factor in self.rule_factors.values():
            uomval = source.get_value(factor.tag)
            if uomval is None:
                raise Exception("value not found:{}".format(factor.tag))
            if len(uom) == 0:
                uom = uomval[0]
            elif uom != uomval[0]:
                raise Exception("uom not same:want {},but {}".format(uom, uomval[0]))
            total = total + uomval[1]*factor.weight
        print("rule :", self.tag, ",value:", total)
        target.set_value(self.tag, uom, total)


class RuleGroup:
    def __init__(self, rules) -> None:
        self.rules: List[Rule] = rules

    def apply(self, source: ValueSource, target: ValueTarget):
        for rule in self.rules:
            rule.apply(source, target)

    def __str__(self) -> str:
        return "rule count:{},tags:{}".format(len(self.rules),
                                              ' '.join([r.tag for r in self.rules]))


class RuleGroupBuilder:
    def __init__(self) -> None:
        self.rules: Dict[str, Rule] = {}
        self.indegrees: Dict[str, int] = {}

    def _find_zero_indegrees(self) -> List[str]:
        tags = []
        for tag, indegree in list(self.indegrees.items()):
            if indegree != 0:
                continue
            tags.append(tag)
            self.indegrees.pop(tag)
            rule = self.rules.get(tag)
            if rule is None:
                continue
            for sub_tag in rule.rule_factors.keys():
                indegree = self.indegrees.get(sub_tag)
                if indegree is None:
                    continue
                self.indegrees[sub_tag] = indegree-1
        return tags

    def build(self) -> RuleGroup:
        rules: List[Rule] = []
        while len(self.indegrees) > 0:
            tags = self._find_zero_indegrees()
            if len(tags) == 0:
                raise Exception("illegal rule tree")
            for tag in tags:
                rule = self.rules.get(tag)
                if rule is None:
                    continue
                rules.append(rule)
        rules.reverse()
        return RuleGroup(rules)

    def simple_rule(self, tag, factor):
        return self.rule(tag, "", {factor: 1})

    def rule(self, tag, uom, factors: Dict[str, float]):
        if self.rules.get(tag) is not None:
            raise Exception("tag already exists:{}".format(tag))
        self.rules[tag] = Rule(uom, tag, factors)
        self.indegrees[tag] = self.indegrees.get(tag, 0)
        for sub_tag in factors.keys():
            indegree = self.indegrees.get(sub_tag, 0)+1
            self.indegrees[sub_tag] = indegree
        return self
