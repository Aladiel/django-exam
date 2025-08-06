from django.db import models

class Cocktail(models.Model):
    name = models.CharField(max_length=50)
    ingredients = models.JSONField()
    prompt = models.TextField()
    description = models.TextField(blank=True, null=True)

    # Contient uniquement la suggestion du User (pas d'upload direct de musique)
    music = models.TextField(max_length=120, blank=True)

    # prompt pour la génération d'image via Midjourney : généré par IA via la liste d'ingrédients et l'éventuelle
    # description
    image_prompt = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='cocktails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name