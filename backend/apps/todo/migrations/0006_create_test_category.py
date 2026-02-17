"""Data migration: create test category if it doesn't exist."""
from django.db import migrations


def create_test_category(apps, schema_editor):
    Category = apps.get_model('todo', 'Category')
    from ulid import ULID

    if not Category.objects.filter(name='Test').exists():
        Category.objects.create(
            id=str(ULID()),
            name='Test',
            description='Тестовая категория',
            color='#3B82F6',
        )


def delete_test_category(apps, schema_editor):
    Category = apps.get_model('todo', 'Category')
    Category.objects.filter(name='Test').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0005_add_celery_task_id_to_task'),
    ]

    operations = [
        migrations.RunPython(create_test_category, delete_test_category),
    ]
