from django.urls import path
from .import views

urlpatterns=[
    path('',views.home,name='home'),
    path('about/',views.about,name='about'),

    path('cart/',views.cart,name='cart'),
    path('checkout/',views.checkout,name='checkout'),
    path('order_success/',views.order_success,name='order_success'),
    path('myorders/',views.myorders,name='myorders'),
    path('myorderdetail/',views.myorderdetail,name='myorderdetail'),
    path('cancel_order_user/',views.cancel_order_user,name='cancel_order_user'),
    path('cancel_order_seller/',views.cancel_order_seller,name='cancel_order_seller'),
    path('invoice/<int:id>/',views.invoice,name='invoice'),

    path('contact/',views.contact,name='contact'),
    path('home/',views.home,name='home'),
    path('services/',views.services,name='services'),
    path('shop/',views.shop,name='shop'),
    path('thankyou/',views.thankyou,name='thankyou'),
    path('blog/',views.blog,name='blog'),
    
    path('register/',views.register,name='register'),
    path('loginpage/',views.loginpage,name='loginpage'),
    path('logoutpage/',views.logoutpage,name='logoutpage'),


    path('increasequantity/',views.increasequantity,name='increasequantity'),
    path('decreasequantity/',views.decreasequantity,name='decreasequantity'),
    path('removecartproduct/',views.removecartproduct,name='removecartproduct'),









    path('seller/',views.seller_login,name='seller_login'),
    path('seller_register/',views.seller_register,name='seller_register'),
    path('seller_login/',views.seller_login,name='seller_login'),
    path('seller_logoutpage/',views.seller_logoutpage,name='seller_logoutpage'),
    

    path('seller_index/',views.seller_index,name='seller_index'),

    path('seller_products/',views.seller_products,name='seller_products'),
    path('seller_product_details/',views.seller_product_details,name='seller_product_details'),
    path('seller_edit_product/<int:id>',views.seller_edit_product,name='seller_edit_product'),
    path('seller_edit_profile/',views.seller_edit_profile,name='seller_edit_profile'),
    path('seller_delete_product/',views.seller_delete_product,name='seller_delete_product'),


    path('seller_add_product/',views.seller_add_product,name='seller_add_product'),
    path('seller_orders/',views.seller_orders,name='seller_orders'),
    path('seller_order_details/<int:id>',views.seller_order_details,name='seller_order_details'),
    path('seller_update_order_status/<int:id>/<str:status>/',views.seller_update_order_status,name='seller_update_order_status'),
    path('seller_profile/',views.seller_profile,name='seller_profile'),
    path('seller_analytics/',views.seller_analytics,name='seller_analytics'),

    path('admin_index/',views.admin_index,name='admin_index'),
    path('admin_users/',views.admin_users,name='admin_users'),
    path('admin_sellers/',views.admin_sellers,name='admin_sellers'),
    path('admin_register/',views.admin_register,name='admin_register'),
    path('admin_login/',views.admin_login,name='admin_login'),
    path('admin_analytics/',views.admin_analytics,name='admin_analytics'),
    path('admin_orders/',views.admin_orders,name='admin_orders'),
    path('admin_products/',views.admin_products,name='admin_products'),
    path('admin_product_details/',views.admin_product_details,name='admin_product_details'),
    path('admin_contacts/',views.admin_contacts,name='admin_contacts'),
    path('admin_contact_details/<int:id>',views.admin_contact_details,name='admin_contact_details'),
    path('admin_logoutpage/',views.admin_logoutpage,name='admin_logoutpage'),
    path('admin_update_order_status/<int:id>/<str:status>/',views.admin_update_order_status,name='admin_update_order_status'),


    # path('<path:exception>/', views.pagenotfound,name='pagenotfound')

]