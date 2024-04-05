from django.urls import path
from .views import save_transferred_credits_by_user, fetch_transfer_credits_requests_by_user

urlpatterns = [
    path('saveTransferCreditsofUser', save_transferred_credits_by_user, name="save-transferred-credits"),
    path('fetchTransferCreditsRequests', fetch_transfer_credits_requests_by_user, name="get-transfer-credits-requests-by-user"),
]