import graphene
from graphene_django.types import DjangoObjectType
from project1.api.models import PurchaseModel, UserModel, PortfolioModel, StockModel


class PurchaseType(DjangoObjectType):
    class Meta:
        model = PurchaseModel


class UserType(DjangoObjectType):
    class Meta:
        model = UserModel


class PortfolioType(DjangoObjectType):
    class Meta:
        model = PortfolioModel


class StockType(DjangoObjectType):
    class Meta:
        model = StockModel


class Query(object):
    all_purchases = graphene.List(PurchaseType)
    all_users = graphene.List(UserType)
    all_portfolios = graphene.List(PortfolioType)
    all_stocks = graphene.List(StockType)

    def resolve_all_purchases(self, info, **kwargs):
        return PurchaseModel.objects.select_related("user").all()

    def resolve_all_users(self, info, **kwargs):
        return UserModel.objects.select_related("portfolio").all()

    def resolve_all_portfolios(self, info, **kwargs):
        return PortfolioModel.objects.all()

    def resolve_all_stocks(self, info, **kwargs):
        return StockModel.objects.select_related("portfolio").all()