from typing import Dict, Tuple
from datetime import datetime
from pythonlangutil.overload import Overload, signature

from finance.filling import Filling
from finance.statement_def import StatementDefinition
from finance.rule import ValueSource, ValueTarget


class StatementItem:
    def __init__(self, tag,  uom, value) -> None:
        self.tag: str = tag
        self.uom: str = uom
        self.value: float = value

    def __str__(self) -> str:
        return '{} {} {}'.format(self.tag, self.uom, self.value)


class Statement:
    def __init__(self, stat_type) -> None:
        self.stat_type: str = stat_type
        self.items: Dict[str, StatementItem] = {}

    @Overload
    @signature("str", "str", "float")
    def add_item(self, tag, uom, value):
        self.items[tag] = StatementItem(tag, uom, value)

    @add_item.overload
    @signature("StatementItem")
    def add_item(self, stat_item):
        self.items[stat_item.tag] = stat_item

    def get_item(self, tag) -> StatementItem:
        return self.items.get(tag)

    def __str__(self) -> str:
        s = "======{}========\n".format(self.stat_type)

        for item in self.items.values():
            s += "{}: {}\n".format(item.tag, item.value)
        return s


class FinancialReport:

    def __init__(self) -> None:
        self.symbol: str = ""
        self.type: str = ""
        self.report_date: str = ""
        self.qtrs: int = 0
        self.end_date: datetime = None
        self.statements: Dict[str, Statement] = {}

    def __str__(self) -> str:
        s = "REPORT STATEMENTS:\n"
        for stat in self.statements.values():
            s = s+str(stat)
        return s

    def get_stat_item_value(self, stat_type, tag):
        item = self.get_stat_item(stat_type, tag)
        if item is None:
            return None
        return (item.uom, item.value)

    def get_stat_item(self, stat_type, tag) -> StatementItem:
        stat = self.statements.get(stat_type)
        if stat is None:
            return None
        return stat.get_item(tag)

    def add_stat_item(self, stat_type, stat_item):
        stat = self.statements.get(stat_type)
        if stat is None:
            raise Exception("statment not found:{}".format(stat_type))
        if type(stat_item) is tuple:
            stat_item = StatementItem(stat_item[0], stat_item[1], stat_item[2])
        stat.add_item(stat_item)

    def add_stat(self, stat: Statement):
        self.statements[stat.stat_type] = stat


def _parse_tag(tag) -> Tuple[str, str]:
    parts = tag.split('/', 2)
    if len(parts) != 2:
        raise Exception("illegal format. tag:{}".format(tag))
    return (parts[0], parts[1])


class FinancialSource(ValueSource):
    def __init__(self, filling: Filling, report: FinancialReport) -> None:
        self.report = report
        self.filling = filling

    def get_value(self, tag) -> Tuple[str, float]:
        type, tag = _parse_tag(tag)

        if type == "filling":
            fact = self.filling.get_fact_by_keystr(tag)
            if fact is None:
                return None
            return (fact.uom, fact.value)
        return self.report.get_stat_item_value(type, tag)


class FinancialTarget(ValueTarget):
    def __init__(self, report: FinancialReport) -> None:
        self.report = report

    def set_value(self, tag, uom, value):
        type, tag = _parse_tag(tag)
        self.report.add_stat_item(type, (tag, uom, value))


class FinancialFactory(object):

    def __init__(self, stat_definitions=None) -> None:
        self.stat_definitions = stat_definitions
        if stat_definitions is None:
            self.stat_definitions = StatementDefinition.default_stat_definitions()

    def create(self, filing: Filling) -> FinancialReport:
        report = FinancialReport()
        source = FinancialSource(filing, report)
        target = FinancialTarget(report)
        for stat_def in self.stat_definitions:
            stat = Statement(stat_def.stat_type)
            report.add_stat(stat)
            if stat_def.rule_group is not None:
                stat_def.rule_group.apply(source, target)
        return report
