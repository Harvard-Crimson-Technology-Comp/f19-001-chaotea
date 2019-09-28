from django.db import models

# TODO: you'll need to fill in the models that you create here!

# a class containing what happened in a purchase (who made it, when it was made, what it traded)
class PurchaseModel(models.Model):
    class Meta:
        app_label = 'api'
    timestamp = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey("UserModel", on_delete=models.CASCADE, null=True, blank=True)
    symbol = models.CharField(max_length=16, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)

# the class containing your user information (including their api token and password, etc)
class UserModel(models.Model):
    class Meta:
        app_label = 'api'
    first_name = models.CharField(max_length=16, null=True, blank=True)
    last_name = models.CharField(max_length=16, null=True, blank=True)
    api_token = models.CharField(max_length=256, null=True, blank=True)
    password = models.CharField(max_length=256, null=True, blank=True)
    username = models.CharField(max_length=16, null=True, blank=True)
    portfolio = models.ForeignKey("PortfolioModel", on_delete=models.CASCADE, null=True, blank=True)

# the class containing a portfolio of stocks
class PortfolioModel(models.Model):
    class Meta:
        app_label = 'api'
    cash = models.IntegerField(default=0, null=True, blank=True)

# a class containing a simple set of data on a stock within a portfolio
class StockModel(models.Model):
    class Meta:
        app_label = 'api'
    portfolio = models.ForeignKey("PortfolioModel", on_delete=models.CASCADE, null=True, blank=True)
    symbol = models.CharField(max_length=16, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)