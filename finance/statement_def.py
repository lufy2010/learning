from finance.rule import RuleGroup, RuleGroupBuilder


class StatementDefinition:

    _default_stat_definitions = []

    def __init__(self, stat_type: str,  rule_group: RuleGroup) -> None:
        self.stat_type = stat_type
        self.rule_group = rule_group

    @staticmethod
    def make_income_sheet_definition():
        ASBCE = "filling/us-gaap:AllocatedShareBasedCompensationExpense"

        builder = RuleGroupBuilder()
        builder.simple_rule("income/Revenue", "filling/us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax")
        builder.simple_rule("income/CostOfRevenue", "filling/us-gaap:CostOfRevenue")
        builder.simple_rule("income/ResearchAndDevelopmentExpense", "filling/us-gaap:ResearchAndDevelopmentExpense")
        builder.simple_rule("income/SellingAndMarketingExpense", "filling/us-gaap:SellingAndMarketingExpense")
        builder.simple_rule("income/GeneralAndAdministrativeExpense", "filling/us-gaap:GeneralAndAdministrativeExpense")
        builder.simple_rule("income/CostsAndExpenses", "filling/us-gaap:CostsAndExpenses")
        builder.simple_rule("income/OperatingIncome", "filling/us-gaap:OperatingIncomeLoss")
        builder.simple_rule("income/NonoperatingIncomeExpense", "filling/us-gaap:NonoperatingIncomeExpense")
        builder.simple_rule(
            "income/IncomeBeforeProvisionForIncomeTaxes",
            "filling/us-gaap:IncomeLossFromContinuingOperationsBeforeIncome"
            "TaxesExtraordinaryItemsNoncontrollingInterest")
        builder.simple_rule("income/IncomeTaxExpenseBenefit", "filling/us-gaap:IncomeTaxExpenseBenefit")
        builder.simple_rule("income/NetIncome", "filling/us-gaap:NetIncomeLoss")
        builder.simple_rule("income/UndistributedEarningsLossAllocatedToParticipatingSecuritiesBasic",
                            "filling/us-gaap:UndistributedEarningsLossAllocatedToParticipatingSecuritiesBasic")
        builder.simple_rule("income/NetIncomeLossAvailableToCommonStockholdersBasic",
                            "filling/us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic")
        builder.simple_rule("income/EarningsPerShareBasic", "filling/us-gaap:EarningsPerShareBasic")
        builder.simple_rule("income/EarningsPerShareDiluted", "filling/us-gaap:EarningsPerShareDiluted")
        builder.simple_rule("income/WeightedAverageNumberOfSharesOutstandingBasic",
                            "filling/us-gaap:WeightedAverageNumberOfSharesOutstandingBasic")
        builder.simple_rule("income/WeightedAverageNumberOfSharesOutstandingDiluted",
                            "filling/us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding")
        builder.simple_rule("income/ASBCE", ASBCE)
        builder.simple_rule("income/ASBCECostOfSales", ASBCE+"#us-gaap:IncomeStatementLocationAxis=us-gaap:CostOfSales")
        builder.simple_rule("income/ASBCEResearchAndDevelopmentExpense",
                            ASBCE+"#us-gaap:IncomeStatementLocationAxis=us-gaap:ResearchAndDevelopmentExpense")
        builder.simple_rule("income/ASBCESellingAndMarketingExpense", ASBCE +
                            "#us-gaap:IncomeStatementLocationAxis=us-gaap:SellingAndMarketingExpense")
        builder.simple_rule("income/ASBCEGeneralAndAdministrativeExpense",
                            ASBCE+"#us-gaap:IncomeStatementLocationAxis=us-gaap:GeneralAndAdministrativeExpense")

        rg = builder.build()

        return StatementDefinition("income", rg)

    @classmethod
    def default_stat_definitions(cls):
        if len(cls._default_stat_definitions) == 0:
            cls._default_stat_definitions = [cls.make_income_sheet_definition()]
        return cls._default_stat_definitions
