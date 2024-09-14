from django.db import models


# Abstract Model for common fields
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null= True)

    class Meta:
        abstract = True