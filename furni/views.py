from django.shortcuts import render,redirect
from django.urls import path
from django.template import loader
from .models import product,Cart,order,orderdetail,payment,seller,Contact
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from .decorators import logout_required,seller_required,seller_logout_required,admin_required,admin_logout_required
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.core.paginator import Paginator
from .helpers import paginate_queryset
from django.db.models import Q
from django.shortcuts import get_object_or_404

# Create your views here.
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def home(request):

    print("user  from user............................",request.user)


    products=product.objects.all()
    return render(request,'index.html',{'products':products})

@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def shop(request):

    products = product.objects.filter(stock__gt=0)

    search = request.GET.get('search', '').strip()

    if search:

        products = products.filter(

            Q(name__icontains=search) |

            Q(description__icontains=search)

        )

   

    return render(request,'shop.html',{'products':products,'search':search})

@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def cart(request):
        
        user=request.user
        userdata=User.objects.get(username=user)
        print("User...... from cart",request.user)

        cartdata=Cart.objects.filter(user=user).order_by('-id')
        print("1111111111111111",cartdata)
        print("22222222222222", request.method)
        if request.method=="POST":
            pid=request.POST['pid']
            products=product.objects.all() # for desplaying all products in shop
            data=product.objects.get(id=pid)
            if data.stock <= 0:

                messages.error(
                    request,
                    "Product is out of stock"
                )

                return redirect(
                    request.META.get(
                        'HTTP_REFERER',
                        'shop'
                    )
                )

            if Cart.objects.filter(product=data,user=user).exists():

                filtereddata = Cart.objects.get(
                    product=data,
                    user=user
                )

                if filtereddata.quantity >= data.stock:

                    messages.warning(
                        request,
                        "Maximum stock available in cart"
                    )

                    return redirect(
                        request.META.get(
                            'HTTP_REFERER',
                            'shop'
                        )
                    )

                filtereddata.quantity += 1

                filtereddata.save()

                messages.success(
                    request,
                    f"{data.name} added to cart"
                )

                return redirect(
                    request.META.get(
                        'HTTP_REFERER',
                        'shop'
                    )
                )
            else:
               

                new_cart = Cart.objects.create(
                    user=user,
                    product=data
                )

                messages.success(
                    request,
                    f"{data.name} added to cart"
                )

                return redirect(
                    request.META.get(
                        'HTTP_REFERER',
                        'shop'
                    )
                )

              


        # cartcount=Cart.objects.filter(user=userdata).aggregate(total=Sum('quantity'))['total'] or 0
        # print("cartcount.......",cartcount)
        # request.session['cart_count']=cartcount
        total=0

        for i in cartdata:
            total+=i.subtotal()
        return render(request,'cart.html',{'cartdata':cartdata,'total':total})

    

#for increase quantity in cart


@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def increasequantity(request):
    print(request)
    if request.method == "POST":

        cartid=request.POST['cartid']
        print("cartid.......",cartid)
        cartproduct=Cart.objects.get(id=cartid)
        

        if cartproduct.quantity >= cartproduct.product.stock:

            messages.error(
                request,
                "Maximum stock reached"
            )

            return redirect('cart')
        else:
            cartproduct.quantity += 1
            cartproduct.save()

    return redirect('cart')


#for decrease quantity in cart

@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def decreasequantity(request):
    print("Hellooooooo",request.method)
    if request.method == "POST":

        cartid=request.POST['cartid']
        cartproduct=Cart.objects.get(id=cartid)

        if cartproduct.quantity > 1:
            cartproduct.quantity-=1
            cartproduct.save()

        else :
            cartproduct.delete()

    return redirect('cart')


#for delete  in cart

@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def removecartproduct(request):
    if request.method=="POST":
        cartid=request.POST['cartid']
        cartproduct=Cart.objects.get(id=cartid)

        cartproduct.delete()
        print("----")

    return redirect('cart')


