import datetime
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.core.models import Item, DailyExpense, PaymentTransaction, MonthlyBalance, Trip, PaymentMode


@login_required
def reporting_dashboard(request):
    available_years = range(datetime.datetime.now().year - 5, datetime.datetime.now().year + 1)
    selected_year = request.GET.get('year', datetime.datetime.now().year)
    selected_month = request.GET.get('month', datetime.datetime.now().month)

    context = {
        'available_years': available_years,
        'selected_year': int(selected_year),
        'selected_month': int(selected_month),
    }

    return render(request, 'reports/reporting_dashboard.html', context)


@login_required
def monthly_expense_by_item(request):
    selected_year = request.GET.get('year', datetime.datetime.now().year)
    selected_month = request.GET.get('month', datetime.datetime.now().month)
    month = int(selected_month)
    year = int(selected_year)
    data = Item.get_monthly_aggregate_for_highlighted_items(user=request.user, month=month, year=year)

    items = [item['name'] for item in data]
    totals = [float(abs(item['total'])) for item in data if item['total'] is not None]

    context = {
        'items': items,
        'totals': totals,
        'month': month,
        'year': year,
    }
    return render(request, 'reports/monthly_expense_by_item.html', context)



@login_required
def monthly_expense_by_category(request):
    selected_year = request.GET.get('year', datetime.datetime.now().year)
    selected_month = request.GET.get('month', datetime.datetime.now().month)
    month = int(selected_month)
    year = int(selected_year)
    data = Item.get_monthly_aggregate_by_category(user=request.user, month=month, year=year)

    categories = [item['name'] for item in data]
    totals = [float(abs(item['total'])) for item in data]

    context = {
        'categories': categories,
        'totals': totals,
        'month': month,
        'year': year,
    }
    return render(request, 'reports/monthly_expense_by_category.html', context)


@login_required
def total_monthly_expenses(request):
    selected_year = request.GET.get('year', datetime.datetime.now().year)
    year = int(selected_year)
    data = []
    for month in range(1, 13):
        total = float(abs(DailyExpense.get_sum_of_expenses(user=request.user, month=month, year=year)))
        data.append({
            'month': month,
            'total': total
        })

    months = [item['month'] for item in data]
    totals = [item['total'] for item in data]

    context = {
        'months': months,
        'totals': totals,
        'year': year,
    }
    return render(request, 'reports/total_monthly_expenses.html', context)


@login_required
def expenses_by_payment_mode(request):
    selected_year = request.GET.get('year', datetime.datetime.now().year)
    selected_month = request.GET.get('month', datetime.datetime.now().month)
    month = int(selected_month)
    year = int(selected_year)

    payment_modes = PaymentMode.objects.values_list('id', 'name')
    modes = [mode[0] for mode in payment_modes]
    mode_labels = [mode[1] for mode in payment_modes]
    totals = [
        float(abs(PaymentTransaction.get_sum(user=request.user, month=month, year=year, mode=mode))) for mode in modes
    ]

    context = {
        'mode_labels': mode_labels,
        'totals': totals,
        'month': month,
        'year': year,
    }
    return render(request, 'reports/expenses_by_payment_mode.html', context)


@login_required
def payment_mode_breakdown(request):
    selected_year = request.GET.get('year', datetime.datetime.now().year)
    selected_month = request.GET.get('month', datetime.datetime.now().month)
    month = int(selected_month)
    year = int(selected_year)

    payment_modes = PaymentMode.objects.values_list('id', 'name')
    modes = [mode[0] for mode in payment_modes]
    mode_labels = [mode[1] for mode in payment_modes]
    datasets = []

    for mode, label in zip(modes, mode_labels):
        totals = PaymentTransaction.get_all(request.user, month, year, mode).values_list('amount', flat=True)
        abs_totals = [float(abs(total)) for total in totals]
        datasets.append({
            'label': label,
            'data': abs_totals,
            'backgroundColor': 'rgba(54, 162, 235, 0.2)',
            'borderColor': 'rgba(54, 162, 235, 1)',
            'borderWidth': 1
        })

    context = {
        'datasets': datasets,
        'month': month,
        'year': year,
    }
    return render(request, 'reports/payment_mode_breakdown.html', context)


@login_required
def trip_expense_report(request):
    trips = Trip.objects.all()
    trip_labels = [trip.location for trip in trips]
    trip_totals = [float(trip.cost) for trip in trips]

    context = {
        'trip_labels': trip_labels,
        'trip_totals': trip_totals,
    }
    return render(request, 'reports/trip_expense_report.html', context)


