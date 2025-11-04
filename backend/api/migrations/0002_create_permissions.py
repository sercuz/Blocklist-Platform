from django.db import migrations
from django.contrib.auth.models import Permission, ContentType

def create_permissions(apps, schema_editor):
    # Create content type for blocklist if it doesn't exist
    content_type, _ = ContentType.objects.get_or_create(app_label='api', model='blocklist')
    
    # Create permissions
    permissions_to_create = [
        ('view_blocklist', 'Can view blocklist'),
        ('add_blocklist', 'Can add to blocklist'),
        ('delete_blocklist', 'Can delete from blocklist'),
        ('view_logs', 'Can view logs'),
    ]
    
    for codename, name in permissions_to_create:
        Permission.objects.get_or_create(
            codename=codename,
            content_type=content_type,
            defaults={'name': name}
        )

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_permissions),
    ]