@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def checkout(request):
   
    cartdata=Cart.objects.filter(user=request.user)

    if not cartdata:
        return redirect('cart')
    
    total=0

    for i in cartdata:
        total+=i.subtotal()

    checkouttotal=total

    if request.method == "POST":
        
        print("Request is ......",request.method)
        firstname=request.POST.get('firstname')
        lastname=request.POST.get('lastname')

        address=request.POST.get('address')
        city=request.POST.get('city')
        state=request.POST.get('state')
        country=request.POST.get('country')
        pincode=request.POST.get('pincode')
        mobile=request.POST.get('mobile')
        email=request.POST.get('email')
        shipping_firstname=request.POST.get('shipping_firstname')
        shipping_lastname=request.POST.get('shipping_lastname')
        shipping_address=request.POST.get('shipping_address')
        shipping_city=request.POST.get('shipping_city')
        shipping_state=request.POST.get('shipping_state')
        shipping_country=request.POST.get('shipping_country')
        shipping_pincode=request.POST.get('shipping_pincode')
        shipping_mobile=request.POST.get('shipping_mobile')
        shipping_email=request.POST.get('shipping_email')
        totalpayment=request.POST.get('totalpayment')
        created_at=request.POST.get('created_at')
        # status=request.POST.get('status')
        payment_method=request.POST.get('payment_method')
        transaction_id=request.POST.get('transaction_id')

        if payment_method=="cod":
            status="pending"
        else:
            status="completed"


        errors=[]

        different_shipping=request.POST.get('c_ship_different_address')

        if not different_shipping:

                shipping_firstname=firstname
                shipping_lastname= lastname
                shipping_address=  address
                shipping_city=     city
                shipping_state=    state
                shipping_country=  country
                shipping_pincode=  pincode
                shipping_mobile=   mobile
                shipping_email=    email


        # for billing fields

        billing_fields={
            'firstname':firstname,
            'lastname':lastname,
            'address':address,
            'city':city,
            'state':state,
            'country':country,
            'pincode':pincode,
            'mobile':mobile,
            'email':email
        }

        for fieldname,fieldvalue in billing_fields.items():
            if not fieldvalue:
                errors.append(f"{fieldname} is required")

        if firstname and not re.match(r'^[A-Za-z ]+$',firstname):
            errors.append("firstname should contain only characters")
        
        if lastname and not re.match(r'^[A-Za-z ]+$',lastname):
            errors.append("lastname should contain only characters")

        if mobile:
            if not mobile.isdigit():
                errors.append("Mobile should contain only digits")
            
            if len(mobile)!=10:
                errors.append("Mobile should contain only 10 digits")
        if pincode:
            if not pincode.isdigit():
                errors.append("pincode should contain only digits")
            
            if len(pincode)!=6:
                errors.append("pincode should contain only 6 digits")

        if email :
            try:
                validate_email(email)

            except ValidationError:
                errors.append("Email is not valid (user12@gmail.com)")


        # for shipping fields



        if different_shipping:

            shipping_fields={
                'shipping_firstname':shipping_firstname,
                'shipping_lastname': shipping_lastname,
                'shipping_address':  shipping_address,
                'shipping_city':     shipping_city,
                'shipping_state':    shipping_state,
                'shipping_country':  shipping_country,
                'shipping_pincode':  shipping_pincode,
                'shipping_mobile':   shipping_mobile,
                'shipping_email':    shipping_email
            }

            

            for fieldname,fieldvalue in shipping_fields.items():
                if not fieldvalue:
                        errors.append(f"{fieldname} is required")

            if shipping_firstname and not re.match(r'^[A-Za-z ]+$',shipping_firstname):
                errors.append("shipping firstname should contain only characters")
            
            if shipping_lastname and not re.match(r'^[A-Za-z ]+$',shipping_lastname):
                errors.append("shipping lastname should contain only characters")

            if shipping_mobile:
                if not shipping_mobile.isdigit():
                    errors.append("shipping mobile should contain only digits")
                
                if len(shipping_mobile)!=10:
                    errors.append("Mobile should contain only 10 digits")
            if shipping_pincode:
                if not shipping_pincode.isdigit():
                    errors.append("pincode should contain only digits")
                
                if len(shipping_pincode)!=6:
                    errors.append("pincode should contain only 6 digits")

            if shipping_email :
                try:
                    validate_email(shipping_email)

                except ValidationError:
                    errors.append("Email is not valid (user12@gmail.com)")


        


        if errors:
            for error in errors:
                messages.error(request,error)

            return render(request,'checkout.html',{'cartdata':cartdata,'total':checkouttotal,'message':messages,'billing_fields':billing_fields,'formdata':request.POST})
       
        
        print("firstname ......",firstname)
        print("lastname ........",lastname)
        print("Mobile..................",mobile)
        print("Shipping Mobile..................",shipping_mobile)
        print("Pin code............................",pincode)
        print("Shipping Pincode....................",shipping_pincode)
       
        print("mobile =", mobile, type(mobile))
        print("shipping_mobile =", shipping_mobile, type(shipping_mobile))
        print("pincode =", pincode, type(pincode))
        print("shipping_pincode =", shipping_pincode, type(shipping_pincode))

        print("Before order creation..................")
      
        for item in cartdata:

            if item.quantity > item.product.stock:

                messages.error(
                    request,
                    f"{item.product.name} is out of stock"
                )

                return redirect('cart')
        new_order=order.objects.create(
            user=request.user,
            firstname=firstname,
            lastname=lastname,
            address=address,
            city=city,
            state=state,
            country= country,     
            pincode=pincode,
            mobile=mobile,
            email=shipping_email,
            shipping_firstname=shipping_firstname,
            shipping_lastname=shipping_lastname,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_state=shipping_state,
            shipping_country=shipping_country,
            shipping_pincode=shipping_pincode,
            shipping_mobile=shipping_mobile,
            shipping_email=shipping_email,
            totalpayment=total
            
        )

        print("after order creation...................")
        print("Mobile..................",mobile)
        print("Shipping Mobile..................",shipping_mobile)
        print("Pin code............................",pincode)
        print("Shipping Pincode....................",shipping_pincode)


        for i in cartdata:
            new_orderdetail=orderdetail.objects.create(
                order=new_order,
                product=i.product,
                price=i.product.price,
                quantity=i.quantity,
                subtotal=i.subtotal()
            )


            #stock decrease when order is created
            i.product.stock-=i.quantity
            i.product.save()

          
        print("............................",request.POST)
        print("amount =", total)
        print("payment_method =", payment_method)
        print("transaction_id =", transaction_id)
        new_payemt=payment.objects.create(
            order=new_order,
            amount=total,
            payment_method=payment_method,
            transaction_id=transaction_id,
            status=status
           

        )

        #delete the cart after payment

        request.session['last_order_id']=new_order.id
        order_id=request.session.get('last_order_id')
        print("order id from session from checkout.............",order_id)
        cartdata.delete()

        return redirect('order_success')

        # print("Payment method......",payment_method)
        # print("Transaction id",transaction_id)
        # print("order id .........",new_order)
        
    return render(request,'checkout.html',{'cartdata':cartdata,'total':checkouttotal,'message':messages})


