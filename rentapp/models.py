from django.db import models

class Apartment(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    number_of_rooms = models.IntegerField()
    rent = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.address}, {self.city}"

class Tenant(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Lease(models.Model):
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Lease for {self.tenant} at {self.apartment}"
