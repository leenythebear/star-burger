from django.db import models


class Address(models.Model):
    address = models.CharField(
        max_length=200, verbose_name="Адрес", unique=True
    )
    lat = models.FloatField("Широта", null=True)
    lon = models.FloatField("Долгота", null=True)
    updated_at = models.DateTimeField("Дата обновления координат")

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = "адрес"
        verbose_name_plural = "адреса"
