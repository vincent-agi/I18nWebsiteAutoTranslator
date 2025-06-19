import argparse
import json
import requests

def translate_text(text, original_lang, target_lang, deepl_api_key):
    """Traduit un texte via l'API DeepL, retourne le texte d'origine en cas d'échec."""
    if not isinstance(text, str):
        return text
    if deepl_api_key.endswith("fx"):
        base_url = "https://api-free.deepl.com/v2/translate"
    else:
        base_url = "https://api.deepl.com/v2/translate"
    params = {
        "text": text,
        "source_lang": original_lang.upper(),
        "target_lang": target_lang.upper(),
        "auth_key": deepl_api_key,
    }
    try:
        response = requests.post(base_url, data=params, timeout=15)
        if response.status_code == 200:
            translation_data = response.json()
            if "translations" in translation_data:
                return translation_data["translations"][0]["text"]
            else:
                print("DeepL API: 'translations' not in response for text:", text)
        else:
            print(f"DeepL API error {response.status_code} for text: {text}")
    except Exception as e:
        print(f"Erreur DeepL sur '{text[:30]}...': {e}")
    return text  # fallback : on garde la valeur d'origine

def translate_any(obj, original_lang, target_lang, deepl_api_key):
    """Traduit récursivement toutes les valeurs str du JSON, quelle que soit la structure."""
    if isinstance(obj, str):
        return translate_text(obj, original_lang, target_lang, deepl_api_key)
    elif isinstance(obj, dict):
        return {k: translate_any(v, original_lang, target_lang, deepl_api_key) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Ne surtout pas mettre un return dans la boucle !
        return [translate_any(item, original_lang, target_lang, deepl_api_key) for item in obj]
    else:
        return obj  # int, float, None, bool, etc.

def main():
    parser = argparse.ArgumentParser(description="Traduction automatique de JSON DeepL.")
    parser.add_argument("--origin-lang", required=True, help="Langue d'origine (ex: FR).")
    parser.add_argument("--target-lang", required=True, help="Langue cible (ex: EN, ES, etc.).")
    parser.add_argument("--input-file", required=True, help="Chemin du JSON source.")
    parser.add_argument("--output-file", required=True, help="Chemin du JSON traduit.")
    parser.add_argument("--credits", action="store_true", help="Afficher les crédits.")
    args = parser.parse_args()

    if args.credits:
        print("Programme de traduction JSON avec DeepL.")
        print("Développé par Vincent AGI.")
        return

    try:
        with open("deepl-key.json", "r", encoding="utf-8") as key_file:
            deepl_key = json.load(key_file)["deepl-key"]
        with open(args.input_file, "r", encoding="utf-8") as input_file:
            input_data = json.load(input_file)
        translated_data = translate_any(
            input_data,
            args.origin_lang,
            args.target_lang,
            deepl_key
        )
        with open(args.output_file, "w", encoding="utf-8") as output_file:
            json.dump(translated_data, output_file, ensure_ascii=False, indent=4)
        print(f"Traduction terminée. Résultat dans {args.output_file}")
    except Exception as e:
        print(f"Une erreur s'est produite : {str(e)}")

if __name__ == "__main__":
    main()