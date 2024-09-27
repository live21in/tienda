from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
 
#Para realizar una funcion privada se utiliza __
def _cart_id(request):
    cart = request.session.session_key # Obtenemos la cookie de session
    if not cart: 
        cart = request.session.create() # Si no existe la creamos
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id) #Obtenemos el id del producto
    product_variations = []
    if request.method == 'POST':
        #BASICAMENTE CON ESTE CICLO LE ESTAMOS DICIENDO color = request.POST['color']
        for item in request.POST:
            key = item
            value = request.POST[key]

            try: 
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variations.append(variation)
            except:
                print("555")
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist: 
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()

    #Revisa si existe un producto repetido que se agrego en el carrito  
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

    if is_cart_item_exists: 
        #Aumentamos el carrito a uno  
        cart_item = CartItem.objects.filter(product=product, cart=cart) #Obtenemos los productos del carrito
        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

        if product_variations in ex_var_list:
            index = ex_var_list.index(product_variations)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variations) > 0 :
                item.variations.clear()
                item.variations.add(*product_variations)
            item.save()
    else:
        #Creamos el carrito si no existe
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        )
        if len(product_variations) > 0 :
            cart_item.variations.clear()
            for item in product_variations:
                cart_item.variations.add(item)
        cart_item.save()
    return redirect('cart')

    
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax=0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total'       : total,
        'quantity'    : quantity,
        'cart_items'  : cart_items,
        'tax'         : tax,
        'grand_total' : grand_total,
    }

    return render(request, 'store/cart.html', context)

def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

# Create your views here.
