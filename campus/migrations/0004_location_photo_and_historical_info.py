from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campus', '0003_location_image_url_alter_location_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='historical_info',
            field=models.TextField(
                blank=True,
                help_text='Optional historical context or fun facts for visitors.',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='location',
            name='photo',
            field=models.ImageField(
                blank=True,
                help_text='Upload location photo.',
                null=True,
                upload_to='locations/photos/',
            ),
        ),
        migrations.AlterField(
            model_name='location',
            name='address',
            field=models.CharField(
                blank=True,
                help_text='Street address or building details shown in the tour.',
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name='location',
            name='category',
            field=models.CharField(
                blank=True,
                help_text='Category used for filtering (e.g., Dining, Academic).',
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name='location',
            name='description',
            field=models.TextField(
                help_text='High-level overview that appears in campus tour content.',
            ),
        ),
        migrations.AlterField(
            model_name='location',
            name='image_url',
            field=models.URLField(
                blank=True,
                help_text='Link to an external photo if one is hosted elsewhere.',
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='location',
            name='latitude',
            field=models.DecimalField(
                decimal_places=6,
                help_text='Latitude in decimal degrees (positive for north).',
                max_digits=9,
            ),
        ),
        migrations.AlterField(
            model_name='location',
            name='longitude',
            field=models.DecimalField(
                decimal_places=6,
                help_text='Longitude in decimal degrees (negative for west).',
                max_digits=9,
            ),
        ),
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(
                help_text='Displayed name of the campus location.',
                max_length=120,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name='location',
            name='slug',
            field=models.SlugField(
                blank=True,
                help_text='URL-friendly identifier auto-generated from the name.',
                unique=True,
            ),
        ),
    ]
