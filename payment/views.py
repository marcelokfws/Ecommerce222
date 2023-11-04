from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render

from cart.cart import Cart

from .models import Order, OrderItem, ShippingAddress

# Create your views here.


def checkout(request):

    # Users with accounts -- Pre-fill the form

    if request.user.is_authenticated:

        try:

            # Authenticated users WITH shipping information

            shipping_address = ShippingAddress.objects.get(
                user=request.user.id)

            context = {'shipping': shipping_address}

            return render(request, 'payment/checkout.html', context=context)

        except:

            # Authenticated users with NO shipping information

            return render(request, 'payment/checkout.html')

    else:

        # Guest users

        return render(request, 'payment/checkout.html')


def complete_order(request):

    if request.POST.get('action') == 'post':

        name = request.POST.get('name')
        email = request.POST.get('email')

        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')

        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')

        # All-in-one shipping address

        shipping_address = (address1 + "\n" + address2 + "\n" +

                            city + "\n" + state + "\n" + zipcode

                            )

        # Shopping cart information

        cart = Cart(request)

        # Get the total price of items

        total_cost = cart.get_total()

        '''

            Order variations

            1) Create order -> Account users WITH + WITHOUT shipping information
        

            2) Create order -> Guest users without an account
        

        '''

        # 1) Create order -> Account users WITH + WITHOUT shipping information

        if request.user.is_authenticated:

            order = Order.objects.create(full_name=name, email=email, shipping_address=shipping_address,

                                         amount_paid=total_cost, user=request.user)

            order_id = order.pk
            product_list = [' Produto x Quantidade: ']

            full_name = name

            for item in cart:

                OrderItem.objects.create(order_id=order_id, product=item['product'], quantity=item['qty'],

                                         price=item['price'], user=request.user)

                product_list.append(item['product'])
                product_list.append(item['qty'])
                all_products = product_list

            send_mail('Pedido recebido', 'Olá, ' + str(full_name) + '\n\n' + 'Obrigado por fazer seu pedido' + '\n\n' +
                      'Por favor, veja seu pedido abaixo:' +
                      '\n\n' + str(all_products) + '\n\n' +
                      'Total pago R$' +
                      str(cart.get_total()), settings.EMAIL_HOST_USER, [email], fail_silently=False,
                      )

        #  2) Create order -> Guest users without an account

        else:

            order = Order.objects.create(full_name=name, email=email, phone=phone, shipping_address=shipping_address,

                                         amount_paid=total_cost)

            order_id = order.pk

            for item in cart:

                OrderItem.objects.create(order_id=order_id, product=item['product'], quantity=item['qty'],

                                         price=item['price'])

        order_success = True

        response = JsonResponse({'success': order_success})

        return response


def payment_success(request):

    # Clear shopping cart

    for key in list(request.session.keys()):

        if key == 'session_key':

            del request.session[key]

    return render(request, 'payment/payment-success.html')


def payment_failed(request):

    return render(request, 'payment/payment-failed.html')
