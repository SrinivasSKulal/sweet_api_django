from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from .models import Sweets


class AuthenticationTestCase(TestCase):
    """Test cases for register and login endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register'
        self.login_url = '/api/auth/login'
    
    def test_register_success(self):
        """Test successful user registration"""
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User created Successfully')
        self.assertTrue(User.objects.filter(username='testuser').exists())
    
    def test_register_duplicate_username(self):
        """Test registration with existing username"""
        User.objects.create_user(username='existing', password='Pass123!')
        data = {
            'username': 'existing',
            'password': 'NewPass123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_register_missing_fields(self):
        """Test registration without username or password"""
        response = self.client.post(self.register_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_weak_password(self):
        """Test registration with weak password"""
        data = {
            'username': 'testuser',
            'password': '123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_login_success(self):
        """Test successful login"""
        User.objects.create_user(username='testuser', password='TestPass123!')
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_login_invalid_credentials(self):
        """Test login with wrong password"""
        User.objects.create_user(username='testuser', password='TestPass123!')
        data = {
            'username': 'testuser',
            'password': 'WrongPassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], 'Invalid Credentials')


class SweetsTestCase(TestCase):
    """Test cases for sweets GET and POST endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.sweets_url = '/api/sweets'
        
        self.sweet1 = Sweets.objects.create(
            name='Gulab Jamun',
            category='Indian',
            price=Decimal('50.00'),
            quantity=100
        )
        self.sweet2 = Sweets.objects.create(
            name='Rasgulla',
            category='Bengali',
            price=Decimal('40.00'),
            quantity=50
        )
    
    def test_get_sweets_authenticated(self):
        """Test getting all sweets with authentication"""
        response = self.client.get(self.sweets_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_get_sweets_unauthenticated(self):
        """Test getting sweets without authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.sweets_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_sweet_success(self):
        """Test creating a new sweet"""
        data = {
            'name': 'Jalebi',
            'category': 'Indian',
            'price': '35.50',
            'quantity': 75
        }
        response = self.client.post(self.sweets_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Jalebi')
        self.assertEqual(Sweets.objects.count(), 3)
    
    def test_create_sweet_invalid_data(self):
        """Test creating sweet with missing required fields"""
        data = {
            'name': 'Incomplete Sweet'
            # Missing category, price, quantity
        }
        response = self.client.post(self.sweets_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SearchTestCase(TestCase):
    """Test cases for search endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.search_url = '/api/sweets/search/'
        
        Sweets.objects.create(name='Gulab Jamun', category='Indian', price=Decimal('50.00'), quantity=100)
        Sweets.objects.create(name='Rasgulla', category='Bengali', price=Decimal('40.00'), quantity=50)
        Sweets.objects.create(name='Barfi', category='Indian', price=Decimal('60.00'), quantity=30)
        Sweets.objects.create(name='Sandesh', category='Bengali', price=Decimal('45.00'), quantity=20)
    
    def test_search_by_name(self):
        """Test searching sweets by name"""
        response = self.client.get(self.search_url, {'name': 'Gulab'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Gulab Jamun')
    
    def test_search_by_category(self):
        """Test searching sweets by category"""
        response = self.client.get(self.search_url, {'category': 'Indian'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_search_by_min_price(self):
        """Test searching sweets with minimum price"""
        response = self.client.get(self.search_url, {'min_price': '50'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_search_by_max_price(self):
        """Test searching sweets with maximum price"""
        response = self.client.get(self.search_url, {'max_price': '45'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_search_by_price_range(self):
        """Test searching sweets within price range"""
        response = self.client.get(self.search_url, {'min_price': '40', 'max_price': '50'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_search_combined_filters(self):
        """Test searching with multiple filters"""
        response = self.client.get(self.search_url, {
            'category': 'Indian',
            'min_price': '55'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Barfi')
    
    def test_search_no_results(self):
        """Test searching with filters that return no results"""
        response = self.client.get(self.search_url, {'name': 'NonExistent'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class PurchaseTestCase(TestCase):
    """Test cases for purchase endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        
        self.sweet = Sweets.objects.create(
            name='Gulab Jamun',
            category='Indian',
            price=Decimal('50.00'),
            quantity=100
        )
        self.purchase_url = f'/api/sweets/{self.sweet.id}/purchase'
    
    def test_purchase_success(self):
        """Test successful purchase"""
        data = {'quantity': 10}
        response = self.client.post(self.purchase_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Purchase complete')
        self.assertEqual(response.data['purchased_quantity'], 10)
        self.assertEqual(response.data['total_cost'], 500.0)
        
        self.sweet.refresh_from_db()
        self.assertEqual(self.sweet.quantity, 90)
    
    def test_purchase_insufficient_quantity(self):
        """Test purchase with quantity exceeding available stock"""
        data = {'quantity': 150}
        response = self.client.post(self.purchase_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Insufficient funds')
    
    def test_purchase_invalid_quantity_zero(self):
        """Test purchase with zero quantity"""
        data = {'quantity': 0}
        response = self.client.post(self.purchase_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_purchase_invalid_quantity_negative(self):
        """Test purchase with negative quantity"""
        data = {'quantity': -5}
        response = self.client.post(self.purchase_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_purchase_invalid_quantity_string(self):
        """Test purchase with non-integer quantity"""
        data = {'quantity': 'ten'}
        response = self.client.post(self.purchase_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_purchase_nonexistent_sweet(self):
        """Test purchase for non-existent sweet"""
        url = '/api/sweets/99999/purchase'
        data = {'quantity': 5}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_purchase_default_quantity(self):
        """Test purchase without specifying quantity (default=1)"""
        response = self.client.post(self.purchase_url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['purchased_quantity'], 1)
        
        self.sweet.refresh_from_db()
        self.assertEqual(self.sweet.quantity, 99)


class RestockTestCase(TestCase):
    """Test cases for restock endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            password='regularpass'
        )
        
        self.sweet = Sweets.objects.create(
            name='Gulab Jamun',
            category='Indian',
            price=Decimal('50.00'),
            quantity=50
        )
        self.restock_url = f'/api/sweets/{self.sweet.id}/restock'
    
    def test_restock_success_admin(self):
        """Test successful restock by admin"""
        self.client.force_authenticate(user=self.admin_user)
        data = {'quantity': 50}
        response = self.client.post(self.restock_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['previous_quantity'], 50)
        self.assertEqual(response.data['new_quantity'], 100)
        
        self.sweet.refresh_from_db()
        self.assertEqual(self.sweet.quantity, 100)
    
    def test_restock_forbidden_regular_user(self):
        """Test restock attempt by non-admin user"""
        self.client.force_authenticate(user=self.regular_user)
        data = {'quantity': 50}
        response = self.client.post(self.restock_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Restock can only be done by a admin')
    
    def test_restock_missing_quantity(self):
        """Test restock without quantity field"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.restock_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Quantity is required')
    
    def test_restock_invalid_quantity_zero(self):
        """Test restock with zero quantity"""
        self.client.force_authenticate(user=self.admin_user)
        data = {'quantity': 0}
        response = self.client.post(self.restock_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_restock_invalid_quantity_negative(self):
        """Test restock with negative quantity"""
        self.client.force_authenticate(user=self.admin_user)
        data = {'quantity': -10}
        response = self.client.post(self.restock_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_restock_nonexistent_sweet(self):
        """Test restock for non-existent sweet"""
        self.client.force_authenticate(user=self.admin_user)
        url = '/api/sweets/99999/restock'
        data = {'quantity': 50}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UpdateDeleteTestCase(TestCase):
    """Test cases for update and delete endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            password='regularpass'
        )
        self.client.force_authenticate(user=self.regular_user)
        
        self.sweet = Sweets.objects.create(
            name='Gulab Jamun',
            category='Indian',
            price=Decimal('50.00'),
            quantity=100
        )
        self.update_url = f'/api/sweets/{self.sweet.id}'
    
    def test_update_sweet_success(self):
        """Test successful update of sweet"""
        data = {
            'name': 'Updated Gulab Jamun',
            'category': 'North Indian',
            'price': '55.00',
            'quantity': 120
        }
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Gulab Jamun')
        
        self.sweet.refresh_from_db()
        self.assertEqual(self.sweet.name, 'Updated Gulab Jamun')
    
    def test_update_sweet_partial(self):
        """Test partial update of sweet"""
        data = {
            'name': 'Gulab Jamun',
            'category': 'Indian',
            'price': '60.00',
            'quantity': 100
        }
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.sweet.refresh_from_db()
        self.assertEqual(float(self.sweet.price), 60.0)
    
    def test_update_nonexistent_sweet(self):
        """Test update for non-existent sweet"""
        url = '/api/sweets/99999'
        data = {'name': 'Test', 'category': 'Test', 'price': '10', 'quantity': 10}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_sweet_as_admin(self):
        """Test deleting sweet as admin"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.update_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Sweets.objects.filter(id=self.sweet.id).exists())
    
    def test_delete_sweet_as_regular_user(self):
        """Test deleting sweet as non-admin (should fail)"""
        response = self.client.delete(self.update_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Sweets.objects.filter(id=self.sweet.id).exists())
    
    def test_delete_nonexistent_sweet(self):
        """Test delete for non-existent sweet"""
        self.client.force_authenticate(user=self.admin_user)
        url = '/api/sweets/99999'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)