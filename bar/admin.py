from django.contrib             import admin
from swingtix.bookkeeper.models import BookSet, Account, AccountEntry, Transaction

from bar.models import FoodStuff, FoodProvider, Purchase, CashBox
from bar.models import Recipe, RecipeIngredient, Product, SaleOffer, Calculation


class AccountEntryInline(admin.TabularInline):
	model = AccountEntry


class AccountAdmin(admin.ModelAdmin):
	inlines = (AccountEntryInline,)


class PurchaseAdmin(admin.ModelAdmin):
	model        = Purchase
	list_display = ('stuff', 'provider', 'transaction_list')
	
	def transaction_list(self, obj):
		return ";".join(obj.transactions.values_list('description', flat=True))


class RecipeIngredientInline(admin.TabularInline):
	model = RecipeIngredient


class RecipeAdmin(admin.ModelAdmin):
	model   = Recipe
	inlines = (RecipeIngredientInline,)


class CalculationInline(admin.TabularInline):
	model = Calculation


class SaleOfferAdmin(admin.ModelAdmin):
	model        = SaleOffer
	inlines      = (CalculationInline,)
	list_display = ('product', 'price', 'is_actual')
	list_filter  = ('is_actual',)


admin.site.register(BookSet)
admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction)

admin.site.register(FoodStuff)
admin.site.register(FoodProvider)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(CashBox)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Product)
admin.site.register(SaleOffer, SaleOfferAdmin)
