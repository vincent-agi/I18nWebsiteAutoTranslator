import argparse
import json
import requests


def translate_text(text, original_lang, target_lang, deepl_api_key):
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

    response = requests.post(base_url, data=params)
    if response.status_code == 200:
        translation_data = response.json()
        if "translations" in translation_data:
            return translation_data["translations"][0]["text"]
    return None


def translate_dict(input_dict, original_lang, target_lang, deepl_api_key):
    output_dict = {}
    for key, value in input_dict.items():
        if isinstance(value, str):
            # Traduire uniquement les valeurs de type chaîne de caractères
            translated_value = translate_text(value, original_lang, target_lang, deepl_api_key)
            if translated_value:
                output_dict[key] = translated_value
            else:
                output_dict[key] = value
        elif isinstance(value, dict):
            # Appel récursif pour les sous-dictionnaires
            output_dict[key] = translate_dict(value, original_lang, target_lang, deepl_api_key)
        else:
            # Conserver les autres types de valeurs tels quels
            output_dict[key] = value
    return output_dict


def main():
    parser = argparse.ArgumentParser(description="Help to auto translate I18N JSON file using famous Deepl API.")
    parser.add_argument("--origin-lang", required=True, help="Original language from input file.")
    parser.add_argument("--target-lang", required=True, help="Target language you wish output file will translate.")
    parser.add_argument("--input-file", required=True, help="Relatif path to original file.")
    parser.add_argument("--output-file", required=True, help="Relatif path to output file.")
    parser.add_argument("--credits", action="store_true", help="Show 'Abouts' informations.")

    args = parser.parse_args()

    if args.credits:
        print("Programme de traduction JSON avec DeepL.")
        print("Développé par Vincent AGI.")
        print("Plus d'informations dans le fichier README.md.")
    else:
        try:
            with open("deepl-key.json", "r") as key_file:
                deepl_key = json.load(key_file)["deepl-key"]

            with open(args.input_file, "r") as input_file:
                input_data = json.load(input_file)

            original_lang = args.origin_lang
            target_lang = args.target_lang
            translated_data = translate_dict(input_data, original_lang, target_lang, deepl_key)

            with open(args.output_file, "w+") as output_file:
               json.dump(translated_data, output_file, ensure_ascii=False, indent=4)

            print(f"Translation done. Result in {args.output_file}")
        except Exception as e:
            print(f"Une erreur s'est produite : {str(e)}")


if __name__ == "__main__":
    main()
