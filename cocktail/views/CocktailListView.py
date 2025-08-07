from cocktail.models import Cocktail
from django.shortcuts import render, redirect

def redirect_home(request):
    return redirect('cocktail_list')

def cocktail_list_view(request):
    sort = request.GET.get('sort', 'date')
    if sort == 'name':
        cocktails = Cocktail.objects.order_by('name')
    elif sort == 'model':
        cocktails = Cocktail.objects.order_by('model_used')
    else:
        cocktails = Cocktail.objects.order_by('-created_at')
    return render(request, 'cocktail/cocktail_list.html', {'cocktails': cocktails, "sort": sort})