@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def order_success(request):

    order_id=request.session.get('last_order_id')

    if not order_id:
        return redirect('home')

    orderdata=order.objects.get(id=order_id,user=request.user)
    paymentdata = payment.objects.get(order=orderdata)

    return render(request,'order_success.html',{'orderdata':orderdata,'order_id':order_id,'paymentdata':paymentdata})


def about(request):
    return render(request,'about.html')

def blog(request):
    return render(request,'blog.html')






def index(request):
    return render(request,'index.html')

def services(request):
    return render(request,'services.html')


@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def thankyou(request):
    return render(request,'thankyou.html')

def logoutpage(request):
    logout(request)
    request.session.flush()
    return redirect('loginpage')
    
@logout_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def register(request):
    print('''''''''''''''''''''''''''''''',request)

    if request.method== "POST":
        print('''''''''''''''''''''''''''''''')
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']

        errors=[]

        fields={
            'username':username,
            'email':email,
            'password':password
        }

        for fields,value in fields.items():
            if not value:
                errors.append(f"{fields} is required")

        if username and not re.match(r'^[A-Za-z ]+$',username):

            errors.append("Username Contains Only Characters")

        if email:
            try:
                validate_email(email)
            except ValidationError:
                errors.append("Email is not Valid")

        if User.objects.filter(email=email).exists():
            errors.append("Email ID Already exists")


        if errors:
            for error in errors:
                messages.error(request,error)

            return render(request,'register.html',{'formdata':request.POST})
        
            

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        return redirect('loginpage')
    return render(request,'register.html')

