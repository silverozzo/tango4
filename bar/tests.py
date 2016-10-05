from django.test import TestCase
from swingtix.bookkeeper.models import BookSet

from models import (
    BOOKSET_MATERIAL_DESCRIPTION, BOOKSET_MONETARY_DESCRIPTION,
    CASHBOX_MAIN_CODE_NAME,
    get_bookset, get_main_cashbox,
    CashBox, FoodStuff, Recipe, RecipeIngredient, Product, SaleOffer,
    Calculation, FoodProvider, Purchase,
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
    def test_save(self):
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

    def test_gets(self):
        stuff = FoodStuff(name='foobar 2')
        stuff.save()

        self.assertEqual(0, stuff.get_material_count())
        self.assertEqual(0, stuff.get_unit_cost())
        self.assertFalse(stuff.is_feasible())

        provider = FoodProvider(name='some provider')
        provider.save()

        purchase = Purchase(
            provider   = provider,
            stuff      = stuff,
            cost       = 200,
            unit_count = 10,
            unit_size  = 1,
        )
        purchase.save()

        self.assertEqual(10, stuff.get_material_count())
        self.assertEqual(20, stuff.get_unit_cost())
        self.assertTrue(stuff.is_feasible())


class RecipeTests(TestCase):
    def test_str(self):
        recipe = Recipe.objects.create(name='some recipe')
        self.assertEqual('some recipe', str(recipe))


class RecipeIngredientTests(TestCase):
    def test_str(self):
        stuff = FoodStuff(name='some stuff')
        stuff.save()

        recipe = Recipe(name='some recipe')
        recipe.save()

        ingredient = RecipeIngredient(
            stuff  = stuff,
            recipe = recipe,
            count  = 1.5
        )
        ingredient.save()

        self.assertEqual('some stuff x 1.5', str(ingredient))


class ProductTests(TestCase):
    def setUp(self):
        stuff = FoodStuff(name='some stuff 2')
        stuff.save()

        recipe = Recipe(name='some recipe 2')
        recipe.save()

        ingredient = RecipeIngredient(stuff=stuff, recipe=recipe, count=1.5)
        ingredient.save()

        self.product = Product(name='some product 2', recipe=recipe)
        self.product.save()

    def test_str(self):
        self.assertEqual('some product 2', str(self.product))

    def test_prepare_price(self):
        check = self.product.prepare_price(100)
        self.assertEqual(100, check)

        self.product.markup = 2
        check = self.product.prepare_price(100)
        self.assertEqual(200, check)

        self.product.markup = 1.44
        check = self.product.prepare_price(100)
        self.assertEqual(150, check)


class SaleOfferTests(TestCase):
    def setUp(self):
        stuff = FoodStuff(name='some stuff 3')
        stuff.save()

        recipe = Recipe(name='some recipe 3')
        recipe.save()

        ingredient = RecipeIngredient(stuff=stuff, recipe=recipe, count=1.5)
        ingredient.save()

        self.product = Product(name='some product 3', recipe=recipe)
        self.product.save()

        self.offer = SaleOffer(product=self.product)
        self.offer.save()

    def test_str(self):
        self.assertEqual('some product 3', str(self.offer))

    def test_save_change_actual(self):
        self.assertEqual(True, self.offer.is_actual)

        offer_2 = SaleOffer(product=self.product)
        offer_2.save()

        self.offer.refresh_from_db()
        self.assertEqual(False, self.offer.is_actual)


class CalculationTests(TestCase):
    def setUp(self):
        stuff = FoodStuff(name='some stuff 4')
        stuff.save()

        recipe = Recipe(name='some recipe 4')
        recipe.save()

        self.ingredient = RecipeIngredient(
            stuff  = stuff,
            recipe = recipe,
            count  = 1.5
        )
        self.ingredient.save()

        self.product = Product(name='some product 4', recipe=recipe)
        self.product.save()

        self.offer = SaleOffer(product=self.product)
        self.offer.save()

    def test_create_with_only_material_count(self):
        check = Calculation.create(self.offer, self.ingredient)
        self.assertEqual(1.5, check.material_count)


class CashBoxTests(TestCase):
    def test_str(self):
        cashbox = CashBox(code_name='foobar')
        self.assertEqual('foobar', str(cashbox))

    def test_save(self):
        cashbox = CashBox(code_name='foobar')
        cashbox.save()
        self.assertIsNotNone(cashbox.account)
        self.assertEqual(
            BOOKSET_MONETARY_DESCRIPTION,
            cashbox.account.bookset.description
        )


class SaleTests(TestCase):
    pass


class FoodProviderTests(TestCase):
    def test_str(self):
        provider = FoodProvider(name='foobar')
        self.assertEqual('foobar', str(provider))

    def test_save(self):
        provider = FoodProvider(name='foobar')
        provider.save()
        self.assertIsNotNone(provider.material_account)
        self.assertEqual(
            BOOKSET_MATERIAL_DESCRIPTION,
            provider.material_account.bookset.description
        )
        self.assertIsNotNone(provider.monetary_account)
        self.assertEqual(
            BOOKSET_MONETARY_DESCRIPTION,
            provider.monetary_account.bookset.description
        )


class PurchaseTests(TestCase):
    def test_save(self):
        stuff = FoodStuff(name = 'some stuff')
        stuff.save()

        provider = FoodProvider(name='some provider')
        provider.save()

        purchase = Purchase(
            provider   = provider,
            stuff      = stuff,
            cost       = 100,
            unit_count = 10,
            unit_size  = 1,
        )
        purchase.save()

        self.assertEqual(3, purchase.transactions.count())

        self.assertEqual(10, stuff.material_account.balance())
        self.assertEqual(100, stuff.monetary_account.balance())

        self.assertEqual(-10, provider.material_account.balance())

        main_cashbox = get_main_cashbox()
        self.assertEqual(-100, main_cashbox.account.balance())
