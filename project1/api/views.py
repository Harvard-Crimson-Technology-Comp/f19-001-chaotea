import datetime

from django.shortcuts import render

from django.http import HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

import bcrypt

from project1.api.models import UserModel, PurchaseModel, StockModel, PortfolioModel

from alpha_vantage.timeseries import TimeSeries

from datetime import datetime
from time import sleep

# don't put this here in real code! you are welcome to use this key if you would like
av_api_key = "B6Z376P6CGR0XAL5"
ts = TimeSeries(key=av_api_key)

"""
You will create many 4 key views here: register, buy, sell, and list

register - allows a user to register and obtain an API token
buy - allows a user to buy some stocks by submitting a symbol and an amount
sell - allows a user to sell some stocks by submitting a symbol and an amount
list - allows a user to see their current portfolio, does not take arguments
"""

@require_http_methods(["POST"])
@csrf_exempt
def register(request):
    fields = ["first_name", "last_name", "username", "password"]

    # Check they provided all the right data
    for field in fields:
        if not request.POST.get(field):
            return JsonResponse({"error": f"Field: {field} not found"})
    
    users = UserModel.objects.filter(username=request.POST.get("username"))
    if len(users) > 0:
        return JsonResponse({"error": "User with that username already exists"})
    

    new_portfolio = PortfolioModel(cash=0)

    new_user = UserModel(
        username=request.POST.get("username"),
        first_name=request.POST.get("first_name"),
        last_name=request.POST.get("last_name"),
        password=hash(request.POST.get("password")),
        portfolio=new_portfolio
    )
    new_user.save()
    
    return JsonResponse({
        "username": new_user.username,
        "api_token": new_user.api_token
    })

@require_http_methods(["POST"])
@csrf_exempt
def buy(request):
    fields = ["api_token", "symbol", "quantity"]

    # Check they provided all the right data
    for field in fields:
        if not request.POST.get(field):
            return JsonResponse({"error": f"Field: {field} not found"})

    users = UserModel.objects.filter(api_token=request.POST.get("api_token"))

    # Validate user
    if len(users) == 1:
        user = users[0]
    else:
        return JsonResponse({"error": "No user found with that API token"})

    try:
        symbol, _ = ts.get_quote_endpoint(symbol=request.POST.get("symbol").upper())
    except ValueError:
        return JsonResponse({"error": f"Symbol: {request.POST.get('symbol')} not found"})

    # Strip off AlphaVantage's annoying stuff:
    old_keys = [k for k in symbol]
    for k in old_keys:
        new_k = k.split(". ")[1]
        symbol[new_k] = symbol[k]

    cash = user.portfolio.cash

    if cash - int(request.POST.get("quantity")) * float(symbol["price"]) < 0:
        return JsonResponse({"error": "User has insufficient funds"})

    # Update the amount of cash the user has
    user.portfolio.cash -= int(request.POST.get("quantity")) * float(symbol["price"])
    user.portfolio.save(update_fields=["cash"])

    # Add a new purchase
    purchase = PurchaseModel(
        user=user,
        symbol=request.POST.get("symbol").upper(),
        price=symbol["price"],
        quantity=int(request.POST.get("quantity"))
    )
    purchase.save()

    stocks = StockModel.objects.filter(portfolio=user.portfolio, symbol=request.POST.get("symbol").upper())

    if stocks:
        stock = stocks[0]
        stock.quantity += int(request.POST.get("quantity"))
        stock.save(update_fields=["quantity"])
    else:
        stock = StockModel(
            portfolio=user.portfolio,
            symbol=request.POST.get("symbol").upper(),
            quantity=int(request.POST.get("quantity"))
        )
        stock.save()

    return JsonResponse({
        "symbol": request.POST.get("symbol").upper(),
        "quantity": int(request.POST.get("quantity")),
        "timestamp": purchase.timestamp,
        "cash_remaining": user.portfolio.cash
    })
    
@require_http_methods(["POST"])
@csrf_exempt
def sell(request):
    fields = ["api_token", "symbol", "quantity"]

    # Check they provided all the right data
    for field in fields:
        if not request.POST.get(field):
            return JsonResponse({"error": f"Field: {field} not found"})

    users = UserModel.objects.filter(api_token=request.POST.get("api_token"))

    # Validate user
    if len(users) == 1:
        user = users[0]
    else:
        return JsonResponse({"error": "No user found with that API token"})

    try:
        symbol, _ = ts.get_quote_endpoint(symbol=request.POST.get("symbol").upper())
    except ValueError:
        return JsonResponse({"error": f"Symbol: {request.POST.get('symbol')} not found"})

    # Strip off AlphaVantage's annoying stuff:
    old_keys = [k for k in symbol]
    for k in old_keys:
        new_k = k.split(". ")[1]
        symbol[new_k] = symbol[k]

    stocks = StockModel.objects.filter(portfolio=user.portfolio, symbol=request.POST.get("symbol").upper())

    if stocks:
        stock = stocks[0]
        if stock.quantity - int(request.POST.get("quantity")) < 0:
            return JsonResponse({"error": "User does not own sufficient quantity of stock"})
        stock.quantity -= int(request.POST.get("quantity"))
        user.portfolio.cash += int(request.POST.get("quantity")) * float(symbol["price"])
        stock.save(update_fields=["quantity"])
        user.portfolio.save(update_fields=["cash"])
    else:
        return JsonResponse({"error": "User does not own any shares of that stock"})

    # Add a new purchase
    purchase = PurchaseModel(
        user=user,
        symbol=request.POST.get("symbol").upper(),
        price=symbol["price"],
        quantity=0 - int(request.POST.get("quantity"))
    )
    purchase.save()

    return JsonResponse({
        "symbol": request.POST.get("symbol").upper(),
        "quantity": 0 - int(request.POST.get("quantity")),
        "timestamp": purchase.timestamp,
        "cash_remaining": user.portfolio.cash
    })

@require_http_methods(["GET"])
@csrf_exempt
def api_list(request):
    fields = ["api_token"]

    # Check they provided all the right data
    for field in fields:
        if not request.POST.get(field):
            return JsonResponse({"error": f"Field: {field} not found"})

    users = UserModel.objects.filter(api_token=request.POST.get("api_token"))

    # Validate user
    if len(users) == 1:
        user = users[0]
    else:
        return JsonResponse({"error": "No user found with that API token"})

    stocks = StockModel.objects.filter(portfolio=user.portfolio)
    stocks_dict = {}
    for stock in stocks:
        symbol, _ = ts.get_quote_endpoint(symbol=stock.symbol.upper())

        # Strip off AlphaVantage's annoying stuff:
        old_keys = [k for k in symbol]
        for k in old_keys:
            new_k = k.split(". ")[1]
            symbol[new_k] = symbol[k]

        stocks_dict.append({
            "symbol": stock.symbol,
            "quantity": stock.quantity,
            "price": symbol[price]
        })

    return JsonResponse({
        "stocks": stocks_dict,
        "cash": user.portfolio.cash,
        "timestamp": datetime.datetime.now()
    })