@logout_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def loginpage(request):


    if request.method=="POST":

        username=request.POST['username']
        password=request.POST['password']

        user=authenticate(
            username=username,
            password=password
        )

        errors=[]

        fields={
            'username':username,
            
            'password':password
        }

        for fields,value in fields.items():
            if not value:
                errors.append(f"{fields} is required")

        if username and not re.match(r'^[A-Za-z ]+$',username):

            errors.append("Username Contains Only Characters")


        if errors:
            for error in errors:
                messages.error(request,error)

            return render(request,'loginpage.html',{'formdata':request.POST})

        if user is not None:
            login(request,user)

            return redirect('home')
        else:
            message="Invalid Credential"
            return render(request,'loginpage.html',{'formdata':request.POST,'message':message})
        
    return render(request,'loginpage.html')

@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def myorders(request):

    orderdata=order.objects.filter(user=request.user).order_by('-id')
    # paymentdata=payment.objects.filter(order=myorders)

    print("myorders...................",orderdata)
    # print("payment data...................",paymentdata)


    

    return render(request,'myorders.html',{'orderdata':orderdata})

@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def myorderdetail(request):

    if request.method=="POST":
        order_id=request.POST['order_id']

        orderdata=order.objects.get(id=order_id,user=request.user)
        orderdetaildata=orderdetail.objects.filter(order=orderdata)
        paymentdata=payment.objects.get(order=orderdata)

        print("order data............",orderdata)

    return render(request,'myorderdetail.html',{'orderdata':orderdata,'orderdetaildata':orderdetaildata,'paymentdata':paymentdata})

@login_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def cancel_order_user(request):

    if request.method=="POST":
        order_id=request.POST['order_id']

        orderdata=order.objects.get(id=order_id,user=request.user)
        print("order data............",orderdata)
        if orderdata.status=="pending":
            cancel_order(orderdata)
       
        

    return redirect('myorders')
    


def cancel_order(orderdata):
    if orderdata.status == "canceled":
        return
    orderdetaildata=orderdetail.objects.filter(order=orderdata)


    for item in orderdetaildata:
        item.product.stock+=item.quantity
        item.product.save()

    orderdata.status="canceled"
    orderdata.save()


def contact(request):
    if request.method == "POST":
        firstname=request.POST['firstname']
        lastname=request.POST['lastname']
        email=request.POST['email']
        message=request.POST['message']


        errors=[]

        fields={
            'firstname':firstname,
            'lastname':lastname,
            'email':email,
            'message':message
        }

        for field,value in fields.items():
            if not value:
                errors.append(f"{field.title()} is required")

        if firstname and not re.match(r'^[A-Za-z ]+$', firstname):
            errors.append("First name can contain only letters")

        if lastname and not re.match(r'^[A-Za-z ]+$', lastname):
            errors.append("Last name can contain only letters")
        if email and not re.match(
            r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$',
            email
        ):

            errors.append("Enter a valid email address")
        if errors:
            
            for error in errors:
                messages.error(request, error)

            return render(request,'contact.html',{'formdata':request.POST})

        new_contact=Contact.objects.create(
            firstname=firstname,
            lastname=lastname,
            email=email,
            message=message
        )
        new_contact.save()
        messages.success(
            request,
            "Thank you! Your message has been sent successfully."
        )

        return redirect('contact')
    return render(request,'contact.html')

@admin_required
def admin_contacts(request):

    contacts = Contact.objects.all().order_by('-id')

    return render(
        request,
        'admin_contacts.html',
        {
            'contacts': contacts
        }
    )


@admin_required
def admin_contact_details(request, id):

    contact = Contact.objects.get(id=id)

    return render(
        request,
        'admin_contact_details.html',
        {
            'contact': contact
        }
    )
                                        # ..................................................


                                                # For Seller - Side


                                        # .......................................................


@seller_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def cancel_order_seller(request):

    if request.method == "POST":

        order_id = request.POST['order_id']

        orderdata = order.objects.get(id=order_id)

        if orderdata.status in ["pending", "processing"]:
            cancel_order(orderdata)

    return redirect('seller_orders')


