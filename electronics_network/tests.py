from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import NetworkNode
from .admin import NetworkNodeAdmin
from django.contrib.admin.sites import AdminSite
from django.urls import resolve, Resolver404
from django.http import QueryDict


class NetworkNodeModelTest(TestCase):
    def setUp(self):
        self.node = NetworkNode.objects.create(
            name="Test Node",
            level=0,
            email="test@example.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="123"
        )

    def test_node_creation(self):
        self.assertTrue(isinstance(self.node, NetworkNode))
        self.assertEqual(self.node.__str__(), self.node.name)


class NetworkNodeAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.supplier = NetworkNode.objects.create(
            name='Supplier Node',
            level=0,
            email='supplier@example.com',
            country='Supplier Country',
            city='Supplier City',
            street='Supplier Street',
            house_number='123'
        )
        self.node_data = {
            'name': 'API Test Node',
            'level': 1,
            'email': 'apitest@example.com',
            'country': 'API Country',
            'city': 'API City',
            'street': 'API Street',
            'house_number': '456',
            'supplier': self.supplier
        }
        self.node = NetworkNode.objects.create(**self.node_data)
        self.post_data = self.node_data.copy()
        self.post_data['supplier'] = self.supplier.id

    def test_api_can_create_node(self):
        response = self.client.post('/api/network-nodes/', self.post_data, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_api_can_get_node(self):
        response = self.client.get(f'/api/network-nodes/{self.node.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.node.name)

    def test_api_can_update_node(self):
        change_node = {'name': 'Updated Node'}
        response = self.client.patch(f'/api/network-nodes/{self.node.id}/', change_node, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_can_delete_node(self):
        response = self.client.delete(f'/api/network-nodes/{self.node.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_api_cannot_update_debt(self):
        change_node = {'debt': 1000}
        response = self.client.patch(f'/api/network-nodes/{self.node.id}/', change_node, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_node = NetworkNode.objects.get(id=self.node.id)
        self.assertEqual(updated_node.debt, 0)  # Проверяем, что долг не изменился

    def test_api_filter_by_country(self):
        response = self.client.get('/api/network-nodes/?country=API Country', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)


class MockRequest:
    def __init__(self):
        self.COOKIES = {}
        self.META = {'SCRIPT_NAME': ''}
        self.GET = QueryDict('')
        self.POST = QueryDict('')
        self.method = 'GET'
        self.path = '/admin/electronics_network/networknode/'
        try:
            self.resolver_match = resolve(self.path)
        except Resolver404:
            self.resolver_match = None

    def get_host(self):
        return 'testserver'


class NetworkNodeAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = NetworkNodeAdmin(NetworkNode, self.site)
        self.user = User.objects.create_superuser('admin', 'admin@test.com', 'password')
        self.client.force_login(self.user)
        self.node = NetworkNode.objects.create(
            name='Test Node',
            level=1,
            email='test@example.com',
            country='Test Country',
            city='Test City',
            street='Test Street',
            house_number='123',
            debt=100
        )
        self.request = MockRequest()
        self.request.user = self.user

    def test_admin_list_display(self):
        response = self.admin.changelist_view(self.request)
        self.assertIn('name', self.admin.list_display)
        self.assertIn('level', self.admin.list_display)
        self.assertIn('city', self.admin.list_display)
        self.assertIn('supplier', self.admin.list_display)
        self.assertIn('debt', self.admin.list_display)

    def test_admin_list_filter(self):
        self.assertIn('level', self.admin.list_filter)
        self.assertIn('city', self.admin.list_filter)
        self.assertIn('country', self.admin.list_filter)

    def test_admin_search_fields(self):
        self.assertIn('name', self.admin.search_fields)
        self.assertIn('city', self.admin.search_fields)

    def test_admin_clear_debt_action(self):
        queryset = NetworkNode.objects.all()
        self.admin.clear_debt(self.request, queryset)
        self.node.refresh_from_db()
        self.assertEqual(self.node.debt, 0)

    def test_admin_page_load(self):
        response = self.client.get('/admin/electronics_network/networknode/')
        self.assertEqual(response.status_code, 200)