from django.test import TestCase
from swingtix.bookkeeper.models import BookSet

from models import (
    BOOKSET_MATERIAL_DESCRIPTION, BOOKSET_MONETARY_DESCRIPTION,
    CASHBOX_MAIN_CODE_NAME,
    CashBox, FoodStuff, get_bookset, get_main_cashbox
)


class GetFunctionsTests(TestCase):
    def test_get_bookset(self):
        existed = BookSet.objects.filter(description='foobar').count()
        self.assertEqual(0, existed)
        check = get_bookset('foobar')
        self.assertEqual('foobar', check.description)
        existed = BookSet.objects.filter(description='foobar').count()
        self.assertEqual(1, existed)

    def test_get_main_cashbox(self):
        existed = CashBox.objects.filter(
            code_name=CASHBOX_MAIN_CODE_NAME).count()
        self.assertEqual(0, existed)
        check = get_main_cashbox()
        self.assertEqual(CASHBOX_MAIN_CODE_NAME, check.code_name)
        existed = CashBox.objects.filter(
            code_name=CASHBOX_MAIN_CODE_NAME).count()
        self.assertEqual(1, existed)


class FoodStuffTests(TestCase):
    def test_simple(self):
        stuff = FoodStuff(name='foobar')
        stuff.save()
        self.assertIsNotNone(stuff.material_account)
        self.assertEqual(
            BOOKSET_MATERIAL_DESCRIPTION,
            stuff.material_account.bookset.description
        )
        self.assertIsNotNone(stuff.monetary_account)
        self.assertEqual(
            BOOKSET_MONETARY_DESCRIPTION,
            stuff.monetary_account.bookset.description
        )

    def test_get_unit_cost(self):
        stuff = FoodStuff(name='foobar 2')
        stuff.save()
        stuff.monetary_account