@seller_logout_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def seller_register(request):

    print('''''''''''''''''''''''''''''''',request)

    if request.method== "POST":
        print('''''''''''''''''''''''''''''''')
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        company=request.POST['company']

        errors=[]

        fields={
            'username':username,
            'email':email,
            'password':password,
            'company':company
        }

        for fields,value in fields.items():
            if not value:
                errors.append(f"{fields} is required")

        if username and not re.match(r'^[A-Za-z ]+$',username):

            errors.append("Username Contains Only Characters")

        if email:
            try:
                validate_email(email)
            except ValidationError:
                errors.append("Email is not Valid")

        
        if errors:
            for error in errors:
                messages.error(request,error)

            return render(request,'seller_register.html',{'formdata':request.POST})


        if User.objects.filter(email=email).exists():
            user=User.objects.get(email=email)

            dataofseller=seller.objects.filter(user_id=user.id).exists()

            if dataofseller:
                msg="Seller Already Exists"
                return render(request,'seller_register.html',{'formdata':request.POST,'msg':msg})
            
            data=seller(
                user=user,
                company=company
            )
            data.save()
            return redirect('seller_login')
        else:

            # dataofuser

            new_user=User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            data=seller(
                user=new_user,
                company=company
            )
            data.save()


            return redirect('seller_login')

    return render(request,'seller_register.html')




@seller_logout_required

@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def seller_login(request):


    if request.method=="POST":

        username=request.POST['username']
        password=request.POST['password']

        user=authenticate(
            username=username,
            password=password
        )

        errors=[]

        fields={
            'username':username,
            
            'password':password
        }

        for fields,value in fields.items():
            if not value:
                errors.append(f"{fields} is required")

        if username and not re.match(r'^[A-Za-z ]+$',username):

            errors.append("Username Contains Only Characters")


        if errors:
            for error in errors:
                messages.error(request,error)

            return render(request,'seller_login.html',{'formdata':request.POST})

        if user is not None:

            if not seller.objects.filter(user=user).exists():
                message="Seller Account not found"
                return render(request,'seller_login.html',{'formdata':request.POST,'message':message})
            login(request,user)

            return redirect('seller_index')
        else:
            message="Invalid Credential"
            return render(request,'seller_login.html',{'formdata':request.POST,'message':message})
        
    return render(request,'seller_login.html')

def seller_logoutpage(request):
    logout(request)
    request.session.flush()
    return redirect('seller_login')



@seller_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def seller_products(request):
    sellerobj=seller.objects.get(user=request.user)

    products=product.objects.filter(isactive=True,seller=sellerobj)

    search=request.GET.get('search','')

    if search:
        products=products.filter(name__icontains=search)

    products=paginate_queryset(request,products,8)
    return render(request,'seller_products.html',{'products':products,'search':search})



@seller_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def seller_product_details(request):
    sellerobj=seller.objects.get(user=request.user)

    if request.method == "POST":

        productid=request.POST['productid']
        productdetails=product.objects.get(id=productid,seller=sellerobj)

        print("Product details ........",productdetails)
    return render(request,'seller_product_details.html',{'productdetails':productdetails})


@seller_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def seller_add_product(request):
    print("request.......",request)
    print("User...........",request.user)

    seller_obj=seller.objects.get(user=request.user)
    if request.method=="POST":
        name=request.POST['name']
        description=request.POST['description']
        price=request.POST['price']
        stock=request.POST['stock']
        image=request.FILES.get('image')

        new_product=product(
            seller=seller_obj,
            name=name,
            description=description,
            price=price,
            stock=stock,
            image=image
        )

        new_product.save()


        print("New Product............",new_product)
        return redirect('seller_products')
    return render(request,'seller_add_product.html')


@seller_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def seller_edit_product(request,id):
   
    sellerobj=seller.objects.get(user=request.user)

    if request.method == "GET":
        productid=id
        productdetails=product.objects.get(id=productid,seller=sellerobj)
        return render(request,'seller_edit_product.html',{'productdetails':productdetails})
    elif request.method == "POST":
        productid=id
        productdetails=product.objects.get(id=productid,seller=sellerobj)
        

        productdetails.name=request.POST['name']
        productdetails.description=request.POST['description']
        productdetails.price=request.POST['price']
        productdetails.stock=request.POST['stock']
        if 'image' in request.FILES:
            productdetails.image=request.FILES['image']

        productdetails.save()




        print("Product details ........",productdetails)
        print("Product details id ........",productdetails.id)

        return redirect('seller_products')


    # return render(request,'seller_edit_product.html',{'productdetails':productdetails})


