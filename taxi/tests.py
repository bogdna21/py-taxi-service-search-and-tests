from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from taxi.forms import DriverCreationForm
from taxi.models import Manufacturer, Car, Driver


class ModelsTest(TestCase):
    def test_manufacturer_str(self):
        manufacturer = Manufacturer.objects.create(name="test")
        self.assertEqual(str(manufacturer), f"{manufacturer.name} {manufacturer.country}")

    def test_driver_str(self):
        driver = get_user_model().objects.create_user(
            username="test",
            password="test123",
            first_name="Bob",
            last_name="Smith",
        )
        self.assertEqual(str(driver), f"{driver.username} ({driver.first_name} {driver.last_name})")

    def test_car_str(self):
        manufacturer = Manufacturer.objects.create(name="test")
        driver = get_user_model().objects.create_user(
            username="test",
            password="test123",
            first_name="Bob",
            last_name="Smith",
        )
        car = Car.objects.create(
            model="test_car",
            manufacturer=manufacturer,
        )
        car.drivers.set([driver])
        self.assertEqual(str(car), car.model)


class PublicCarTest(TestCase):

    def setUp(self):
        self.client = Client()

    """Testing car-views for client, who don't login """
    def test_login_required(self):
        url = reverse("taxi:car-list")
        res = self.client.get(url)
        self.assertNotEqual(res.status_code, 200)


class PrivateCarTest(TestCase):
    """"Testing for logined client"""
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test123",
        )
        self.client.force_login(self.user)

    def test_retrieve_car(self):
        manufacturer = Manufacturer.objects.create(name="test")
        Car.objects.create(model="test", manufacturer=manufacturer)
        url = reverse("taxi:car-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        cars = Car.objects.all()
        self.assertEqual(list(res.context["car_list"]), list(cars))
        self.assertTemplateUsed(res, "taxi/car_list.html")

    def test_create_driver(self):
        form_data = {
            "username": "tesla",
            "first_name": "test123",
            "last_name": "test123",
            "license_number": "BOB09631",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        }

        response = self.client.post(reverse("taxi:driver-create"), data=form_data)

        # перевірка, що форма пройшла успішно (редірект)
        self.assertEqual(response.status_code, 302)

        # тепер можна шукати
        new_driver = Driver.objects.get(license_number=form_data["license_number"])
        self.assertEqual(new_driver.username, form_data["username"])
