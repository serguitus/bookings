# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-05-28 19:24

from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('config', '0001_initial'),
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('agencyinvoiceitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='finance.AgencyInvoiceItem')),
                ('date_from', models.DateTimeField()),
                ('date_to', models.DateTimeField()),
                ('list_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('list_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.CharField(max_length=1000)),
                ('reference', models.CharField(max_length=256)),
                ('status', models.CharField(choices=[('RQ', 'Requested'), ('OK', 'Confirmed'), ('CN', 'Cancelled')], default='RQ', max_length=2)),
            ],
            options={
                'verbose_name': 'Booking',
                'verbose_name_plural': 'Bookings',
            },
            bases=('finance.agencyinvoiceitem', models.Model),
        ),
        migrations.CreateModel(
            name='BookingAllotmentLinePax',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Booking Allotment Line Pax',
                'verbose_name_plural': 'Bookings Allotments Lines Paxes',
            },
        ),
        migrations.CreateModel(
            name='BookingPax',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('age', models.SmallIntegerField()),
            ],
            options={
                'verbose_name': 'Booking Pax',
                'verbose_name_plural': 'Bookings Paxes',
            },
        ),
        migrations.CreateModel(
            name='BookingService',
            fields=[
                ('providerinvoiceitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='finance.ProviderInvoiceItem')),
                ('date_from', models.DateTimeField()),
                ('date_to', models.DateTimeField()),
                ('list_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('list_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.CharField(max_length=1000)),
                ('status', models.CharField(choices=[('RQ', 'Requested'), ('OK', 'Confirmed'), ('CN', 'Cancelled')], default='RQ', max_length=2)),
            ],
            options={
                'verbose_name': 'Booking Service',
                'verbose_name_plural': 'Bookings Services',
            },
            bases=('finance.providerinvoiceitem', models.Model),
        ),
        migrations.CreateModel(
            name='BookingServiceLine',
            fields=[
                ('providerinvoiceitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='finance.ProviderInvoiceItem')),
                ('date_from', models.DateTimeField()),
                ('date_to', models.DateTimeField()),
                ('list_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('list_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.CharField(max_length=1000)),
                ('list_unit_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('list_unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('RQ', 'Requested'), ('OK', 'Confirmed'), ('CN', 'Cancelled')], default='RQ', max_length=2)),
            ],
            options={
                'verbose_name': 'Booking Service Line',
                'verbose_name_plural': 'Bookings Services Lines',
            },
            bases=('finance.providerinvoiceitem', models.Model),
        ),
        migrations.CreateModel(
            name='BookingServiceLineSupplement',
            fields=[
                ('providerinvoiceitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='finance.ProviderInvoiceItem')),
                ('date_from', models.DateTimeField()),
                ('date_to', models.DateTimeField()),
                ('list_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('list_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.CharField(max_length=1000)),
            ],
            options={
                'verbose_name': 'Booking Service Line Supplement',
                'verbose_name_plural': 'Bookings Services Lines Supplements',
            },
            bases=('finance.providerinvoiceitem', models.Model),
        ),
        migrations.CreateModel(
            name='BookingAllotment',
            fields=[
                ('bookingservice_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='booking.BookingService')),
                ('allotment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Allotment')),
            ],
            options={
                'verbose_name': 'Booking Allotment',
                'verbose_name_plural': 'Bookings Allotments',
            },
            bases=('booking.bookingservice',),
        ),
        migrations.CreateModel(
            name='BookingAllotmentLine',
            fields=[
                ('bookingserviceline_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='booking.BookingServiceLine')),
                ('board_type', models.CharField(choices=[('NB', 'NB'), ('BB', 'BB'), ('HB', 'HB'), ('FB', 'FB'), ('AI', 'AI')], max_length=2)),
                ('pax_combo', models.CharField(choices=[('A', '1A'), ('AC', '1A1C'), ('AB', '1A1B'), ('ACC', '1A2C'), ('ACB', '1A1C1B'), ('ABB', '1A2B'), ('AA', '2A'), ('AAC', '2A1C'), ('AAB', '2A1B'), ('AACC', '2A2C'), ('AACB', '2A1C1B'), ('AABB', '2A2B'), ('AAA', '3A'), ('AAAC', '3A1C'), ('AAAB', '3A1B'), ('AAACC', '3A2C'), ('AAACB', '3A1C1B'), ('AAABB', '3A2B'), ('AS', '1A1S'), ('ASC', '1A1S1C'), ('ASB', '1A1S1B'), ('ASCC', '1A1S2C'), ('ASCB', '1A1S1C1B'), ('ASBB', '1A1S2B'), ('ASS', '1A2S'), ('ASSC', '1A2S1C'), ('ASSB', '1A2S1B'), ('ASSCC', '1A2S2C'), ('ASSCB', '1A2S1C1B'), ('ASSBB', '1A2S2B'), ('AAS', '2A1S'), ('AASC', '2A1S1C'), ('AASB', '2A1S1B'), ('AASCC', '2A1S2C'), ('AASCB', '2A1S1C1B'), ('AASBB', '2A1S2B'), ('S', '1S'), ('SC', '1S1C'), ('SB', '1S1B'), ('SCC', '1S2C'), ('SCB', '1S1C1B'), ('SBB', '1S2B'), ('SS', '2S'), ('SSC', '2S1C'), ('SSB', '2S1B'), ('SSCC', '2S2C'), ('SSCB', '2S1C1B'), ('SSBB', '2S2B'), ('SSS', '3S'), ('SSSC', '3S1C'), ('SSSB', '3S1B'), ('SSSCC', '3S2C'), ('SSSCB', '3S1C1B'), ('SSSBB', '3S2B')], max_length=5)),
                ('allotment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Allotment')),
                ('room_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.AllotmentRoom')),
            ],
            options={
                'verbose_name': 'Booking Allotment Line',
                'verbose_name_plural': 'Bookings Allotments Lines',
            },
            bases=('booking.bookingserviceline', models.Model),
        ),
        migrations.CreateModel(
            name='BookingAllotmentLineSupplement',
            fields=[
                ('bookingservicelinesupplement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='booking.BookingServiceLineSupplement')),
                ('supplement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.AllotmentSupplement')),
            ],
            options={
                'verbose_name': 'Booking Allotment Line Supplement',
                'verbose_name_plural': 'Bookings Allotments Lines Supplements',
            },
            bases=('booking.bookingservicelinesupplement',),
        ),
        migrations.CreateModel(
            name='BookingTransfer',
            fields=[
                ('bookingservice_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='booking.BookingService')),
                ('transfer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Transfer')),
            ],
            options={
                'verbose_name': 'Booking Transfer',
                'verbose_name_plural': 'Bookings Transfers',
            },
            bases=('booking.bookingservice',),
        ),
        migrations.CreateModel(
            name='BookingTransferLine',
            fields=[
                ('bookingserviceline_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='booking.BookingServiceLine')),
                ('pax_qtty', models.SmallIntegerField()),
                ('transport_qtty', models.SmallIntegerField(default=1)),
                ('transfer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Transfer')),
                ('transport_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.TransportType')),
            ],
            options={
                'verbose_name': 'Booking Transfer Line',
                'verbose_name_plural': 'Bookings Transfers Lines',
            },
            bases=('booking.bookingserviceline', models.Model),
        ),
        migrations.CreateModel(
            name='BookingTransferLineSupplement',
            fields=[
                ('bookingservicelinesupplement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='booking.BookingServiceLineSupplement')),
                ('hours', models.SmallIntegerField(default=1)),
                ('supplement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.TransferSupplement')),
            ],
            options={
                'verbose_name': 'Booking Transfer Line Supplement',
                'verbose_name_plural': 'Bookings Transfers Lines Supplements',
            },
            bases=('booking.bookingservicelinesupplement',),
        ),
        migrations.AddField(
            model_name='bookingservicelinesupplement',
            name='booking_service_line',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.BookingServiceLine'),
        ),
        migrations.AddField(
            model_name='bookingserviceline',
            name='booking_service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.BookingService'),
        ),
        migrations.AddField(
            model_name='bookingservice',
            name='booking',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.Booking'),
        ),
        migrations.AddField(
            model_name='bookingservice',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Service'),
        ),
        migrations.AddField(
            model_name='bookingallotmentlinepax',
            name='booking_pax',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.BookingPax'),
        ),
        migrations.AddField(
            model_name='bookingallotmentlinepax',
            name='booking_allotment_line',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.BookingAllotmentLine'),
        ),
    ]
