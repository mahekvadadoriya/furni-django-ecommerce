from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class seller(models.Model):
    user=models.OneToOneField(User,on_delete=models.PROTECT)
    company=models.CharField(max_length=255)
    mobile=models.CharField(max_length=255)
    address=models.CharField(max_length=350)
    city=models.CharField(max_length=255)
    state=models.CharField(max_length=255)
    country=models.CharField(max_length=255)

    def __str__(self):
        return f"Company {self.company}  , Seller {self.user.username}"
    
class product(models.Model):
    seller=models.ForeignKey(seller,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    description=models.CharField(max_length=1000)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    stock=models.PositiveIntegerField()
    image=models.ImageField(upload_to='products/')
    created_at=models.DateTimeField(auto_now_add=True)
    isactive=models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
# class User(models.Model):

    
class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)

    product=models.ForeignKey(product,on_delete=models.PROTECT)
    quantity=models.PositiveIntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        return (self.product.price * self.quantity)

    def __str__(self):
        return self.product.name
    
class order(models.Model):
    user=models.ForeignKey(User,on_delete=models.PROTECT,null=True,blank=True)
    firstname=models.CharField(max_length=255)
    lastname=models.CharField(max_length=255)
    address=models.CharField(max_length=300)
    city=models.CharField(max_length=50)
    state=models.CharField(max_length=50)
    country=models.CharField(max_length=50)
    pincode=models.IntegerField()
    mobile=models.CharField(max_length=15)
    email=models.EmailField()
    shipping_firstname=models.CharField(max_length=255,null=True,blank=True)
    shipping_lastname=models.CharField(max_length=255,null=True,blank=True)
    shipping_address=models.CharField(max_length=300,null=True,blank=True)
    shipping_city=models.CharField(max_length=50,null=True,blank=True)
    shipping_state=models.CharField(max_length=50,null=True,blank=True)
    shipping_country=models.CharField(max_length=50,null=True,blank=True)
    shipping_pincode=models.IntegerField(null=True,blank=True)
    shipping_mobile=models.CharField(null=True,blank=True)
    shipping_email=models.EmailField(null=True,blank=True)
    totalpayment=models.DecimalField(max_digits=10,decimal_places=2)
    created_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(default="pending")

    def __str__(self):
        return f"Order {self.id}"
    
class orderdetail(models.Model):
    order=models.ForeignKey(order,on_delete=models.CASCADE)
    product=models.ForeignKey(product,on_delete=models.PROTECT)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    quantity=models.PositiveIntegerField()
    subtotal=models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - Order {self.order.id}"
    
    @property
    def subtotalorder(self):
        return self.price * self.quantity


class payment(models.Model):
    order=models.OneToOneField(order,on_delete=models.PROTECT)
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    payment_method=models.CharField(max_length=10)
    transaction_id=models.CharField(null=True,blank=True)
    status=models.CharField(max_length=20)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order.id}" 
    
class Contact(models.Model):

    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.firstname