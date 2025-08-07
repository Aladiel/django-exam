from django import forms

MODEL_CHOICES = [
    ("llama3:8b", "Llama 3 (créatif, rapide)"),
    ("mixtral:8x7b", "Mixtral (robuste)"),
]

class CocktailRequestForm(forms.Form):
    user_prompt = forms.CharField(
        label="La demande de cocktail",
        widget=forms.TextInput(attrs={'placeholder': 'Décrivez votre cocktail idéal'}),
        required=True
    )
    model_name = forms.ChoiceField(
        label="Modèle IA",
        choices=MODEL_CHOICES,
        required=True,
        initial="llama3:8b"
    )