from django.db import models



class StockRecord(models.Model):
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='stockrecords')
    buy_price = models.PositiveBigIntegerField(null=True, blank=True)
    sale_price = models.PositiveBigIntegerField()
    num_stock = models.PositiveIntegerField(default=0, )
    threshold_low_stack = models.PositiveIntegerField(null=True, blank=True)


    class Meta:
        verbose_name = 'Stock Record'
        verbose_name_plural = 'Stock Records'
    