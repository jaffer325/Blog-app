from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Post


def create_groups_permissions(sender, **kwargs):
    try:

        # Create groups
        readers_group, _ = Group.objects.get_or_create(name="Readers")
        editors_group, _ = Group.objects.get_or_create(name="Editors")
        authors_group, _ = Group.objects.get_or_create(name="Authors")

        # Get content type for Post model
        content_type = ContentType.objects.get_for_model(Post)

        # Custom permission
        can_publish, _ = Permission.objects.get_or_create(
            codename="can_publish",
            name="Can publish post",
            content_type=content_type
        )

        # Permissions
        readers_permissions = [
            Permission.objects.get(codename="view_post")
        ]

        authors_permissions = [
            Permission.objects.get(codename="add_post"),
            Permission.objects.get(codename="change_post"),
            Permission.objects.get(codename="delete_post"),
        ]

        editors_permissions = [
            Permission.objects.get(codename="add_post"),
            Permission.objects.get(codename="change_post"),
            Permission.objects.get(codename="delete_post"),
            can_publish
        ]

        # Assign permissions
        readers_group.permissions.set(readers_permissions)
        authors_group.permissions.set(authors_permissions)
        editors_group.permissions.set(editors_permissions)

        print("Groups and Permissions created successfully")

    except Exception as e:
        print(f"Error occurred: {e}")