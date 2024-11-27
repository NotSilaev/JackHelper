from django.db import models


class SalaryMetric(models.Model):
    employee = models.CharField(max_length=256)
    city = models.CharField(max_length=3)
    year = models.IntegerField()
    month = models.IntegerField()
    metric_amount = models.IntegerField()
    metric_comment = models.TextField(null=True, blank=True)
    metric_type = models.CharField(max_length=10)

    class Meta:
        db_table = 'salaries'

    def __str__(self):
        return f'{self.employee}-{self.city}-{self.year}-{self.month}'