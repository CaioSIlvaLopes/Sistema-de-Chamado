from django.db import models


class Enterprise(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=200, null=False,blank=False)
    cnpj=models.CharField(max_length=14, null=False,blank=False)

    def __str__(self):
        return self.name
    
class Client(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=100, blank=False,null=False)
    enterprise=models.ForeignKey(Enterprise,on_delete=models.PROTECT,related_name='Empresa')
    department=models.CharField(max_length=100, blank=False,null=False)
    login = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128) 
    def __str__(self):
        return self.name
    
class Technical(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=100, blank=False,null=False)
    number=models.CharField(max_length=20, blank=True,null=True)
    
    def __str__(self):
        return self.name
    

