from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from user.managers import CustomUserManager
from django.utils import timezone
from django.conf import settings
import random, string
from datetime import datetime, date, time, timedelta
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

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
    plans = models.ManyToManyField("Plan", blank=True)
    
    


    objects = CustomUserManager()

    USERNAME_FIELD = "email"


    @property
    def get_profit_7(self):
        profits =0
        for plan in self.plans.all():
            profits+= plan.get_profit_7()
        return profits
    
    @property
    def get_free_investments(self):
        profits =0
        for plan in self.plans.all():
            profits+= plan.get_free()
        trans = self.transactions.filter(transaction_type="unsubscribe")
        unamounts  = 0
        for tran in trans:
            unamounts += tran.amount
        return profits - unamounts
    
    @property
    def get_unfree_investments(self):
        profits =0
        for plan in self.plans.all():
            profits+= plan.get_unfree()
        return profits
    
    
    @property
    def get_unfree_investments_principal(self):
        profits =0
        for plan in self.plans.all():
            profits+= plan.get_unfree_principal()
        return profits
    
    @property
    def get_unfree_investments_profit(self):
        profits =0
        for plan in self.plans.all():
            profits+= plan.get_unfree_profit()
        return profits
    
    @property
    def get_all_investments(self):
        return self.get_free_investments + self.get_unfree_investments



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
    



class Plan(models.Model):
    amount = models.FloatField(default=0)
    date = models.DateField(default=timezone.now)
    release_date = models.DateField(null=True, blank=True)
    interest = models.FloatField(default=0)
    investment_plan = models.ForeignKey("InvestmentPlan", on_delete=models.CASCADE, null=True)


    def get_profit(self):
        current_date = timezone.now().date() if timezone.now().date() < self.release_date else self.release_date
        days = (current_date - self.date).days
        total_days = (self.release_date - self.date).days
        return (self.amount * ((self.interest / 100) * (days/total_days)))
    
    def get_profit_7(self):
        if timezone.now().date() > self.release_date:
            return 0

        _7days_ago = timezone.now().date() - timedelta(days=7)
        days_no = (timezone.now().date() - self.date).days if self.date > _7days_ago else (timezone.now().date() - _7days_ago).days
        total_days = (self.release_date - self.date).days

        if total_days == 0:
            return 0  # To prevent division by zero

        return self.amount * ((self.interest / 100) * (days_no / total_days))
    
    def get_free(self):
        if(timezone.now().date() < self.release_date):
            return 0
        return (self.amount * ((self.interest / 100) * 1) +self.amount)
    
    def get_unfree(self):
        if(timezone.now().date() >= self.release_date):
            return 0
        current_date = timezone.now().date() if timezone.now().date() < self.release_date else self.release_date
        days = (current_date - self.date).days
        total_days = (self.release_date - self.date).days
        return (self.amount * ((self.interest / 100) * (days/total_days)) + self.amount)
    
    def get_unfree_profit(self):
        if(timezone.now().date() >= self.release_date):
            return 0
        current_date = timezone.now().date() if timezone.now().date() < self.release_date else self.release_date
        days = (current_date - self.date).days
        total_days = (self.release_date - self.date).days
        return (self.amount * ((self.interest / 100) * (days/total_days)))
    
    def get_unfree_principal(self):
        if(timezone.now().date() >= self.release_date):
            return 0
        return (self.amount)


class InvestmentPlan(models.Model):
    name = models.CharField(max_length=255)
    min_deposit = models.FloatField(default=0)
    max_deposit = models.FloatField(default=0)
    duration = models.IntegerField(default=0)
    duration_type = models.CharField(choices=(("weeks", "weeks"), ("months", "months")), max_length=255)
    interest = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Investment Plan"
        verbose_name_plural = "Investment Plans"
        ordering = ["min_deposit"]

    def __str__(self):
        return (f'{self.name} - {self.interest}% - {self.duration}{self.duration_type}')

class Transaction(models.Model):
    amount = models.FloatField(default=0)
    time = models.DateTimeField(default=timezone.now)
    transaction_type= models.CharField(choices=(("deposit", "Deposit"), ("withdrawal", "Withdrawal"),("subscribe","subscribe"),("unsubscribe","unsubscribe")), max_length=255)
    transaction_medium = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(choices=(("pending", "pending"), ("completed", "completed")), default="pending", max_length=255)
    email_status = models.CharField(choices=(("not sent", "not sent"), ("sent", "sent")), default="not sent", max_length=255)

    def __str__(self):
        user = User.objects.filter(transactions__in=[self]).first()
        if self.transaction_type == "deposit":
            return f"{self.transaction_type.capitalize()} via {self.transaction_medium} by {user.get_name()} - Amount: {self.amount}"
        return f"{self.transaction_type.capitalize()} by {user.get_name()} - Amount: {self.amount}"
    
    def save(self, *args, **kwargs):
        domain = SiteSetting.objects.filter(active=True).first().domain
        if self.pk is not None:
            user = User.objects.filter(transactions__in=[self]).first()
            original = Transaction.objects.get(pk=self.pk)
            if original.email_status == "not sent" and self.status == "sent" and self.transaction_type == "deposit" and self.transaction_medium != 'btc':
                details = TransactionDetail.objects.filter(active=True).first()
                html_message = render_to_string('deposit_template.html', {'details':details, "name": user.get_name(), "domain": domain, "type": self.transaction_medium, "amount": self.amount})
                plain_message = strip_tags(html_message)
                mail.send_mail('Deposit Notification', plain_message, settings.EMAIL_HOST_USER, [user.email], html_message=html_message)

        super(Transaction, self).save(*args, **kwargs)


class TransactionDetail(models.Model):
    address = models.CharField(max_length=255, blank=True, null=True)
    qr_code = models.ImageField(upload_to="QR/", blank=True, null=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    bank_account_number = models.CharField(max_length=255, null=True, blank=True)
    bank_account_name = models.CharField(max_length=255, null=True, blank=True)
    zelle_email =models.CharField(max_length=255, null=True, blank=True)
    cashapp_username=models.CharField(max_length=255, null=True, blank=True)
    cashapp_account_name = models.CharField(max_length=255, null=True, blank=True)
    paypal_email= models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True)

    def get_qr(self):
        try:
            return self.qr_code.url
        except ValueError:
            return ""
        
    def save(self, *args, **kwargs):
        if self.active:
            with transaction.atomic():
                TransactionDetail.objects.exclude(id=self.id).update(active=False)
        super().save(*args, **kwargs)


class SiteSetting(models.Model):
    support_email = models.EmailField(default="support@chestgold.net")
    support_phone = models.CharField(default="+1234567890", max_length=255)
    concierge_phone = models.CharField(default="+1234567890", max_length=255)
    expert_phone = models.CharField(default="+1234567890", max_length=255)
    domain = models.CharField(default="chestgold.net", max_length=255)