@seller_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def seller_delete_product(request):
    sellerobj=seller.objects.get(user=request.user)
    if request.method == "POST":
        productid=request.POST['productid']

        print("Pro id..........",productid)

        productdata=product.objects.get(id=productid,seller=sellerobj)

        productdata.isactive=False

        

        productdata.save()

    return redirect('seller_products')


@seller_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def seller_orders(request):
    sellerobj=seller.objects.get(user=request.user)

    orders=order.objects.filter(orderdetail__product__seller=sellerobj).distinct().order_by('-id')

    search=request.GET.get('search','')

    if search:
        orders=orders.filter(id__exact=search)

    orders=paginate_queryset(request,orders,8)
    return render(request,'seller_orders.html',{'orders':orders,'search':search})


@seller_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)



def seller_order_details(request, id):

    sellerobj = seller.objects.get(user=request.user)

    orderdata = get_object_or_404(
        order.objects.filter(
            orderdetail__product__seller=sellerobj
        ).distinct(),
        id=id
    )

    orderdetails = orderdetail.objects.filter(
        order=orderdata,
        product__seller=sellerobj
    )

    paymentdata = payment.objects.get(order=orderdata)

    return render(
        request,
        'seller_order_details.html',
        {
            'orderdata': orderdata,
            'orderdetails': orderdetails,
            'user': orderdata,
            'paymentdata': paymentdata
        }
    )

@seller_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def seller_update_order_status(request,id,status):
    sellerobj=seller.objects.get(user=request.user)

    orderdata = get_object_or_404(
        order.objects.filter(
            orderdetail__product__seller=sellerobj
        ).distinct(),
        id=id
    )
    allowed_options={
        'pending':['processing'],
        'processing':['shipped'],
        'shipped':[],
        'delivered':[],
        'canceled':[]
    }

    current_status=orderdata.status
    if status not in allowed_options[current_status]:
        return redirect('seller_order_details',id=id)
    
    orderdata.status=status

    orderdata.save()
    return redirect('seller_order_details',id=id)




@seller_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def seller_profile(request):

    user=request.user
    sellerdata=seller.objects.get(user=user)
    
    return render(request,'seller_profile.html',{'user':user,'sellerdata':sellerdata})


@seller_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def seller_edit_profile(request):
    user=request.user
    sellerdata=seller.objects.get(user=user)
    # userdata=User.objects.get(user=user)
    # print(".................",userdata)

    if request.method=="POST":

        name=request.POST['name']
        email=request.POST['email']
        mobile=request.POST['mobile']
        company=request.POST['company']
        address=request.POST['address']
        city=request.POST['city']
        state=request.POST['state']
        country=request.POST['country']

        sellerdata.user.username=name
        sellerdata.user.email=email
        sellerdata.mobile=mobile
        sellerdata.company=company
        sellerdata.address=address
        sellerdata.city=city
        sellerdata.state=state
        sellerdata.country=country

        sellerdata.save()

        return redirect('seller_profile')

    return render(request,'seller_edit_profile.html',{'sellerdata':sellerdata})

@seller_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def seller_analytics(request):
    user=request.user
    sellerobj=seller.objects.get(user=user)

    total_sales=orderdetail.objects.filter(product__seller=sellerobj,order__status='delivered').aggregate(total=Sum('subtotal'))['total'] or 0

    total_orders=orderdetail.objects.filter(product__seller=sellerobj).exclude(order__status__in=['delivered','canceled']).count()

    products_sold=orderdetail.objects.filter(product__seller=sellerobj,order__status='delivered').count()

    cancelled_orders=orderdetail.objects.filter(product__seller=sellerobj,order__status='canceled').count()

    monthly_sales=[]

    for month in range(1,13):
        sale=orderdetail.objects.filter(product__seller=sellerobj,order__status='delivered',order__created_at__month=month).aggregate(total=Sum('subtotal'))['total'] or 0

        monthly_sales.append(float(sale))

    monthly_orders=[]

    for month in range(1,13):
        sale=orderdetail.objects.filter(product__seller=sellerobj,order__status='delivered',order__created_at__month=month).count()

        monthly_orders.append(float(sale))

    print("monthly sales.....",monthly_sales)
    print("monthly orders.......",monthly_orders)
    print("....................",products_sold)
    return render(request,'seller_analytics.html',{'total_sales':total_sales,'products_sold':products_sold,'total_orders':total_orders,'cancelled_orders':cancelled_orders,'monthly_sales':monthly_sales,'monthly_orders':monthly_orders})


