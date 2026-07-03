from django.db import models

# Create your models here.

class EmpDetail(models.Model):
    emp_id = models.IntegerField(null=True)
    name = models.TextField()
    email = models.CharField(max_length = 500,)
    password = models.CharField(max_length = 500,)
    mob_no = models.BigIntegerField()
    salary = models.DecimalField(max_digits=20, decimal_places=2)
    title = models.CharField(max_length=500)
    
    # models.py
    date = models.CharField(max_length=255, null=True, blank=True)
    
    objects = models.Manager()
    
    class Meta:
        db_table = 'tbl_employee'
    

class LoggedInUser(models.Model):
    emp = models.OneToOneField(
        EmpDetail,
        on_delete=models.CASCADE,
        related_name='logged_in_user'
    )
    session_key = models.CharField(max_length=40, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        db_table = 'tbl_log_emp'