from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json,datetime
from .utils import cookieCart, cartData, guestOrder

# Create your views here.
def store(request):
     data = cartData(request)
     cartItems = data['cartItems']

     products = Product.objects.all()
     context = {'products' : products, 'cartItems':cartItems}
     return render(request, 'store/store.html', context)


def cart(request):
     data = cartData(request)
     cartItems = data['cartItems']
     order = data['order']
     items = data['items']

     context = {'items' : items, 'order':order, 'cartItems':cartItems}
     return render(request, 'store/cart.html', context)


def checkout(request):
     data = cartData(request)
     cartItems = data['cartItems']
     order = data['order']
     items = data['items']

     context = {'items' : items, 'order':order, 'cartItems' : cartItems}
     return render(request, 'store/checkout.html', context)


# api to update cart value and items
def updateItem(request):
     data = json.loads(request.body)
     productId = data['productId']
     action = data['action']

     print('Action: ',action)
     print('productId:',productId)

     customer = request.user.customer
     product = Product.objects.get(id=productId)
     order, created = Order.objects.get_or_create(customer = customer, complete = False)
     orderItem, created = OrderItem.objects.get_or_create(order = order, product = product)

     if action =='add':
          orderItem.quantity += 1
     elif action =='remove':
          orderItem.quantity -= 1
     elif action=='delete':
          orderItem.quantity = 0

     #save item in db
     orderItem.save()
     #delete the item from db if its value is <=0
     if orderItem.quantity<=0:
          orderItem.delete()
     return JsonResponse('Item was added/removed', safe=False)


def processOrder(request):
     transaction_id = datetime.datetime.now().timestamp()
     data = json.loads(request.body)

     if request.user.is_authenticated:
          customer = request.user.customer
          order, created = Order.objects.get_or_create(customer = customer, complete = False)

     else:
          customer, order = guestOrder(request, data)
     
     #check if frontends total matches db total before proceeding with order
     total = float(data['form']['total'])
     order.transaction_id = transaction_id
     if total == order.get_cart_total:
          order.complete = True
     order.save()

     #if order is not digital, save the shipping info in db
     if order.shipping == True:
               ShippingAddress.objects.create(
                    customer =customer,
                    order = order,
                    address = data['shipping']['address'],
                    city = data['shipping']['city'],
                    state = data['shipping']['state'],
                    zipcode = data['shipping']['zip'],
               )


     return JsonResponse('Payment submitted...', safe=False)

#api for getting all orders for a particular user
def getOrders(request):
     data = cartData(request)
     cartItems = data['cartItems']

     #get all orders and pass into template


def wishlist(request):
     data = cartData(request)
     cartItems = data['cartItems']

     customer = request.user
     user = Customer.objects.get(user = customer)
     wishListItems = user.wishlist_set.all()
     wishListCount = wishListItems.count()
     context = {'wishListItems' : wishListItems, 'cartItems':cartItems, 'wishListCount': wishListCount}
     return render(request, 'store/wishlist.html', context)

def update_wishlist(request):
     data = json.loads(request.body)
     productId = data['productId']
     action = data['action']

     product = Product.objects.get(id=productId)
     customer = request.user.customer

     if(action=='move'):
          wishListItem, created = WishList.objects.get_or_create(product = product, customer=customer)
          wishListItem.save()
     #user = Customer.objects.get(user = customer)
     else:
          wishListItem = WishList.objects.get(product = product, customer = customer)
          print(wishListItem)
          wishListItem.delete()
     return JsonResponse({"wishListItem": wishListItem.product.name})