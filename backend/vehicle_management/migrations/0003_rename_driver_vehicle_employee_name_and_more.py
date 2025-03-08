# Generated by Django 5.1.6 on 2025-03-06 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle_management', '0002_vehicle_driver_vehicle_name_vehicle_notes'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehicle',
            old_name='driver',
            new_name='employee_name',
        ),
        migrations.AddField(
            model_name='vehicle',
            name='drive_type',
            field=models.CharField(blank=True, choices=[('2x4', '2x4'), ('4x4', '4x4')], max_length=10),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='engine_number',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='fuel_card_number',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='insurance_company',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='insurance_expiry',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='next_major_service_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='registration_expiry',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='rim_color',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('maintenance', 'In Maintenance'), ('off_road', 'Off Road'), ('decommissioned', 'Decommissioned')], default='active', max_length=20),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='tyre_size',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='current_mileage',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
