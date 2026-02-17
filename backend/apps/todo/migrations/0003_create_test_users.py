"""Data migration: create admin and test users if they don't exist."""
from django.db import migrations


def create_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')

    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin',
        )

    if not User.objects.filter(username='test_user').exists():
        User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='test_user_password',
        )


def delete_users(apps, schema_editor):
    """Rollback: удалить созданных пользователей."""
    User = apps.get_model('auth', 'User')
    User.objects.filter(username__in=['admin', 'test_user']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0002_alter_category_id_alter_task_id'),
    ]

    operations = [
        migrations.RunPython(create_users, delete_users),
    ]
