from __future__ import unicode_literals

from decimal import Decimal, ROUND_UP
from django.db import models
from swingtix.bookkeeper.models import Account, BookSet, Transaction


BOOKSET_MATERIAL_DESCRIPTION = 'material'
BOOKSET_MONETARY_DESCRIPTION = 'monetary'
CASHBOX_MAIN_CODE_NAME       = 'cash'

PURCHASE_SUPPLY_MONETARY  = 'supply from provider to stuff'
PURCHASE_SUPPLY_MATERIAL  = 'supply from provider to stuff'
PURCHASE_DELIVERY_PAYMENT = 'payment for delivery'


def get_bookset(description):
    if BookSet.objects.filter(description=description).exists():
        return BookSet.objects.get(description=description)
    book = BookSet(description=description)
    book.save()
    return book


def get_main_cashbox():
    if CashBox.objects.filter(code_name=CASHBOX_MAIN_CODE_NAME).exists():
        return CashBox.objects.get(code_name=CASHBOX_MAIN_CODE_NAME)
    cash = CashBox(code_name=CASHBOX_MAIN_CODE_NAME)
    cash.save()
    return cash


class FoodStuff(models.Model):
    category = models.CharField(max_length=200)
    name = models.CharField(max_length=200, unique=True)
    material_account = models.OneToOneField(
        Account, blank=True, related_name='stuff')
    monetary_account = models.OneToOneField(
        Account, blank=True, related_name='food')

    def __unicode__(self):
        return self.category + ' ' + self.name

    def save(self, *args, **kwargs):
        if self.material_account_id is None:
            book = get_bookset(BOOKSET_MATERIAL_DESCRIPTION)
            account = Account(name=self.name, bookset=book)
            account.save()
            self.material_account = account
        if self.monetary_account_id is None:
            book = get_bookset(BOOKSET_MONETARY_DESCRIPTION)
            account = Account(name=self.name, bookset=book)
            account.save()
            self.monetary_account = account
        return super(FoodStuff, self).save(*args, **kwargs)

    def get_unit_cost(self, date=None):
        material_count = self.material_account.balance(date)
        monetary_count = self.monetary_account.balance(date)
        if material_count == 0:
            return 0

        return monetary_count / material_count

    def is_feasible(self, date=None):
        if self.material_account.balance(date) > 0:
            return True
        return False

    def get_material_count(self, date=None):
        return self.material_account.balance(date)


class Recipe(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='ingredients')
    stuff = models.ForeignKey(FoodStuff)
    count = models.DecimalField(max_digits=8, decimal_places=2)
    comment = models.CharField(max_length=200, blank=True, default='')

    def __unicode__(self):
        return self.stuff.name + ' x ' + str(self.count)


class Product(models.Model):
    name = models.CharField(max_length=200)
    recipe = models.OneToOneField(Recipe)
    is_active = models.BooleanField(default=True)
    fixed_price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0)
    rounding = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    markup = models.DecimalField(max_digits=8, decimal_places=2, default=1)

    def __unicode__(self):
        return self.name

    def prepare_price(self, cost):
        price = Decimal(cost * self.markup)
        price /= Decimal(10) ** int(self.rounding)
        price = price.quantize(Decimal(1), rounding=ROUND_UP)
        price *= Decimal(10) ** int(self.rounding)
        return price


class SaleOffer(models.Model):
    product = models.ForeignKey(Product)
    is_actual = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    when = models.DateTimeField(auto_now=True)
    feasible = models.BooleanField(default=False)

    def __unicode__(self):
        return self.product.name

    def save(self, *args, **kwargs):
        new_record = False
        if self.pk is None:
            new_record = True
        if self.is_actual:
            SaleOffer.objects.filter(product=self.product).update(
                is_actual=False)
        result = super(SaleOffer, self).save(*args, **kwargs)
        if not new_record:
            return result

        self.feasible = True
        full_cost = Decimal(0)
        for ingredient in self.product.recipe.ingredients.all():
            calc = Calculation.create(self, ingredient)
            if not calc.feasible:
                self.feasible = False
            full_cost += calc.monetary_count

        self.price = self.product.prepare_price(full_cost)

        result = super(SaleOffer, self).save(*args, **kwargs)

        return result


class Calculation(models.Model):
    sale_offer = models.ForeignKey(SaleOffer)
    ingredient = models.ForeignKey(RecipeIngredient)
    material_count = models.DecimalField(
        max_digits=8, decimal_places=2, default=0)
    monetary_count = models.DecimalField(
        max_digits=8, decimal_places=2, default=0)
    feasible = models.BooleanField(default=False)

    @staticmethod
    def create(offer, ingredient):
        monetary_count = ingredient.count * ingredient.stuff.get_unit_cost()
        feasible = ingredient.count <= ingredient.stuff.get_material_count()

        calc = Calculation(
            sale_offer     = offer,
            ingredient     = ingredient,
            material_count = ingredient.count,
            monetary_count = monetary_count,
            feasible       = feasible
        )
        calc.save()
        return calc


class CashBox(models.Model):
    name = models.CharField(max_length=200, default='')
    code_name = models.CharField(max_length=200, unique=True, default='')
    account = models.OneToOneField(Account, blank=True)

    def __unicode__(self):
        return self.code_name

    def save(self, *args, **kwargs):
        if self.account_id is None:
            book = get_bookset(BOOKSET_MONETARY_DESCRIPTION)
            account = Account(name=self.name, bookset=book)
            account.save()
            self.account = account
        return super(CashBox, self).save(*args, **kwargs)


class Sale(models.Model):
    offer = models.ForeignKey(SaleOffer)
    cashbox = models.ForeignKey(CashBox)
    transactions = models.ManyToManyField(
        Transaction, blank=True, editable=False)
    when = models.DateTimeField(auto_now=True)


class FoodProvider(models.Model):
    name = models.CharField(max_length=200)
    material_account = models.OneToOneField(
        Account, blank=True, related_name='supply')
    monetary_account = models.OneToOneField(
        Account, blank=True, related_name='cost')

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.material_account_id is None:
            book = get_bookset(BOOKSET_MATERIAL_DESCRIPTION)
            account = Account(name=self.name, bookset=book)
            account.save()
            self.material_account = account
        if self.monetary_account_id is None:
            book = get_bookset(BOOKSET_MONETARY_DESCRIPTION)
            account = Account(name=self.name, bookset=book)
            account.save()
            self.monetary_account = account
        return super(FoodProvider, self).save(*args, **kwargs)


class Purchase(models.Model):
    provider = models.ForeignKey(FoodProvider)
    stuff = models.ForeignKey(FoodStuff)
    transactions = models.ManyToManyField(
        Transaction, blank=True, editable=False)
    when = models.DateTimeField(auto_now=True)
    cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    unit_count = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    unit_size = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        new_record = False
        if self.id is None:
            new_record = True

        result = super(Purchase, self).save(*args, **kwargs)

        if not new_record:
            return result

        full_count = self.unit_count * self.unit_size

        res = self.stuff.material_account.post(
            full_count, self.provider.material_account,
            PURCHASE_SUPPLY_MATERIAL)
        self.transactions.add(res[0].transaction)

        res = self.stuff.monetary_account.post(
            self.cost, self.provider.monetary_account,
            PURCHASE_SUPPLY_MONETARY)
        self.transactions.add(res[0].transaction)

        cashbox = get_main_cashbox()
        res = self.provider.monetary_account.post(
            self.cost, cashbox.account, PURCHASE_DELIVERY_PAYMENT)
        self.transactions.add(res[0].transaction)

        return result
