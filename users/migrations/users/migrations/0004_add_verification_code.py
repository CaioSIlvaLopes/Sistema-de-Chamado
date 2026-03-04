from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_account_email_confirmed'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='verification_code',
            field=models.CharField(max_length=6, null=True, blank=True),
        ),
    ]
