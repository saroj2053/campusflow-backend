from django.db import models

class TransferCredits(models.Model):
    email = models.CharField(max_length=255)
    status = models.TextField()
    fromModules = models.JSONField(null=True)
    toModules = models.JSONField(null=True)
    possibleTransferrableCredits = models.IntegerField(null=True)
    # Timestamp fields
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.email} - Status: {self.status}, Created At: {self.created_at}, Updated At: {self.updated_at}"
