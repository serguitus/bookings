import unittest
from django.test import TestCase

# Create your tests here.

class BookingTest(TestCase):
    fixtures = ['booking/fixtures.json']
    def test_details(self):
        # Issue a GET request.
        response = self.client.get('/bookings/login/')
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/bookings/login/', {'username':'test', 'password':'test'})
        self.assertEqual(response.status_code, 302)
        # print(response.__dict__)
        # getting list of bookings...
        response = self.client.get('/bookings/booking/booking/')
        # print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select Booking to change')
        # getting list of BaseBookingServices...
        response = self.client.get('/bookings/booking/basebookingservice/')
        # print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select BaseBookingService to change')

        # Check that the rendered context contains 5 customers.
        # self.assertEqual(len(response.context['customers']), 5)