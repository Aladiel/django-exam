# Read-me

<center>Vous pouvez modifier ce fichier (cf. Brief)</center>

## Comment gérer cette évaluation ?

1. Le rendu s'effectuera **uniquement** au travers de Github Classroom (clonez bien le repository créé par Github Classroom, et travaillez dedans. N'en recréez pas un nouveau). 
2. Une Pull-Request est automatiquement générée par Github Classroom, **ne la fermez pas**. Elle me permettra de vous faire un feedback sous forme de code annoté. 
3. Mettez-vous en condition d'une mise en situation professionnelle : le client (fictif, bien entendu) attend une app fonctionnelle qui répond au besoin énoncé, c'est tout :) 
4. Lisez bien l'entièreté du brief avant de démarrer, n'hésitez pas à poser votre architecture sur papier (ou du moins à y réfléchir sur un support autre que l'IDE) avant de coder. 

➡️ [Cliquez ici pour lire le brief du client](BRIEF.md)

# Compte-rendu du développement
Langage : Python 3.12
Stack : Django, Langchain, Ollama, Stable Diffusion XL, TailwindCSS, Docker

 ## 1) Choix de la stack

### Backend : Framework Django
  -> Robuste et facile à déployer. ORM intégré, gestion des templates inclues, sécurité native.  
  -> L'alternative Flask aurait demandé beaucoup plus de temps pour coder à la main les formulaires, la gestion admin, l'ORM.  

### Frontend : Framework Django (Templates) + TailwindCSS
  -> Templates suffisant pour un projet de cette envergure (2 pages et un mode admin)  
  -> Alternative : React. Overkill pour un projet de cette taille, aurait nécessité une plus grosse gestion des droits, sécurité CSRF, CORS  
  -> TailwindCSS : tout ce qui peut alléger le CSS est bon à prendre !  
  -> widget-tweaks : personnalisation facilitée des formulaires Django  

### LLM : Ollama (local) 
  -> LLM local open-source, nécessitant une machine capable de le faire tourner, mais utilisable hors ligne et sans dépendance ni fuite de données.  
  -> LangChain : simplification de la gestion des prompts pour les LLM, gestion détaillée du cycle de vie  
  -> Possiblité de choisir entre plusieurs modèles (par défaut, Llama3 et Mixtral, mais extensible facilement)  
    - Llama3 : créatif, léger et rapide. Peut avoir du mal à respecter le format demandé dans ses réponses.  
    - Mixtral : plus costaud, nécessite une bonne machine et beaucoup de RAM (suggéré : 32GB), mais très efficace et imaginatif  
 
### Génération d'image : Stable Diffusion XL
  -> Accessible via API (pas de déploiement local supplémentaire, les LLMs consomme déjà beaucoup)  
  -> Bonne qualité d'image, respecte bien les prompts  
  -> Désavantages : Limitation du nombre de réalisation (crédits), nécessite des prompts en anglais exclusivement  

 ## 2) Installation
-> Clone du repo  
-> Création de l'environnement virtuel et installation des dépendances  
    python -m venv .env  
    .venv\Scripts\activate    (sous Windows)  
    pip install -r requirements.txt  
-> Variables d'environnement : jeu de test proposé  (.env.demo)
-> Installation d'Ollama : installer les modèles proposés (au moins llama3, plus léger ~3 à 4 GB)  
    Dans une console de commande :  
      - ollama pull llama3:8b  
      - ollama pull mixtral:8x7b  
-> effectuer les migrations :  
    - python manage.py makemigrations  
    - python manage.py migrate  
-> lancer le serveur Django : python manage.py runserver  

## 3) User Guide
Une fois le serveur lancé :  
http://localhost:8000/  -> redirige sur la galerie http://localhost:8000/cocktails/  
La galerie présente la liste des cocktails créés, avec les images associées, le nom, la musique suggérée, une brève description et la liste d'ingrédients.  
Un filtre est disponible pour trier les résultats selon différents critères : date de création, nom, modèle utilisé.  
Note : pour le modèle utilisé, il me faudrait rajouté la mention du modèle dans la présentation des cocktails.  

Depuis la galerie : bouton "Nouveau cocktail", ou http://localhost:8000/generate/  -> page de création de cocktails  
Zone de texte pour écrire le prompt : le modèle est prévu pour créer des cocktails. Il peut répondre aux questions générales, mais est censé recadrer l'utilisateur sur son utilité première (censé, car Mixtral le fait bien mais llama3 a plus de mal)  
Choix du modèle à sélectionner.
Bouton Submit "Shaker !"
