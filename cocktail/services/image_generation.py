import requests
import os

def generate_sdxl_image(prompt, api_key, outpath="media/generated_cocktail.png"):
    directory = os.path.dirname(outpath)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/png",
    }
    payload = {
        "text_prompts": [{"text": prompt}],
        "samples": 1,
        "steps": 30,
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        with open(outpath, "wb") as f:
            f.write(response.content)
        return outpath
    else:
        print(f"Failed to generate image. Status code: {response.status_code} {response.text}")
        return None