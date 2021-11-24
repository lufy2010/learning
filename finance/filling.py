from dataclasses import dataclass, field
from typing import Dict
from bs4 import BeautifulSoup, Tag
import re
from datetime import datetime


class FilingFactKey:
    """FillingFactKey is the unique key of a filling fact"""

    def __init__(self, tag, end_date,  members) -> None:
        self.tag: str = tag
        self.end_date: int = end_date
        self.members: dict[str, str] = members

    def __hash__(self):
        return hash((self.tag,  self.end_date))

    def __eq__(self, other):
        result1 = self.members == other.members
        result2 = (self.tag,  self.end_date) == (other.tag,  other.end_date)
        return result1 and result2

    def __str__(self) -> str:
        return '{} {} {}'.format(self.tag,  self.end_date, self.members)


class FillingFact:
    def __init__(self, tag, members, end_date, qtrs, uom, value) -> None:
        self.key: FilingFactKey = FilingFactKey(tag, end_date,  members)
        self.uom: str = uom
        self.value: float = value
        self.qtrs = qtrs

    def __str__(self) -> str:
        return '{} {} {} {} {} {}'.format(self.key.tag, self.qtrs, self.key.end_date,
                                          self.uom, self.value, self.key.members)


@dataclass
class Filling:
    FILING_TYPE_10K = "10-K"
    FILING_TYPE_10Q = "10-Q"

    id: int = 0
    symbol: str = ""
    type: str = ""
    report_date: str = ""
    period_end_date: str = "",
    adsh: str = ""
    facts: Dict[FilingFactKey, FillingFact] = field(default_factory=dict)

    def get_fact_by_keystr(self, fact_keystr: str, end_date=None) -> FillingFact:
        parts = fact_keystr.split('#')
        if len(parts) == 1:
            return self.get_fact(fact_keystr, end_date)
        if len(parts) != 2:
            raise RuntimeError("illegal fact key string:{}".format(fact_keystr))
        members = dict(x.split("=") for x in parts[1].split(";"))
        return self.get_fact(parts[0], end_date, members)

    def get_fact(self, tag, end_date=None, members={}) -> FillingFact:
        if end_date is None:
            end_date = self.period_end_date
        return self.facts.get(FilingFactKey(tag.lower(), end_date, members))

    def add_fact(self, fact: FillingFact):
        if fact.key in self.facts:
            return
        self.facts[fact.key] = fact


class FillingContext(object):

    def __init__(self, id, end, qtrs, members) -> None:
        self.id: str = id
        self.qtrs: int = qtrs
        self.end_date: datetime = end
        self.members: dict[str, str] = members


class FillingParser(object):

    def _parse_context_members(self, ctx_tag) -> Dict[str, str]:
        member_tags = ctx_tag.find_all(name=re.compile("xbrldi:explicitMember",
                                                       re.IGNORECASE | re.MULTILINE))
        members = {}
        for member_tag in member_tags:
            dim = member_tag.attrs['dimension']
            val = member_tag.text
            if val.endswith("Member"):
                val = val[:-6]
            members[dim] = val
        return members

    def _parse_context_period_date(self, period_tag, name) -> datetime:
        date_tag = period_tag.find(name=re.compile(name,
                                                   re.IGNORECASE | re.MULTILINE))
        if not date_tag:
            return None
        return datetime.strptime(re.compile('[^\\d]+')
                                 .sub('', date_tag.text)[:8], "%Y%m%d")

    def _parse_contexts(self, xbrl) -> Dict[str, FillingContext]:
        context_tags = xbrl.find_all(name=re.compile("context",
                                     re.IGNORECASE | re.MULTILINE))
        ctx_dict = {}
        for ctx_tag in context_tags:
            context_id = ctx_tag.attrs['id']
            period = ctx_tag.find("period")
            if not period:
                continue
            end_date = self._parse_context_period_date(period, "endDate")
            if end_date:
                start_date = self._parse_context_period_date(period, "startDate")
                qtrs = int((end_date-start_date).days/90)
            else:
                end_date = self._parse_context_period_date(period, "instant")
                if not end_date:
                    print("context enddate/instant not present:", context_id)
                    continue
                qtrs = 0
            members = self._parse_context_members(ctx_tag)
            ctx_dict[context_id] = FillingContext(context_id, end_date, qtrs, members)
        return ctx_dict

    def _parse_fact(self, element: Tag, contexts: Dict[str, FillingContext]) -> FillingFact:

        if not element.has_attr("contextref") or not element.has_attr("unitref"):
            raise RuntimeError("[{}] no contextref/unitref attribute".format(element.name))
        try:
            val = float(element.text)
        except ValueError:
            raise RuntimeError("[{}] element text is not a numbers".format(element.name))
        id = element.attrs['contextref']
        if id not in contexts.keys():
            raise RuntimeError("[{}] context not found:{}".format(element.name, id))
        ctx = contexts[id]

        fact = FillingFact(element.name, ctx.members, ctx.end_date.strftime("%Y-%m-%d"), ctx.qtrs,
                           element.attrs["unitref"], val)
        return fact

    def _pattern(self, name):
        return re.compile(name, re.IGNORECASE | re.MULTILINE)

    def parse(self, file_path) -> Filling:
        filling = Filling()
        with open(file_path, 'r') as f:
            xbrl = BeautifulSoup(f, "lxml").find('xbrl')
        if xbrl is None:
            raise Exception("not a xbrl")

        filling.symbol = xbrl.find(self._pattern("(dei:TradingSymbol)")).text
        filling.type = xbrl.find(self._pattern("(dei:DocumentType)")).text
        filling.period_end_date = xbrl.find(self._pattern("(dei:DocumentPeriodEndDate)")).text

        contexts = self._parse_contexts(xbrl)
        gaaps = xbrl.find_all(recursive=False, name=re.compile("^((?!(context)).)*:\\w*",
                                                               re.IGNORECASE | re.MULTILINE))

        for gaap in gaaps:
            try:
                fact = self._parse_fact(gaap, contexts)
                filling.add_fact(fact)
            except RuntimeError as e:
                print("parse fact fail:", e)

        return filling


class FillingRepository:
    def findall_by_symbol(self, symbol):
        pass

    def find_by_symbol_period(self, symbol, period):
        pass

    def save(self, filling: Filling):
        pass
