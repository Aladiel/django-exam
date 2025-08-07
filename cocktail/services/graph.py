import inspect

from django.core.files import File
from django.utils.text import slugify
from langchain_core.prompts import ChatPromptTemplate as PromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel
from typing import Optional
from langgraph.graph import StateGraph, END
from decouple import config

from .image_generation import generate_sdxl_image
from ..models.Cocktail import Cocktail

IMAGE_GEN_ENABLED = config("IMAGE_GEN_ENABLED", cast=bool, default=True)
AVAILABLE_MODELS = ["llama3:8b", "mixtral:8x7b"]
SDXL_KEY = config("SDXL_KEY")

def get_llm(model_name):
    return ChatOllama(model=model_name)

def handleError(state, e):
    caller = inspect.stack()[1].function
    print(f"[{caller}] Erreur LLM : {e}")
    state.reply = (
        "Désolé, je n’ai pas réussi à générer la fiche cocktail cette fois-ci. "
        "Merci de reformuler votre demande ou réessayez plus tard."
    )
    state.is_cocktail = False

def safe_model_choice(model_name):
    if model_name not in AVAILABLE_MODELS:
        return AVAILABLE_MODELS[0]
    return model_name

class CocktailState(BaseModel):
    user_prompt: Optional[str] = None
    is_cocktail: bool = False
    ingredients: Optional[list] = None
    name: Optional[str] = None
    description: Optional[str] = None
    music: Optional[str] = None
    image_prompt: Optional[str] = None
    translated_prompt: Optional[str] = None
    generated_image_path: Optional[str] = None
    reply: Optional[str] = None
    model_used: Optional[str] = "llama3:8b"

class IsCocktail(BaseModel):
    is_cocktail:bool



# === Vérification du prompt utilisateur : s'agit-il d'une demande de cocktail ? ===
is_cocktail_prompt = PromptTemplate.from_template("""
Tu es un assistant barman professionnel, et tu aimes varier les plaisirs et imaginer de nouvelles recettes originales de cocktails.
Ton travail sera dans un premier temps de déterminer si une demande est bien une demande de création de cocktail. Tu 
réponds en renvoyant UNIQUEMENT un booléen 'is_cocktail' :
- 'True" si l'input est une demande de création de cocktail 
- 'False' sinon.

Input de l'utilisateur : {user_prompt}
""")

def detect_cocktail_recipe(state: CocktailState) -> CocktailState:
    llm = get_llm(state.model_used)
    user_prompt = state.user_prompt
    structured_llm = llm.with_structured_output(IsCocktail)
    chain = is_cocktail_prompt | structured_llm

    try:
        result = chain.invoke({"user_prompt": user_prompt})
        print("Est-ce bien une demande de création de cocktail ? : ", result)
        state.is_cocktail = result.is_cocktail
    except Exception as e:
        handleError(state, e)
    return state


# === Extraction du message de l'utilisateur et formatage de la réponse ===
class CocktailJSON(BaseModel):
    name: str
    ingredients:list
    description: str
    music: str

extract_prompt = PromptTemplate.from_template("""
Tu dois extraire la demande de l'utilisateur concernant le cocktail qu'il souhaite. Il peut s'agir d'un contexte (
exemple : "cocktail signature pour un enterrement de vie de garçon"), ou de l'envie d'un client (exemple : "Mon 
client veut un cocktail saveur bacon avec des framboises, sans alcool").
Tu dois répondre OBLIGATOIREMENT avec un format JSON très spécifique :
{{
  "name": "Nom créatif",
  "ingredients": ["4cl gin", "2cl citron", "framboises fraîches", "..."],
  "description": "Une histoire courte ou une note d'ambiance.",
  "music": "Nom d'un style musical ou une chanson.",
}}
Contrainte : retourne uniquement le JSON, sans rien autour. Répond uniquement en Français !

Demande utilisateur : {user_prompt}
""")

def extract_JSON_info(state: CocktailState) -> CocktailState:
    llm = get_llm(state.model_used)
    user_prompt = state.user_prompt
    structured_llm = llm.with_structured_output(CocktailJSON)
    chain = extract_prompt | structured_llm

    try:
        result = chain.invoke({ "user_prompt": user_prompt })
        print("Réponse LLM : ", result)
        if not result.name or not result.ingredients:
            raise ValueError("Réponse LLM incomplète")
        # === Remplissage du state (CocktailState) ===
        state.ingredients = result.ingredients
        state.name = result.name
        state.description = result.description
        state.music = result.music
    except Exception as e:
        handleError(state, e)
    return state


# === Création d'image via Stable Diffusion ===
class CocktailImage(BaseModel):
    image_prompt: str

cocktail_image_prompt = PromptTemplate.from_template("""
En te basant UNIQUEMENT sur la description suivante :
"{description}"
et la liste d'ingrédients :
"{ingredients}"
génère un prompt d'illustration photoréaliste destiné à Stable Diffusion pour représenter le cocktail.
Ta réponse doit être un JSON au format :
{{
  "image_prompt": "prompt détaillé pour illustrer le cocktail, en français"
}}
Ne fais AUCUN commentaire ni explication, ne retourne que ce JSON.
""")

def generate_image_prompt(state: CocktailState) -> CocktailState:
    llm = get_llm(state.model_used)
    structured_llm = llm.with_structured_output(CocktailImage)
    chain = cocktail_image_prompt | structured_llm

    try:
        result = chain.invoke({ "description": state.description, "ingredients": state.ingredients })
        state.image_prompt = result.image_prompt
    except Exception as e:
        handleError(state, e)
    return state

