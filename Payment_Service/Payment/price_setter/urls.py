from .views import (
    GetAllSubscriptionAmountsView,
    ChangeSubscriptionAmountView
    )
from django.urls import path

urlpatterns = [

    path('get-all-subscriptions-amount/', GetAllSubscriptionAmountsView.as_view()),
    path("update-amount/<int:pk>/", ChangeSubscriptionAmountView.as_view()),

]
