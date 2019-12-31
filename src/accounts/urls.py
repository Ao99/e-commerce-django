from django.urls import path
from .views import (
    ProfileView,
    cancel_order,
    reorder,
)

app_name = 'accounts'
urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/ref-code-<ref_code>', ProfileView.as_view(), name='show-items'),
    path('cancel-order/<ref_code>', cancel_order, name='cancel-order'),
    path('reorder/<ref_code>', reorder, name='reorder'),
]
