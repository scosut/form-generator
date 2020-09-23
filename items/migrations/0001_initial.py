# Generated by Django 3.0.7 on 2020-06-17 19:29

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('forms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('title', models.CharField(max_length=255)),
                ('price', models.IntegerField()),
                ('image', models.ImageField(upload_to='forms/')),
                ('sizes', models.TextField()),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='forms.Form')),
            ],
        ),
    ]