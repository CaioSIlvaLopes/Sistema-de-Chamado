from django.db import models

class Client(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=100, blank=False,null=False)
    enterprise=models.CharField(max_length=100, blank=False,null=False)
    department=models.CharField(max_length=100, blank=False,null=False)
    code_department = models.CharField(max_length=20, default="DEF")

    def __str__(self):
        return self.name
    
class Technical(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=100, blank=False,null=False)
    number=models.CharField(max_length=20, blank=True,null=True)
    
    def __str__(self):
        return self.name