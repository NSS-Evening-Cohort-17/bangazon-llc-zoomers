import random
# import faker_commerce
# from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.core.management import call_command
from django.contrib.auth.models import User
from bangazon_api.helpers import STATE_NAMES
from bangazon_api.models import Category, Store
from bangazon_api.models.product import Product


class ProductTests(APITestCase):
    def setUp(self):
        """
        Set up for ProductTests
        """        
        url = '/api/register'
        
        user = {
            "first_name": "John",
            "last_name": "Doe", 
            "username": "johndoe11",
            "password": "me"
        }
        
        response = self.client.post(url, user, format='json')
            
        call_command('seed_db', user_count=3)
        # self.user1 = User.objects.filter(store__isnull=False).first()
        self.token = Token.objects.get(pk=response.data['token'])

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.category = Category.objects.create(name="Clothing")
        self.store = Store.objects.create(
            name="Rose, Johnson and Terrell",
            description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam elit.",
            is_active=1,
            seller_id=1)
        self.product = Product.objects.create(
            name="pants",
            store=self.store,
            price="5.0",
            description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam elit.",
            quantity="10",
            location="Tennessee",
            image_path="",
            category=self.category,
        )
        

        # self.faker = Faker()
        # self.faker.add_provider(faker_commerce.Provider)
        


    def test_create_product(self):
        """
        Ensure we can create a new product.
        """
        category = Category.objects.first()

        data = {
            "name": self.faker.ecommerce_name(),
            "price": random.randint(50, 1000),
            "description": self.faker.paragraph(),
            "quantity": random.randint(2, 20),
            "location": random.choice(STATE_NAMES),
            "imagePath": "",
            "categoryId": category.id
        }
        response = self.client.post('/api/products', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['id'])


    def test_update_product(self):
        """
        Ensure we can update a product.
        """
        product = Product.objects.first()
        data = {
            "name": product.name,
            "price": product.price,
            "description": self.faker.paragraph(),
            "quantity": product.quantity,
            "location": product.location,
            "imagePath": "",
            "categoryId": product.category.id
        }
        response = self.client.put(f'/api/products/{product.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        product_updated = Product.objects.get(pk=product.id)
        self.assertEqual(product_updated.description, data['description'])

    def test_get_all_products(self):
        """
        Ensure we can get a collection of products.
        """

        response = self.client.get('/api/products')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Product.objects.count())
        
    def test_delete_product(self):
        """
        Ensure we can delete an existing product.
        """
        url = f'/api/products/{self.product.id}'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
