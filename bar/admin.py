from django.contrib             import admin
from swingtix.bookkeeper.models import BookSet, Account, AccountEntry, Transaction

from bar.models import FoodStuff, FoodProvider, Purchase, CashBox


class AccountEntryInline(admin.TabularInline):
	model = AccountEntry


class AccountAdmin(admin.ModelAdmin):
	inlines = (AccountEntryInline,)


class PurchaseAdmin(admin.ModelAdmin):
	model        = Purchase
	list_display = ('stuff', 'provider', 'transaction_list')
	
	def transaction_list(self, obj):
		return ";".join(obj.transactions.values_list('description', flat=True))


admin.site.register(BookSet)
admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction)

admin.site.register(FoodStuff)
admin.site.register(FoodProvider)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(CashBox)

