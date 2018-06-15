# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-06-14 19:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgencyAllotmentPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Agency')),
            ],
            options={
                'verbose_name': 'Agency Allotment Price',
                'verbose_name_plural': 'Agencies Allotments Prices',
            },
        ),
        migrations.CreateModel(
            name='AgencyAllotmentSuplementPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Agency')),
            ],
            options={
                'verbose_name': 'Agency Allotment Suplement Price',
                'verbose_name_plural': 'Agencies Allotments Suplements Prices',
            },
        ),
        migrations.CreateModel(
            name='AgencyTransferPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Agency')),
            ],
            options={
                'verbose_name': 'Agency Transfer Price',
                'verbose_name_plural': 'Agencies Tranfers Prices',
            },
        ),
        migrations.CreateModel(
            name='AgencyTransferSupplementPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Agency')),
            ],
            options={
                'verbose_name': 'Agency Transfer Price',
                'verbose_name_plural': 'Agencies Tranfers Prices',
            },
        ),
        migrations.CreateModel(
            name='AllotmentBoardType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('board_type', models.CharField(choices=[('NB', 'NB'), ('BB', 'BB'), ('HB', 'HB'), ('FB', 'FB'), ('AI', 'AI')], max_length=2)),
            ],
            options={
                'verbose_name': 'Allotment Board Type',
                'verbose_name_plural': 'Alloments Boards Types',
            },
        ),
        migrations.CreateModel(
            name='AllotmentPaxCombo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pax_combo', models.CharField(choices=[('A', '1A'), ('AC', '1A1C'), ('AB', '1A1B'), ('ACC', '1A2C'), ('ACB', '1A1C1B'), ('ABB', '1A2B'), ('AA', '2A'), ('AAC', '2A1C'), ('AAB', '2A1B'), ('AACC', '2A2C'), ('AACB', '2A1C1B'), ('AABB', '2A2B'), ('AAA', '3A'), ('AAAC', '3A1C'), ('AAAB', '3A1B'), ('AAACC', '3A2C'), ('AAACB', '3A1C1B'), ('AAABB', '3A2B'), ('AS', '1A1S'), ('ASC', '1A1S1C'), ('ASB', '1A1S1B'), ('ASCC', '1A1S2C'), ('ASCB', '1A1S1C1B'), ('ASBB', '1A1S2B'), ('ASS', '1A2S'), ('ASSC', '1A2S1C'), ('ASSB', '1A2S1B'), ('ASSCC', '1A2S2C'), ('ASSCB', '1A2S1C1B'), ('ASSBB', '1A2S2B'), ('AAS', '2A1S'), ('AASC', '2A1S1C'), ('AASB', '2A1S1B'), ('AASCC', '2A1S2C'), ('AASCB', '2A1S1C1B'), ('AASBB', '2A1S2B'), ('S', '1S'), ('SC', '1S1C'), ('SB', '1S1B'), ('SCC', '1S2C'), ('SCB', '1S1C1B'), ('SBB', '1S2B'), ('SS', '2S'), ('SSC', '2S1C'), ('SSB', '2S1B'), ('SSCC', '2S2C'), ('SSCB', '2S1C1B'), ('SSBB', '2S2B'), ('SSS', '3S'), ('SSSC', '3S1C'), ('SSSB', '3S1B'), ('SSSCC', '3S2C'), ('SSSCB', '3S1C1B'), ('SSSBB', '3S2B')], max_length=5)),
            ],
            options={
                'verbose_name': 'Allotment Pax Combo',
                'verbose_name_plural': 'Allotments Paxes Combos',
            },
        ),
        migrations.CreateModel(
            name='AllotmentPaxTypeDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pax_type', models.CharField(choices=[('B', 'Baby'), ('C', 'Child'), ('A', 'Adult'), ('S', 'Senior')], max_length=1)),
                ('age_from', models.IntegerField()),
                ('age_to', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Allotment Pax Type Definition',
                'verbose_name_plural': 'Allotments Paxes Types Definitions',
            },
        ),
        migrations.CreateModel(
            name='AllotmentRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Allotment Room',
                'verbose_name_plural': 'Allotments Rooms',
            },
        ),
        migrations.CreateModel(
            name='AllotmentSupplement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('cost_type', models.CharField(choices=[('F', 'Fixed'), ('P', 'By Paxes'), ('D', 'By Days'), ('PD', 'By Paxes Days')], max_length=10)),
                ('automatic', models.BooleanField(default=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Allotment Supplement',
                'verbose_name_plural': 'Allotments Supplements',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('enabled', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProviderAllotmentCost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_from', models.DateField()),
                ('date_to', models.DateField()),
                ('name', models.CharField(max_length=50)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('board_type', models.CharField(choices=[('NB', 'NB'), ('BB', 'BB'), ('HB', 'HB'), ('FB', 'FB'), ('AI', 'AI')], max_length=2)),
                ('pax_combo', models.CharField(choices=[('A', '1A'), ('AC', '1A1C'), ('AB', '1A1B'), ('ACC', '1A2C'), ('ACB', '1A1C1B'), ('ABB', '1A2B'), ('AA', '2A'), ('AAC', '2A1C'), ('AAB', '2A1B'), ('AACC', '2A2C'), ('AACB', '2A1C1B'), ('AABB', '2A2B'), ('AAA', '3A'), ('AAAC', '3A1C'), ('AAAB', '3A1B'), ('AAACC', '3A2C'), ('AAACB', '3A1C1B'), ('AAABB', '3A2B'), ('AS', '1A1S'), ('ASC', '1A1S1C'), ('ASB', '1A1S1B'), ('ASCC', '1A1S2C'), ('ASCB', '1A1S1C1B'), ('ASBB', '1A1S2B'), ('ASS', '1A2S'), ('ASSC', '1A2S1C'), ('ASSB', '1A2S1B'), ('ASSCC', '1A2S2C'), ('ASSCB', '1A2S1C1B'), ('ASSBB', '1A2S2B'), ('AAS', '2A1S'), ('AASC', '2A1S1C'), ('AASB', '2A1S1B'), ('AASCC', '2A1S2C'), ('AASCB', '2A1S1C1B'), ('AASBB', '2A1S2B'), ('S', '1S'), ('SC', '1S1C'), ('SB', '1S1B'), ('SCC', '1S2C'), ('SCB', '1S1C1B'), ('SBB', '1S2B'), ('SS', '2S'), ('SSC', '2S1C'), ('SSB', '2S1B'), ('SSCC', '2S2C'), ('SSCB', '2S1C1B'), ('SSBB', '2S2B'), ('SSS', '3S'), ('SSSC', '3S1C'), ('SSSB', '3S1B'), ('SSSCC', '3S2C'), ('SSSCB', '3S1C1B'), ('SSSBB', '3S2B')], max_length=5)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Provider')),
                ('room_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.AllotmentRoom')),
            ],
            options={
                'verbose_name': 'Provider Allotment Cost',
                'verbose_name_plural': 'Providers Allotments Costs',
            },
        ),
        migrations.CreateModel(
            name='ProviderAllotmentRoomAvailability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_from', models.DateField()),
                ('date_to', models.DateField()),
                ('availability', models.SmallIntegerField(default=10)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Provider')),
                ('room_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.AllotmentRoom')),
            ],
            options={
                'verbose_name': 'Allotment Availability',
                'verbose_name_plural': 'Allotments Availabilities',
            },
        ),
        migrations.CreateModel(
            name='ProviderAllotmentSupplementCost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_from', models.DateField()),
                ('date_to', models.DateField()),
                ('name', models.CharField(max_length=50)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('board_type', models.CharField(choices=[('NB', 'NB'), ('BB', 'BB'), ('HB', 'HB'), ('FB', 'FB'), ('AI', 'AI')], max_length=2)),
                ('pax_combo', models.CharField(choices=[('A', '1A'), ('AC', '1A1C'), ('AB', '1A1B'), ('ACC', '1A2C'), ('ACB', '1A1C1B'), ('ABB', '1A2B'), ('AA', '2A'), ('AAC', '2A1C'), ('AAB', '2A1B'), ('AACC', '2A2C'), ('AACB', '2A1C1B'), ('AABB', '2A2B'), ('AAA', '3A'), ('AAAC', '3A1C'), ('AAAB', '3A1B'), ('AAACC', '3A2C'), ('AAACB', '3A1C1B'), ('AAABB', '3A2B'), ('AS', '1A1S'), ('ASC', '1A1S1C'), ('ASB', '1A1S1B'), ('ASCC', '1A1S2C'), ('ASCB', '1A1S1C1B'), ('ASBB', '1A1S2B'), ('ASS', '1A2S'), ('ASSC', '1A2S1C'), ('ASSB', '1A2S1B'), ('ASSCC', '1A2S2C'), ('ASSCB', '1A2S1C1B'), ('ASSBB', '1A2S2B'), ('AAS', '2A1S'), ('AASC', '2A1S1C'), ('AASB', '2A1S1B'), ('AASCC', '2A1S2C'), ('AASCB', '2A1S1C1B'), ('AASBB', '2A1S2B'), ('S', '1S'), ('SC', '1S1C'), ('SB', '1S1B'), ('SCC', '1S2C'), ('SCB', '1S1C1B'), ('SBB', '1S2B'), ('SS', '2S'), ('SSC', '2S1C'), ('SSB', '2S1B'), ('SSCC', '2S2C'), ('SSCB', '2S1C1B'), ('SSBB', '2S2B'), ('SSS', '3S'), ('SSSC', '3S1C'), ('SSSB', '3S1B'), ('SSSCC', '3S2C'), ('SSSCB', '3S1C1B'), ('SSSBB', '3S2B')], max_length=5)),
                ('allotment_supplement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.AllotmentSupplement')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Provider')),
                ('room_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.AllotmentRoom')),
            ],
            options={
                'verbose_name': 'Provider Allotment Supplement Cost',
                'verbose_name_plural': 'Providers Allotments Supplements Costs',
            },
        ),
        migrations.CreateModel(
            name='ProviderTransferCost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_from', models.DateField()),
                ('date_to', models.DateField()),
                ('name', models.CharField(max_length=50)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Provider')),
            ],
            options={
                'verbose_name': 'Provider Transfer Cost',
                'verbose_name_plural': 'Providers Transfers Costs',
            },
        ),
        migrations.CreateModel(
            name='ProviderTransferSupplementCost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_from', models.DateField()),
                ('date_to', models.DateField()),
                ('name', models.CharField(max_length=50)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Provider')),
            ],
            options={
                'verbose_name': 'Provider Transfer Supplement Cost',
                'verbose_name_plural': 'Providers Transfers Supplements Costs',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('category', models.CharField(choices=[('A', 'Allotment'), ('T', 'Transfer')], max_length=1)),
                ('enabled', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='TransferLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enabled', models.BooleanField(default=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Location')),
            ],
        ),
        migrations.CreateModel(
            name='TransferSupplement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('cost_type', models.CharField(choices=[('F', 'Fixed'), ('T', 'By Transports'), ('H', 'By Hours'), ('TH', 'By Transports Hours')], max_length=10)),
                ('automatic', models.BooleanField(default=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Transfer Supplement',
                'verbose_name_plural': 'Transfers Supplements',
            },
        ),
        migrations.CreateModel(
            name='TransferTransport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Transfer Transport',
                'verbose_name_plural': 'Transfers Transports',
            },
        ),
        migrations.CreateModel(
            name='TransportType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('max_capacity', models.SmallIntegerField()),
                ('cost_type', models.CharField(choices=[('P', 'By Pax'), ('T', 'By Transport')], max_length=1)),
            ],
            options={
                'verbose_name': 'Transport Type',
                'verbose_name_plural': 'Transport Types',
            },
        ),
        migrations.CreateModel(
            name='Allotment',
            fields=[
                ('service_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='config.Service')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Location')),
            ],
            bases=('config.service',),
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('service_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='config.Service')),
                ('location_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_from', to='config.TransferLocation')),
                ('location_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_to', to='config.TransferLocation')),
            ],
            bases=('config.service',),
        ),
        migrations.AddField(
            model_name='transfertransport',
            name='transport_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.TransportType'),
        ),
        migrations.AddField(
            model_name='providertransfersupplementcost',
            name='transfer_supplement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.TransferSupplement'),
        ),
        migrations.AddField(
            model_name='providertransfersupplementcost',
            name='transport_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.TransportType'),
        ),
        migrations.AddField(
            model_name='providertransfercost',
            name='transport_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.TransportType'),
        ),
        migrations.AddField(
            model_name='agencytransfersupplementprice',
            name='provider_transfer_supplement_cost',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.ProviderTransferSupplementCost'),
        ),
        migrations.AddField(
            model_name='agencytransferprice',
            name='provider_transfer_cost',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.ProviderTransferCost'),
        ),
        migrations.AddField(
            model_name='agencyallotmentsuplementprice',
            name='provider_allotment_supplement_cost',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.ProviderAllotmentSupplementCost'),
        ),
        migrations.AddField(
            model_name='agencyallotmentprice',
            name='provider_allotment_cost',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.ProviderAllotmentCost'),
        ),
        migrations.AddField(
            model_name='transfertransport',
            name='transfer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Transfer'),
        ),
        migrations.AddField(
            model_name='transfersupplement',
            name='transfer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Transfer'),
        ),
        migrations.AddField(
            model_name='providertransfersupplementcost',
            name='transfer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Transfer'),
        ),
        migrations.AddField(
            model_name='providertransfercost',
            name='transfer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Transfer'),
        ),
        migrations.AddField(
            model_name='providerallotmentsupplementcost',
            name='allotment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Allotment'),
        ),
        migrations.AddField(
            model_name='providerallotmentroomavailability',
            name='allotment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Allotment'),
        ),
        migrations.AddField(
            model_name='providerallotmentcost',
            name='allotment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Allotment'),
        ),
        migrations.AddField(
            model_name='allotmentsupplement',
            name='allotment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Allotment'),
        ),
        migrations.AddField(
            model_name='allotmentroom',
            name='allotment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Allotment'),
        ),
        migrations.AddField(
            model_name='allotmentpaxcombo',
            name='allotment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Allotment'),
        ),
        migrations.AddField(
            model_name='allotmentboardtype',
            name='allotment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Allotment'),
        ),
    ]
