import json
from .models import *

#this function handles cartItems,cart, total for guest user(not authenticated). Created dummy cart item.
def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    items=[]
    order = {'get_cart_total':0, 'get_cart_items':0, 'shipping': False}
    cartItems = order['get_cart_items']

    for i in cart:
        try:
            #adding all items quantity 
            cartItems+=cart[i]['quantity']
            product = Product.objects.get(id=i)
            total = product.price*cart[i]['quantity']
            order['get_cart_total']+=total
            order['get_cart_items']+=cart[i]['quantity']

            item = {
                    'product' : {
                        'id' : product.id,
                        'name' : product.name,
                        'price' : product.price,
                        'imageURL' : product.imageURL,
                    },
                    'quantity' : cart[i]['quantity'],
                    'get_total' : total,
            }
            items.append(item)

            if product.digital == False:
                    order['shipping'] =True

        except:
            pass
    
    return {'cartItems' : cartItems, 'order' : order, 'items' : items}


def cartData(request):
    if request.user.is_authenticated:
          customer = request.user.customer
          order, created = Order.objects.get_or_create(customer = customer, complete = False)
          items = order.orderitem_set.all()
          cartItems = order.get_cart_items
    else:
          cookieData = cookieCart(request)
          cartItems = cookieData['cartItems']
          order = cookieData['order']
          items = cookieData['items']
    return {'cartItems' : cartItems, 'order' : order, 'items' : items}

#checkout process for guest user
def guestOrder(request, data):
    print('user not logged in')
    print('COOKIES:', request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    #create customer account if not present already(shopping for first time)
    customer, created = Customer.objects.get_or_create(
        email=email,
    )
    customer.name = name
    customer.save()

    #create order object
    order = Order.objects.create(
        customer = customer,
        complete = False
    )

    #add items to order
    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        orderItem = OrderItem.objects.create(
            product = product,
            order = order,
            quantity = item['quantity'],
        )
    return customer, order