from django.db.models import Count
from django.contrib.auth.models import AnonymousUser

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect,render
from django.views import View

from .forms import CustomerProfileForm, CustomerRegistrationForm

from .models import Cart, Customer, Product,Wishlist
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator




def home(request):

    totalitem = 0
    wishitem = 0

    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = Wishlist.objects.filter(user=request.user).count()

    return render(request, 'app/home.html', locals())

def about(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = Wishlist.objects.filter(user=request.user).count()
    return render(request,'app/about.html',locals())


def contact(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = Wishlist.objects.filter(user=request.user).count()
    return render(request,'app/contact.html',locals())


class CategoryView(View):
    def get(self, request, val):

        totalitem = 0
        wishitem = 0

        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()
            wishitem = Wishlist.objects.filter(user=request.user).count()

        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')

        return render(request, 'app/category.html', locals())


class CategoryTitle(View):
    def get(self, request, val):

        product = Product.objects.filter(title=val)

        if product.exists():
            category = product.first().category
            title = Product.objects.filter(
                category=category
            ).values_list('title', flat=True)
        else:
            title = []

        totalitem = 0
        wishitem = 0

        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()
            wishitem = Wishlist.objects.filter(user=request.user).count()

        return render(request, 'app/category.html', locals())
    

class ProductDetail(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)

        wishlist = None

        totalitem = 0
        wishitem = 0

        if request.user.is_authenticated:
            wishlist = Wishlist.objects.filter(
                product=product,
                user=request.user
            )

            totalitem = Cart.objects.filter(user=request.user).count()
            wishitem = Wishlist.objects.filter(user=request.user).count()

        return render(request, "app/productdetail.html", locals())
    

class CustomerRegistrationView(View):
    def get(self,request):
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
            wishitem=len(Wishlist.objects.filter(user=request.user))
        form=CustomerRegistrationForm()
        return render(request,'app/customerregistration.html',locals())
    def post(self,request):
        form=CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registered Successfully !")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request,'app/customerregistration.html',locals())
    

    
@login_required    
def add_to_cart(request):
    user=request.user
    product_id=request.GET.get('prod_id')
    product=Product.objects.get(id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('/cart')

@login_required
def show_cart(request):
    user=request.user
    cart=Cart.objects.filter(user=user)
    amount=0
    for p in cart:
        value=p.quantity*p.product.discounted_price
        amount=amount+value
    totalamount=amount+40
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=Cart.objects.filter(user=request.user).count()
        wishitem=Wishlist.objects.filter(user=request.user).count()
    return render(request,'app/addtocart.html',locals())

@login_required
def show_wishlist(request):
    user=request.user
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Wishlist.objects.filter(user=request.user))
    product = Wishlist.objects.filter(user=user).select_related('product')
    return render(request,'app/wishlist.html',locals())

@method_decorator(login_required, name='dispatch')
class Checkout(View):
    def get(self, request):
        totalitem = 0
        wishitem = 0

        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()
            wishitem = Wishlist.objects.filter(user=request.user).count()

        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)

        famount = 0
        for p in cart_items:
            famount += p.quantity * p.product.discounted_price

        totalamount = famount + 40

        return render(request, 'app/checkout.html', locals())
    
@login_required
def plus_cart(request):
    if request.method=='GET':
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id)&Q(user=request.user))
        c.quantity+=1
        c.save()
        user=request.user
        cart=Cart.objects.filter(user=user)
        amount=0
        for p in cart:
            value=p.quantity*p.product.discounted_price
            amount=amount+value
        totalamount=amount+40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)
    
@login_required    
def minus_cart(request):
    if request.method=='GET':
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id)&Q(user=request.user))
        c.quantity-=1
        c.save()
        user=request.user
        cart=Cart.objects.filter(user=user)
        amount=0
        for p in cart:
            value=p.quantity*p.product.discounted_price
            amount=amount+value
        totalamount=amount+40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)


@login_required
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')

        try:
            # Find and delete all cart items for the user with this product
            cart_items = Cart.objects.filter(product_id=prod_id, user=request.user)

            if cart_items.exists():
                cart_items.delete()

                # Recalculate cart total after removal
                cart = Cart.objects.filter(user=request.user)
                amount = sum(item.quantity * item.product.discounted_price for item in cart)
                totalamount = amount + 40  # Shipping cost

                return JsonResponse({
                    'amount': amount,
                    'totalamount': totalamount
                })

            else:
                return JsonResponse({'error': 'Cart item not found'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

@login_required
def plus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user

        Wishlist.objects.get_or_create(
            user=user,
            product=product
        )

        return JsonResponse({
            'message': 'Wishlist Added Successfully'
        })

@login_required
def minus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user

        # Properly delete the wishlist item
        Wishlist.objects.filter(user=user, product=product).delete()

        data = {
            'message': 'Wishlist Removed Successfully',
        }
        return JsonResponse(data)
    

def search(request):
    query=request.GET['search']
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Wishlist.objects.filter(user=request.user))
    product=Product.objects.filter(Q(title__icontains=query))
    return render(request,'app/search.html',locals())

@login_required
def order_success(request):
    Cart.objects.filter(user=request.user).delete()

    totalitem = 0
    wishitem = Wishlist.objects.filter(user=request.user).count()

    return render(request, 'app/order_success.html', {
        'totalitem': totalitem,
        'wishitem': wishitem,
    })