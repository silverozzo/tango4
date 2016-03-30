from __future__ import unicode_literals

from django.db                  import models
from future.utils               import python_2_unicode_compatible
from swingtix.bookkeeper.models import Account, BookSet, Transaction


def get_bookset(description):
	if BookSet.objects.filter(description=description).exists():
		return BookSet.objects.get(description=description)
	book = BookSet(description=description)
	book.save()
	return book


def get_main_cashbox():
	if CashBox.objects.filter(code_name='cash').exists():
		return CashBox.objects.get(code_name='cash')
	cash = CashBox(code_name='cash')
	cash.save()
	return cash


class FoodStuff(models.Model):
	category         = models.CharField(max_length=200)
	name             = models.CharField(max_length=200, unique=True)
	material_account = models.OneToOneField(Account, blank=True, related_name='stuff')
	monetary_account = models.OneToOneField(Account, blank=True, related_name='food')
	
	def __unicode__(self):
		return self.category + ' ' + self.name
	
	def save(self, *args, **kwargs):
		if self.material_account_id is None:
			book    = get_bookset('material')
			account = Account(name=self.name, bookset=book)
			account.save()
			self.material_account = account
		if self.monetary_account_id is None:
			book    = get_bookset('monetary')
			account = Account(name=self.name, bookset=book)
			account.save()
			self.monetary_account = account
		return super(FoodStuff, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Recipe(models.Model):
	name = models.CharField(max_length=200)


@python_2_unicode_compatible
class RecipeIngredient(models.Model):
	recipe = models.ForeignKey(Recipe)
	count  = models.DecimalField(max_digits=8, decimal_places=2)


@python_2_unicode_compatible
class Product(models.Model):
	name        = models.CharField(max_length=200)
	recipe      = models.OneToOneField(Recipe)
	is_active   = models.BooleanField(default=True)
	fixed_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	rounding    = models.DecimalField(max_digits=8, decimal_places=2, default=1)
	markup      = models.DecimalField(max_digits=8, decimal_places=2, default=1)


@python_2_unicode_compatible
class SaleOffer(models.Model):
	product   = models.ForeignKey(Product)
	is_actual = models.BooleanField(default=True)
	price     = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	when      = models.DateTimeField(auto_now=True)


@python_2_unicode_compatible
class Calculation(models.Model):
	sale_offer     = models.ForeignKey(SaleOffer)
	ingredient     = models.ForeignKey(RecipeIngredient)
	material_count = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	monetary_count = models.DecimalField(max_digits=8, decimal_places=2, default=0)


class CashBox(models.Model):
	name      = models.CharField(max_length=200, default='')
	code_name = models.CharField(max_length=200, unique=True, default='')
	account   = models.OneToOneField(Account, blank=True)
	
	def __unicode__(self):
		return self.code_name
	
	def save(self, *args, **kwargs):
		if self.account_id is None:
			book    = get_bookset('monetary')
			account = Account(name=self.name, bookset=book)
			account.save()
			self.account = account
		return super(CashBox, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Sale(models.Model):
	offer        = models.ForeignKey(SaleOffer)
	cashbox      = models.ForeignKey(CashBox)
	transactions = models.ManyToManyField(Transaction, blank=True, editable=False)
	when         = models.DateTimeField(auto_now=True)


class FoodProvider(models.Model):
	name             = models.CharField(max_length=200)
	material_account = models.OneToOneField(Account, blank=True, related_name='supply')
	monetary_account = models.OneToOneField(Account, blank=True, related_name='cost')
	
	def __unicode__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		if self.material_account_id is None:
			book    = get_bookset('material')
			account = Account(name=self.name, bookset=book)
			account.save()
			self.material_account = account
		if self.monetary_account_id is None:
			book    = get_bookset('monetary')
			account = Account(name=self.name, bookset=book)
			account.save()
			self.monetary_account = account
		return super(FoodProvider, self).save(*args, **kwargs)


class Purchase(models.Model):
	provider     = models.ForeignKey(FoodProvider)
	stuff        = models.ForeignKey(FoodStuff)
	transactions = models.ManyToManyField(Transaction, blank=True, editable=False)
	when         = models.DateTimeField(auto_now=True)
	cost         = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	unit_count   = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	unit_size    = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	
	def save(self, *args, **kwargs):
		super(Purchase, self).save(*args, **kwargs)
		full_count = self.unit_count * self.unit_size
		
		res = self.stuff.material_account.post(full_count, self.provider.material_account, 
			'supply from provider to stuff')
		print(res)
		print(res[0])
		print(res[0].transaction)
		self.transactions.add(res[0].transaction)
		
		res = self.stuff.monetary_account.post(self.cost, self.provider.monetary_account, 
			'supply from provider to stuff')
		self.transactions.add(res[0].transaction)
		
		res = self.provider.monetary_account.post(self.cost, get_main_cashbox().account,
			'payment for delivery')
		self.transactions.add(res[0].transaction)
