from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, F, DecimalField
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField("название", max_length=50)
    address = models.CharField(
        "адрес",
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        "контактный телефон",
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = "ресторан"
        verbose_name_plural = "рестораны"

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = RestaurantMenuItem.objects.filter(
            availability=True
        ).values_list("product")
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField("название", max_length=50)

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("название", max_length=50)
    category = models.ForeignKey(
        ProductCategory,
        verbose_name="категория",
        related_name="products",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        "цена",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    image = models.ImageField("картинка")
    special_status = models.BooleanField(
        "спец.предложение",
        default=False,
        db_index=True,
    )
    description = models.TextField(
        "описание",
        max_length=255,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name="menu_items",
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="menu_items",
        verbose_name="продукт",
    )
    availability = models.BooleanField(
        "в продаже", default=True, db_index=True
    )

    class Meta:
        verbose_name = "пункт меню ресторана"
        verbose_name_plural = "пункты меню ресторана"
        unique_together = [["restaurant", "product"]]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def total_price(self):
        total_prices = self.annotate(
            total_price=Sum(
                F("products__price") * F("products__quantity"),
                output_field=DecimalField(),
            )
        )
        return total_prices


class Order(models.Model):
    CREATED = "CREATED"
    PREPARING = "PREPARING"
    READY = "READY"
    DELIVERING = "DELIVERING"
    FINISHED = "FINISHED"
    STATUS_CHOICES = [
        (CREATED, "Создан"),
        (PREPARING, "Готовится"),
        (READY, "Готов"),
        (DELIVERING, "Доставляется"),
        (FINISHED, "Закончен"),
    ]
    CASH = "CASH"
    CARD = "CARD"
    NOT_CHOSEN = "NOT_CHOSEN"
    PAYMENT_CHOICES = [
        (CASH, "Наличными курьеру"),
        (CARD, "Картой онлайн"),
        (NOT_CHOSEN, "Не выбран"),
    ]

    firstname = models.CharField(
        max_length=200, verbose_name="Имя", db_index=True, null=False
    )
    lastname = models.CharField(
        max_length=200, verbose_name="Фамилия", db_index=True
    )
    phonenumber = PhoneNumberField(verbose_name="Телефон", db_index=True)
    address = models.CharField(max_length=200, db_index=True)
    status = models.CharField(
        max_length=50,
        verbose_name="Статус",
        choices=STATUS_CHOICES,
        default=CREATED,
    )
    comment = models.TextField(verbose_name="Комментарий", blank=True)
    created_at = models.DateTimeField(
        verbose_name="Дата  и время создания заказа", default=timezone.now
    )
    called_at = models.DateTimeField(
        verbose_name="Дата и время звонка", null=True, blank=True
    )
    delivered_at = models.DateTimeField(
        verbose_name="Дата и время доставки", null=True, blank=True
    )
    payment_type = models.CharField(
        max_length=50,
        verbose_name="Способ оплаты",
        choices=PAYMENT_CHOICES,
        default=NOT_CHOSEN,
    )
    responsible_restaurant = models.ForeignKey(
        Restaurant,
        verbose_name="назначенный ресторан",
        related_name="restaurant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    objects = OrderQuerySet.as_manager()

    def __str__(self):
        return f"{self.firstname}  {self.lastname}"

    def available_restaurants(self):
        restaurants = set()
        for product in self.products.all():
            available_restaurants = RestaurantMenuItem.objects.filter(
                product=product.product
            ).values_list("restaurant__name", "restaurant__address")
            if not restaurants:
                restaurants = set(available_restaurants)
            else:
                restaurants &= set(available_restaurants)
        return restaurants

    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "заказы"


class OrderProducts(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name="Заказ",
        related_name="products",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product, verbose_name="Продукт", on_delete=models.CASCADE
    )
    quantity = models.IntegerField(verbose_name="Количество", validators=[MinValueValidator(1)])
    price = models.DecimalField(
        verbose_name="цена",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return f"{self.product} {self.quantity}"

    class Meta:
        verbose_name = "товар в заказе"
        verbose_name_plural = "товары в заказе "
