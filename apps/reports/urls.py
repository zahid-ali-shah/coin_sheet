from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.reporting_dashboard, name='reporting_dashboard'),
    path('monthly_expense_by_mode/', views.monthly_expense_by_mode, name='monthly_expense_by_mode'),
    path('monthly_expense_by_item/', views.monthly_expense_by_item, name='monthly_expense_by_item'),
    path('monthly_expense_by_category/', views.monthly_expense_by_category, name='monthly_expense_by_category'),
    path('total_monthly_expenses/', views.total_monthly_expenses, name='total_monthly_expenses'),
    path('expenses_by_payment_mode/', views.expenses_by_payment_mode, name='expenses_by_payment_mode'),
    path('payment_mode_breakdown/', views.payment_mode_breakdown, name='payment_mode_breakdown'),
    path('trip_expense_report/', views.trip_expense_report, name='trip_expense_report'),
    path('monthly_balance_report/', views.monthly_balance_report, name='monthly_balance_report'),
    path('compare_expenses_balances/', views.compare_expenses_balances, name='compare_expenses_balances'),
    path('highlighted_items_report/', views.highlighted_items_report, name='highlighted_items_report'),
    path('user_expense_distribution/', views.user_expense_distribution, name='user_expense_distribution'),
    path('monthly_expense_trend/', views.monthly_expense_trend, name='monthly_expense_trend'),
]
