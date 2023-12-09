from django.shortcuts import render
from django.conf import settings
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from django.views.generic import ListView #new

from .models import Item

import stripe


class HomePageView(ListView):
    model = Item
    template_name = 'home.html'
    context_object_name = 'items'

# class HomePageView(TemplateView):
#     template_name = 'home.html'

    # def get_context_data(self, **kwargs):
    #     pk = self.kwargs.get("pk")
    #     product = Item.objects.get(pk=pk)
    #     context = super(HomePageView, self).get_context_data(**kwargs)
    #     context.update({
    #         "product": product,
    #             "STRIPE_PUBLICHABLE_KEY": settings.STRIPE_PUBLICHABLE_KEY
    #     })
        # return context

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def create_checkout_session(request): #new self args kwargs
    # product_id = self.kwargs["pk"] #new
    # product = Item.objects.get(id=product_id) #new
    if request.method == 'GET':
        domain_url = settings.URL
        stripe.api_key = settings.STRIPE_SECRET_KEY
        product_id = request.GET.get('product')

        print("PRODUCT ID: ", product_id)

        product = Item.objects.get(pk=product_id)

        print("PRODUCT HERE: ", product.name)
        
        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                        {
                                'quantity': 1,
                            'price_data': {
                                'currency': "usd",
                                'unit_amount': product.price,
                                'product_data': {
                                    'name': product.name,
                                    'description': product.description
                            },
                        },
                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})
        


class SuccessView(TemplateView):
    template_name = 'success.html'


class CancelledView(TemplateView):
    template_name = 'cancelled.html'



@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status = 400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    print('MY MESSAGE: ', event['type'])
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        # todo: run some custom code here

    return HttpResponse(status=200)