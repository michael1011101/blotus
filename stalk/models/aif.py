from django.db import models
from lolly import Lolly


class Basic(Lolly):
    plat_id = models.CharField(max_length=20)
    date = models.CharField(max_length=20, null=True)
    turnover_amount = models.CharField(max_length=20, null=True)
    unconventional_turnover_amount = models.CharField(max_length=20, null=True)
    trade_amount = models.CharField(max_length=20, null=True)
    borrower_amount = models.CharField(max_length=20, null=True)
    investor_amount = models.CharField(max_length=20, null=True)
    different_borrower_amount = models.CharField(max_length=20, null=True)
    different_investor_amount = models.CharField(max_length=20, null=True)
    loan_balance = models.CharField(max_length=20, null=True)
    avg_full_time = models.CharField(max_length=20, null=True)
    product_overdue_rate = models.CharField(max_length=20, null=True)
    overdue_loan_amount = models.CharField(max_length=20, null=True)
    compensatory_amount = models.CharField(max_length=20, null=True)
    loan_overdue_rate = models.CharField(max_length=20, null=True)

    class Meta:
        app_label = 'stalk'
        db_table = 'aif_basic'
        unique_together = ('plat_id', 'date')


class Daily(Lolly):
    plat_id = models.CharField(max_length=20)
    date = models.CharField(max_length=20, null=True)
    daily_turnover = models.CharField(max_length=20, null=True)
    daily_trade_cnt = models.CharField(max_length=20, null=True)
    daily_invest_cnt = models.CharField(max_length=20, null=True)
    thityday_income = models.CharField(max_length=20, null=True)
    service_time = models.CharField(max_length=20, null=True)

    class Meta:
        app_label = 'stalk'
        db_table = 'aif_daily'
        unique_together = ('plat_id', 'date')

class MonthlyBasic(Lolly):
    plat_id = models.CharField(max_length=20)
    date = models.CharField(max_length=20, null=True)
    loan_amount_per_capita = models.CharField(max_length=20, null=True)
    avg_loan_per_trade = models.CharField(max_length=20, null=True)
    invest_amount_per_capita = models.CharField(max_length=20, null=True)
    avg_invest_per_trade = models.CharField(max_length=20, null=True)
    max_borrower_ratio = models.CharField(max_length=20, null=True)
    topten_borrowers_ratio = models.CharField(max_length=20, null=True)
    overdue_project_amount = models.CharField(max_length=20, null=True)
    avg_interest_rate = models.CharField(max_length=20, null=True)
    avg_borrow_period = models.CharField(max_length=20, null=True)

    class Meta:
        app_label = 'stalk'
        db_table = 'aif_monthly_basic'
        unique_together = ('plat_id', 'date')