@seller_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def seller_index(request):

    print("user............................",request.user)
    sellerobj=seller.objects.get(user=request.user)
    cancleordercount=orderdetail.objects.filter(order__status='canceled',product__seller=sellerobj).count()

    totalorders=orderdetail.objects.filter(product__seller=sellerobj).exclude(order__status='canceled').count()
    totalproducts=product.objects.filter(seller=sellerobj).count()
    
    totalsales=orderdetail.objects.filter(product__seller=sellerobj,order__status='delivered').aggregate(total=Sum('subtotal'))['total'] or 0

    today=timezone.now().date()
    orders = order.objects.filter(orderdetail__product__seller=sellerobj,created_at__date=today).exclude(status='canceled').distinct().order_by('-created_at')    
    return render(request,'seller_index.html',{'orders':orders,'cancleordercount':cancleordercount,'totalorders':totalorders,'totalproducts':totalproducts,'totalsales':totalsales})








                            # ..................................................


                                                # For Admin - Side


                            # .......................................................



@admin_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def admin_index(request):

    admin=request.user
   
    users=User.objects.all().count()
    cancleordercount=orderdetail.objects.filter(order__status='canceled').count()

    totalorders=orderdetail.objects.all().exclude(order__status='canceled').count()
    totalproducts=product.objects.all().count()
    
    totalsales=orderdetail.objects.filter(order__status='delivered').aggregate(total=Sum('subtotal'))['total'] or 0

    today=timezone.now().date()
    orders=order.objects.filter(created_at__date=today).exclude(status='canceled').order_by('-created_at')
    return render(request,'admin_index.html',{'users':users,'orders':orders,'cancleordercount':cancleordercount,'totalorders':totalorders,'totalproducts':totalproducts,'totalsales':totalsales})




def admin_register(request):
    print('''''''''''''''''''''''''''''''',request)

    if request.method== "POST":
        print('''''''''''''''''''''''''''''''')
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']

        errors=[]

        fields={
            'username':username,
            'email':email,
            'password':password
        }

        for fields,value in fields.items():
            if not value:
                errors.append(f"{fields} is required")

        if username and not re.match(r'^[A-Za-z ]+$',username):

            errors.append("Username Contains Only Characters")

        if email:
            try:
                validate_email(email)
            except ValidationError:
                errors.append("Email is not Valid")

        if User.objects.filter(email=email).exists():
            errors.append("Email ID Already exists")


        if errors:
            for error in errors:
                messages.error(request,error)

            return render(request,'admin_register.html',{'formdata':request.POST})
        
            

        new_user=User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True
        )
        
        return redirect('admin_login')
    return render(request,'admin_register.html')

@admin_logout_required

def admin_login(request):


    if request.method=="POST":

        username=request.POST['username']
        password=request.POST['password']

        user=authenticate(
            username=username,
            password=password,
          
        )

        errors=[]

        fields={
            'username':username,
            
            'password':password
        }

        for fields,value in fields.items():
            if not value:
                errors.append(f"{fields} is required")

        if username and not re.match(r'^[A-Za-z0-9_ ]+$',username):

            errors.append("Username can contain only letters, numbers and underscore")


        if errors:
            for error in errors:
                messages.error(request,error)

            return render(request,'admin_login.html',{'formdata':request.POST})

        if user is not None:
            if not user.is_staff:
                return render(request,'admin_login.html',{'message':'Admin account not found'}
                )
            login(request,user)

            return redirect('admin_index')
        else:
            message="Invalid Credential"
            return render(request,'admin_login.html',{'formdata':request.POST,'message':message})
        
    return render(request,'admin_login.html')



