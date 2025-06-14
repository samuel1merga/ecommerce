from django.db import models
from django.contrib.auth.models import User
# Create your models here.



class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # assuming supplier logs in
    company_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    address = models.TextField()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name
    

class Product(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    status = models.BooleanField(default=True) 
    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    address = models.TextField()
    payment_method = models.CharField(max_length=50)
    total = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    price = models.FloatField()
    quantity = models.IntegerField()