# === Traduction du prompt image pour SDXL ===
class PromptTranslation(BaseModel):
    translated_prompt: str

translate_prompt = PromptTemplate.from_template("""
Traduis ce texte en anglais, sans commentaire, sans fioritures, sans rien ajouter : "{image_prompt}"
""")

def translate_image_prompt(state: CocktailState) -> CocktailState:
    llm = get_llm(state.model_used)
    structured_llm = llm.with_structured_output(PromptTranslation)
    chain = translate_prompt | structured_llm

    try:
        result = chain.invoke({ "image_prompt": state.image_prompt })
        state.translated_prompt = result.translated_prompt
    except Exception as e:
        handleError(state, e)
    return state

# === Appel API SDXL ===
def call_sdxl_api(state:CocktailState) -> CocktailState:
    if not IMAGE_GEN_ENABLED:
        state.generated_image_path = None
        state.reply = "La génération d'image est temporairement désactivée (mode test)"
        print(state.reply)
        return state
    else:
        if not state.name:
            state.reply = "Erreur : nom de cocktail manquant pour la génération d'image."
            return state

        image_filename = slugify(state.name) + ".png"
        image_path = generate_sdxl_image(state.translated_prompt, SDXL_KEY, outpath=f"media/cocktails/{image_filename}")
        if image_path:
            state.generated_image_path = image_path
        else:
            state.reply = "Impossible de générer l'image du cocktail. Merci de réessayer plus tard"
        return state

# === Enregistrement du cocktail en Base de données ===
def generate_cocktail(state: CocktailState) -> CocktailState:
    try:
        image_file_path = state.generated_image_path
        cocktail = Cocktail(
            name=state.name,
            ingredients=state.ingredients,
            description=state.description,
            music=state.music,
            image_prompt=state.image_prompt,
            translated_prompt=state.translated_prompt,
            prompt=state.user_prompt,
            model_used=state.model_used,
        )
        # === Assignation de l'image à ImageField ===
        if image_file_path:
            image_relative_path = image_file_path.replace("media/", "")
            with open(image_file_path, "rb") as f:
                cocktail.image.save(image_relative_path, File(f), save=False)
        cocktail.save()
    except Exception as e:
        print(f"[generate_cocktail] Erreur sauvegarde BDD : {e}")
        state.reply = "Impossible d'enregistrer le cocktail en base de données. "
    return state


# === Réponse à l'utilisateur ===
class ReplyContent(BaseModel):
    reply: str

acknowledge_prompt = PromptTemplate.from_template("""
Tu dois répondre à l'utilisateur pour lui confirmer que la tâche a bien été créée (ou non). Tu dois répondre avec un 
ton agréable et serviable, toujours en français.
Tu inclues le nom du cocktail et un résumé de la demande de l'utilisateur.

Demande de cocktail : {user_prompt}
Concept imaginé : {cocktail_name}
""")

def acknowledge_cocktail_creation(state: CocktailState) -> CocktailState:
    llm = get_llm(state.model_used)
    user_prompt = state.user_prompt
    cocktail_name = state.name

    structured_llm = llm.with_structured_output(ReplyContent)
    chain = acknowledge_prompt | structured_llm
    try:
        result = chain.invoke({ "cocktail_name": cocktail_name, "user_prompt": user_prompt })
        state.reply = result.reply
    except Exception as e:
        handleError(state, e)
    return state

# === Quand ce n'est pas une demande de cocktail ===
response_prompt = PromptTemplate.from_template("""
Tu dois répondre à la question posée en t'appuyant sur tes connaissances générales, sans inventer d'informations, 
ni t'étendre plus que nécessaire.
Tu rappelles à l'utilisateur que ta principale fonction est de créer des recettes de cocktails et que toute autre utilisation n'est pas optimisée.
Question : {user_prompt}
""")

def respond_to_user(state: CocktailState) -> CocktailState:
    llm = get_llm(state.model_used)
    user_prompt = state.user_prompt
    structured_llm = llm.with_structured_output(ReplyContent)
    chain = response_prompt | structured_llm

    try:
        result = chain.invoke({ "user_prompt": user_prompt })
        state.reply = result.reply
    except Exception as e:
        handleError(state,e)
    return state


# === Création du graphe ===
graph = StateGraph(CocktailState)

graph.add_node("detect_cocktail", detect_cocktail_recipe)
graph.add_node("extract_JSON", extract_JSON_info)
graph.add_node("generate_image_prompt", generate_image_prompt)
graph.add_node("translate_image_prompt", translate_image_prompt)
graph.add_node("call_sdxl_api", call_sdxl_api)
graph.add_node("generate_cocktail", generate_cocktail)
graph.add_node("acknowledge_cocktail", acknowledge_cocktail_creation)
graph.add_node("respond_to_user", respond_to_user)

graph.set_entry_point("detect_cocktail")
graph.add_conditional_edges(
    "detect_cocktail",
    lambda state: "extract_JSON" if state.is_cocktail else "respond_to_user",
)
graph.add_edge("extract_JSON", "generate_image_prompt")
graph.add_edge("generate_image_prompt", "translate_image_prompt")
graph.add_edge("translate_image_prompt", "call_sdxl_api")
graph.add_edge("call_sdxl_api", "generate_cocktail")
graph.add_edge("generate_cocktail", "acknowledge_cocktail")
graph.add_edge("acknowledge_cocktail", END)
graph.add_edge("respond_to_user", END)

assistant_graph = graph.compile()