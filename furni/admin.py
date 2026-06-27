from django.contrib import admin
from .models import product,Cart,order,orderdetail,payment
# Register your models here.

admin.site.register(product)
admin.site.register(Cart)
admin.site.register(order)
admin.site.register(orderdetail)
admin.site.register(payment)