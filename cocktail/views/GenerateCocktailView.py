from ..forms.form import CocktailRequestForm
from ..models import Cocktail
from ..services.graph import CocktailState, safe_model_choice, assistant_graph

from django.shortcuts import render


def generate_cocktail_view(request):
    result = None
    reply = None

    if request.method == 'POST':
        form = CocktailRequestForm(request.POST)
        if form.is_valid():
            prompt = form.cleaned_data['user_prompt']
            model = form.cleaned_data['model_name']
            model_used = safe_model_choice(model)

            # Récupération du state
            initial_state = CocktailState(user_prompt=prompt, model_used=model_used)

            # Exécution du graph -> renvoie un dictionnaire qu'on transforme de nouveau en state
            final_state_dict = assistant_graph.invoke(initial_state)
            final_state = CocktailState(**final_state_dict)

            # Si le cocktail existe (i.e s'il possède un id), on récupère l'objet. Sinon : on n'affiche rien,
            # mais on récupère le 'reply' qui contiendra tout de même une réponse de l'IA
            if final_state.cocktail_id:
                result = Cocktail.objects.get(id=final_state.cocktail_id)
            else:
                result = None
                reply = getattr(final_state, 'reply', None)

    else:
        form = CocktailRequestForm()
    return render(request, "cocktail/generate.html", {"form": form, "result": result, "reply": reply})
