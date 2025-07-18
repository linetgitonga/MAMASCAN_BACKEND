from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ResourceRating, Resource

@receiver(post_save, sender=ResourceRating)
@receiver(post_delete, sender=ResourceRating)
def update_resource_rating(sender, instance, **kwargs):
    """Update resource average rating when a rating is added/updated/deleted"""
    resource = instance.resource
    ratings = ResourceRating.objects.filter(resource=resource)
    if ratings.exists():
        avg_rating = sum(r.rating for r in ratings) / len(ratings)
        resource.rating = round(avg_rating, 1)
    else:
        resource.rating = 0.0
    resource.save(update_fields=['rating'])