@login_required
def monthly_balance_report(request):
    selected_year = request.GET.get('year', datetime.datetime.now().year)
    year = int(selected_year)
    payment_modes = PaymentMode.objects.values_list('id', 'name')

    mode_ids = [mode[0] for mode in payment_modes]
    mode_names = [mode[1] for mode in payment_modes]

    colors = [
        'rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)',
        'rgba(75, 192, 192, 0.2)', 'rgba(153, 102, 255, 0.2)', 'rgba(255, 159, 64, 0.2)'
    ]
    border_colors = [
        'rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)', 'rgba(255, 159, 64, 1)'
    ]

    data = {mode_name: [] for mode_name in mode_names}

    for month in range(1, 13):
        for mode_id, mode_name in zip(mode_ids, mode_names):
            total_balance = float(
                abs(MonthlyBalance.get_cb(user=request.user, month=month, year=year, mode=mode_id))
            )
            data[mode_name].append(total_balance)

    context = {
        'months': list(range(1, 13)),
        'data': data,
        'year': year,
        'colors': colors,
        'border_colors': border_colors,
    }
    return render(request, 'reports/monthly_balance_report.html', context)


@login_required
def compare_expenses_balances(request):
    selected_year = request.GET.get('year', datetime.datetime.now().year)
    year = int(selected_year)

    payment_modes = PaymentMode.objects.values_list('id', 'name')

    mode_ids = [mode[0] for mode in payment_modes]
    mode_names = [mode[1] for mode in payment_modes]

    colors = [
        'rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)',
        'rgba(75, 192, 192, 0.2)', 'rgba(153, 102, 255, 0.2)', 'rgba(255, 159, 64, 0.2)'
    ]
    border_colors = [
        'rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)', 'rgba(255, 159, 64, 1)'
    ]

    expenses_data = []
    balances_data = {mode_name: [] for mode_name in mode_names}

    for month in range(1, 13):
        total_expenses = float(abs(DailyExpense.get_sum_of_expenses(user=request.user, month=month, year=year)))
        expenses_data.append(total_expenses)

        for mode_id, mode_name in zip(mode_ids, mode_names):
            opening_balance = float(
                abs(MonthlyBalance.get_cb(user=request.user, month=month, year=year, mode=mode_id)))
            balances_data[mode_name].append(opening_balance)

    context = {
        'months': list(range(1, 13)),
        'expenses_data': expenses_data,
        'balances_data': balances_data,
        'year': year,
        'colors': colors,
        'border_colors': border_colors,
    }
    return render(request, 'reports/compare_expenses_balances.html', context)


@login_required
def highlighted_items_report(request):
    selected_year = request.GET.get('year', datetime.datetime.now().year)
    selected_month = request.GET.get('month', datetime.datetime.now().month)
    month = int(selected_month)
    year = int(selected_year)
    data = Item.get_monthly_aggregate_for_highlighted_items(user=request.user, month=month, year=year)

    items = [item['name'] for item in data]
    totals = [float(abs(item['total'])) for item in data]

    context = {
        'items': items,
        'totals': totals,
        'month': month,
        'year': year,
    }
    return render(request, 'reports/highlighted_items_report.html', context)


@login_required
def user_expense_distribution(request):
    User = get_user_model()
    users = User.objects.all()
    user_totals = [
        abs(float(DailyExpense.objects.filter(transaction__user=user).aggregate(
            total=Sum('transaction__amount')
        )['total'] or 0))
        for user in users
    ]
    user_labels = [user.email for user in users]

    context = {
        'user_labels': user_labels,
        'user_totals': user_totals,
    }
    return render(request, 'reports/user_expense_distribution.html', context)


@login_required
def monthly_expense_trend(request):
    selected_year = request.GET.get('year', datetime.datetime.now().year)
    year = int(selected_year)
    monthly_expenses = []
    for month in range(1, 13):
        total = float(abs(DailyExpense.get_sum_of_expenses(user=request.user, month=month, year=year)))
        monthly_expenses.append(total)

    average_expense = sum(monthly_expenses) / len(monthly_expenses)

    context = {
        'months': list(range(1, 13)),
        'expenses': monthly_expenses,
        'average_expense': average_expense,
        'year': year,
    }
    return render(request, 'reports/monthly_expense_trend.html', context)

