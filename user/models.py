from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from user.managers import CustomUserManager
from django.utils import timezone
from django.conf import settings
import random, string


class User(AbstractUser):
    username = None
    REQUIRED_FIELDS = []

    email = models.EmailField(_("email address"), unique=True)
    profile_pic = models.ImageField(upload_to="Profile pictures", null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=6, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    next_of_kin = models.CharField(max_length=255, null=True, blank=True)
    next_of_kin_phone = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, default="available")
    ref = models.CharField(max_length=255, null=True, blank=True)
    dep_type = models.CharField(max_length=255, null=True, blank=True)
    usd = models.FloatField(null=True, blank=True)
    btc = models.FloatField(null=True, blank=True)
    transactions = models.ManyToManyField("Transaction", blank=True)
    email_confirmation_code = models.CharField(max_length=6, null=True, blank=True)
    otpt = models.DateTimeField(default=timezone.now)
    
    


    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email
    
    def get_name(self):
        name = self.first_name if self.first_name else ""
        if self.last_name:
            name += " " + self.last_name
        return name
    
    def gen_ref(self, length=10):
        characters = string.ascii_letters + string.digits
        uniq=False
        while not uniq:
            ref = ''.join(random.choice(characters) for _ in range(length))
            u = User.objects.filter(ref=ref).first()
            if(not u):
                self.ref= ref
                self.save()
                uniq=True

    
    def get_ref(self):
        if(not self.ref):
            self.gen_ref()
        return self.ref
    
    def get_balance(self):
        transactions = self.transactions.filter(status="completed")
        return sum([t.amount for t in transactions if t.transaction_type == "deposit" or t.transaction_type == "unsubscribe"]) - sum([t.amount for t in transactions if t.transaction_type == "withdrawal" or t.transaction_type == "subscribe"])
    
    def get_total_deposit(self):
        transactions = self.transactions.filter(status="completed")
        return sum([t.amount for t in transactions if t.transaction_type == "deposit"])
    
    def get_total_deposit_this_month(self):
        transactions = self.transactions.filter(status="completed", time__month=timezone.now().month)
        return sum([t.amount for t in transactions if t.transaction_type == "deposit"])
    
    def get_total_withdrawal_this_month(self):
        transactions = self.transactions.filter(status="completed", time__month=timezone.now().month)
        return sum([t.amount for t in transactions if t.transaction_type == "withdrawal"])
    
    def get_total_withdrawal(self):
        transactions = self.transactions.filter(status="completed")
        return sum([t.amount for t in transactions if t.transaction_type == "withdrawal"])

class Transaction(models.Model):
    amount = models.FloatField(default=0)
    time = models.DateTimeField(default=timezone.now)
    transaction_type= models.CharField(choices=(("deposit", "Deposit"), ("withdrawal", "Withdrawal"),("subscribe","subscribe"),("unsubscribe","unsubscribe")), max_length=255)
    status = models.CharField(choices=(("pending", "pending"), ("completed", "completed")), default="pending", max_length=255)


class Address(models.Model):
    address = models.CharField(max_length=255)
    qr_code = models.ImageField(upload_to="QR/", blank=True, null=True)
    active = models.BooleanField(default=True)

    def get_qr(self):
        try:
            return self.qr_code.url
        except ValueError:
            return ""
        
    def save(self, *args, **kwargs):
        if self.active:
            with transaction.atomic():
                Address.objects.exclude(id=self.id).update(active=False)
        super().save(*args, **kwargs)