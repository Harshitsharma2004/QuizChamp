# Generated by Django 5.1.2 on 2025-04-06 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0003_category_question_choice'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='correct_answer',
            field=models.CharField(default='option1', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='question',
            name='option1',
            field=models.CharField(default='Option 1', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='question',
            name='option2',
            field=models.CharField(default='Option 2', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='question',
            name='option3',
            field=models.CharField(default='Option 3', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='question',
            name='option4',
            field=models.CharField(default='Option 4', max_length=255),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Choice',
        ),
    ]
