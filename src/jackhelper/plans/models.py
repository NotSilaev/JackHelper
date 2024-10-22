from django.db import models


class Plan(models.Model):
    city = models.CharField(max_length=3)
    year = models.IntegerField()
    month = models.IntegerField()
    revenue = models.IntegerField()
    works_revenue = models.IntegerField()
    spare_parts_revenue = models.IntegerField()
    normal_hours = models.IntegerField()

    class Meta:
        db_table = 'plans'

    def __str__(self):
        return f'{self.city}-{self.year}-{self.month}'