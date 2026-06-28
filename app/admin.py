from django.contrib import admin
from .models import Cart, Customer,Product, Wishlist

admin.site.site_header = "JK Cafe Admin"

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display=['id','title','discounted_price','category','product_image']

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display=['id','user','locality','city','state','zipcode']

@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display=['id','user','product','quantity']
   
@admin.register(Wishlist)
class WishlistModelAdmin(admin.ModelAdmin):
    list_display=['id','user','product']