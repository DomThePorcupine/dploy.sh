from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponse
import json

# NOTE there is no way to even attempt to sign up here


def userlogin(request):
    if request.method == 'OPTIONS':
        return HttpResponse(status=200)
    if request.method != 'POST':
        # Tell them its no good
        return HttpResponse(status=404)

    # We know it is a POST request for sure now

    try:
        params = json.loads(request.body)
        username = params['username']
        password = params['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return JsonResponse({'message': 'success'})
        else:
            # Return an 'invalid login' error message.
            return JsonResponse({'message': 'failure'}, status=400)
    # In case they haven't actually sent us any valid information
    except Exception as e:
        return JsonResponse({'message': 'Invalid params'}, status=400)