@admin_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def admin_analytics(request):
   

    total_sales=orderdetail.objects.filter(order__status='delivered').aggregate(total=Sum('subtotal'))['total'] or 0

    total_orders=orderdetail.objects.exclude(order__status__in=['delivered','canceled']).count()

    products_sold=orderdetail.objects.filter(order__status='delivered').count()

    cancelled_orders=orderdetail.objects.filter(order__status='canceled').count()

    monthly_sales=[]

    for month in range(1,13):
        sale=orderdetail.objects.filter(order__status='delivered',order__created_at__month=month).aggregate(total=Sum('subtotal'))['total'] or 0

        monthly_sales.append(float(sale))

    monthly_orders=[]

    for month in range(1,13):
        sale=orderdetail.objects.filter(order__status='delivered',order__created_at__month=month).count()

        monthly_orders.append(float(sale))

    print("monthly sales.....",monthly_sales)
    print("monthly orders.......",monthly_orders)
    print("....................",products_sold)

    return render(request,'admin_analytics.html',{'total_sales':total_sales,'products_sold':products_sold,'total_orders':total_orders,'cancelled_orders':cancelled_orders,'monthly_sales':monthly_sales,'monthly_orders':monthly_orders})





@admin_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def admin_orders(request):
    orders=order.objects.all().order_by('-id')
    search=request.GET.get('search','')

    if search :
        orders=orders.filter(id=search)

    orders=paginate_queryset(request,orders,8)

    return render(request,'admin_orders.html',{'orders':orders,'search':search})


@admin_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def admin_products(request):
    products=product.objects.all()

    search=request.GET.get('search','')

    if search:
        products=products.filter(name__icontains=search)

    products=paginate_queryset(request,products,8)
    return render(request,'admin_products.html',{'products':products,'search':search})


@admin_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def admin_product_details(request):

    if request.method == "POST":    

        productid=request.POST['productid']
        productdetails=product.objects.get(id=productid)

        print("Product details ........",productdetails)
    return render(request,'admin_product_details.html',{'productdetails':productdetails})

@admin_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def admin_users(request):
    users=User.objects.all()
    search=request.GET.get('search','')

    if search:
        users=users.filter(username__icontains=search)
    seller_ids = set(
    seller.objects.values_list(
        'user_id',
        flat=True
    ))

    users=paginate_queryset(request,users,8)
    return render(request,'admin_users.html',{'users':users,'seller_ids':seller_ids,'search':search })

@admin_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def admin_sellers(request):
    sellers=seller.objects.all()
    search=request.GET.get('search','')

    if search:
        sellers=sellers.filter(user__username__icontains=search)

    sellers=paginate_queryset(request,sellers,8)
    return render(request,'admin_sellers.html',{'sellers':sellers,'search':search})









@admin_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)

def admin_update_order_status(request,id,status):

    orderdata=order.objects.get(id=id)

    allowed_options={
        'pending': [],
        'processing': [],
        'shipped': ['delivered'],
        'delivered': [],
        'canceled': []
        
    }

    current_status=orderdata.status
    if status not in allowed_options[current_status]:
        return redirect('admin_orders')
    
    orderdata.status=status

    orderdata.save()
    return redirect('admin_orders')

def admin_logoutpage(request):
    logout(request)
    request.session.flush()
    return redirect('admin_login')


def pagenotfound(request,exception=None):

    path=request.path.lower()

    if path.startswith('/seller'):

        if request.user.is_authenticated and seller.objects.filter(user=request.user).exists():
            dashboard = 'seller_index'
        else:
            dashboard = 'seller_login'
    
    elif path.startswith('/admin'):

        if request.user.is_authenticated and request.user.is_staff:
            dashboard = 'admin_index'
        else:
            dashboard = None
    else:
        dashboard='home'

    return render(request,'pagenotfound.html',{'dashboard':dashboard})


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def invoice(request, id):

    try:

        orderdata = order.objects.get(
            id=id,
            user=request.user
        )

    except order.DoesNotExist:

        messages.error(
            request,
            "Invoice not found."
        )

        return redirect("myorders")

    orderdetails = orderdetail.objects.filter(order=orderdata)

    paymentdata = payment.objects.get(order=orderdata)

    subtotal = sum(i.subtotal for i in orderdetails)

    shipping = 0          # Free shipping
    discount = 0          # Future use

    grand_total = subtotal + shipping - discount

    invoice_no = (
        f"INV-"
        f"{orderdata.created_at.strftime('%Y%m%d')}-"
        f"{orderdata.id:04d}"
    )

    context = {

        'orderdata': orderdata,

        'orderdetails': orderdetails,

        'paymentdata': paymentdata,

        'subtotal': subtotal,

        'shipping': shipping,

        'discount': discount,

        'grand_total': grand_total,

        'invoice_no': invoice_no,
    }

    return render(request,'invoice.html',context)