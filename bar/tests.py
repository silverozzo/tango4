from django.test import TestCase

from bar.models import FoodStuff


class FoodStuffTests(TestCase):
	def test_simple(self):
		stuff1 = FoodStuff(name='foobar')
		stuff1.save()
