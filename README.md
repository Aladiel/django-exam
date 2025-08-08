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
 ### sur serveur local :  
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

 ### via image Docker :
   -> docker compose up --build :
     - va installer le modèle llama3:8b, mais pas mixtral (par souci de performance et d'espace mémoire)
     - ollama est géré sur un container à part (séparation des rôles, facilité de maintenance)
     - environnement prod/dev inutilisé : la command du docker-compose overwrite celle du Dockerfile. Gunicorn run le serveur dans tous les cas.
     - possibles problèmes de timeout sur la génération de cocktails : le temps alloué a été augmenté à 120s, mais peut nécessiter plus avec la génération d'image.
     

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

## 4) Limites et précautions
L'environnement : l'image Docker est chargée avec le fichier.env.demo, lequel a des infos censurées.  
Pour la génération d'image : API Stable Diffusion nécessite un compte utilisateur (un nouveau compte bénéficie de 15 crédits gratuits : https://platform.stability.ai/). Il faut récupérer la clef API et la mettre dans le fichier .env.prod, sinon la génération d'image ne sera pas fonctionnelle.  
Explication de ce choix : les LLMs sont déjà installés en local et lourd sur l'espace mémoire et la RAM. Faire un appel API plutôt qu'installer aussi SDXL en local permet de faire des économies de ressources.  

Toujours dans le .env.prod -> Option IMAGE_GEN_ENABLED : booléen qui peut se régler sur True ou False, et qui permet de désactiver la génération d'image (en cas de test, ou si la clef API fait défaut)  

Possibilité d'ajouter des LLMs à ceux dispo, mais attention à l'attribution des ressources !  
Mixtral non installé sur l'image Docker : pour le faire, il faut ajouter une ligne dans le docker-compose.yml  
Dans le container ollama :  
entrypoint: >  
      sh -c "  
      ollama serve &  
      sleep 5 &&  
      ollama pull llama3:8b &&  
      ollama pull mxitral8x7b &&  
      wait  
      "  
   
 ## 5) Améliorations
 Améliorer le visuel des cartes cocktails, en particulier la liste d'ingrédients  
 Indiquer le modèle à l'origine du cocktail et de l'image  
 Ajouter plus de modèles LLMs / permettre une génération d'image locale ou open-access  
 Fiches détaillées de chaque cocktail dispo en cliquant sur une carte  
 Système d'authentification plus poussé, permettant un accès admin pour le barman et user pour les clients qui feraient leurs suggestions et pourraient voir la galerie.  
 Export PDF (ou autre), ou partage des fiches sur réseaux  


 ## Conclusion
 Merci de votre lecture, n'hésitez pas à m'envoyer un message privé en cas de doute d'utilisation.  
 Si l'application vous plait, pensez à mettre un pouce bleu et à vous abonner.  

 Auteur : Jonathan Mougin
