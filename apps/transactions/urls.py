from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('',                               views.journal,            name='journal'),
    path('ajouter/',                       views.add_transaction,    name='add'),
    path('modifier/<int:pk>/',             views.edit_transaction,   name='edit'),
    path('supprimer/<int:pk>/',            views.delete_transaction, name='delete'),
    path('exporter/csv/',                  views.export_csv,         name='export_csv'),
    path('analyse/',                       views.analyse,            name='analyse'),
    path('budgets/',                       views.budgets,            name='budgets'),
    path('budgets/supprimer/<int:pk>/',    views.delete_budget,      name='delete_budget'),
    path('categories/',                    views.manage_categories,  name='categories'),
    path('categories/supprimer/<int:pk>/', views.delete_category,    name='delete_category'),
    path('patrimoine/',                    views.patrimoine,         name='patrimoine'),
    path('patrimoine/ajouter/',            views.add_patrimoine,     name='add_patrimoine'),
    path('patrimoine/supprimer/<int:pk>/', views.delete_patrimoine,  name='delete_patrimoine'),
    path('api/parse-sms/',                 views.parse_sms_view,     name='parse_sms'),
    path('api/add-sms/',                   views.add_from_sms,       name='add_from_sms'),
    path('api/liste/',                     views.api_list,           name='api_list'),
    path('api/push/subscribe/',            views.push_subscribe,     name='push_subscribe'),
    path('api/push/check/',                views.push_check,         name='push_check'),
]
