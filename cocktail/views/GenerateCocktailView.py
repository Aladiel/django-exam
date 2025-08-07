from ..forms.form import CocktailRequestForm
from ..models import Cocktail
from ..services.graph import CocktailState, safe_model_choice, assistant_graph

from django.shortcuts import render


def generate_cocktail_view(request):
    result = None
    if request.method == 'POST':
        form = CocktailRequestForm(request.POST)
        if form.is_valid():
            prompt = form.cleaned_data['user_prompt']
            model = form.cleaned_data['model_name']
            model_used = safe_model_choice(model)

            state = CocktailState(user_prompt=prompt, model_used=model_used)
            assistant_graph.invoke(state)

            if Cocktail.objects.exists():
                generated_cocktail = Cocktail.objects.latest('created_at')
            else:
                generated_cocktail = None
            result = generated_cocktail

    else:
        form = CocktailRequestForm()
    return render(request, "cocktail/generate.html", {"form": form, "result": result})
