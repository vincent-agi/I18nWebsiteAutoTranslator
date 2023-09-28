import unittest
from unittest.mock import Mock

from requests import patch
from main import *

class TestTranslateDict(unittest.TestCase):

    def test_translate_strings(self):
        # Teste la traduction de chaînes de caractères
        input_dict = {"hello": "bonjour", "cat": "chat", "dog": "chien"}
        original_lang = "en"
        target_lang = "fr"
        deepl_api_key = ""
        with open("deepl-key.json", "r") as key_file:
                deepl_api_key = json.load(key_file)["deepl-key"]

        translated_dict = translate_dict(input_dict, original_lang, target_lang, deepl_api_key)

        expected_dict = {"hello": "bonjour", "cat": "chat", "dog": "chien"}
        self.assertEqual(translated_dict, expected_dict)

    def test_nested_dicts(self):
        # Teste la traduction de sous-dictionnaires
        input_dict = {"greetings": {"hello": "bonjour"}, "pets": {"cat": "chat", "dog": "chien"}}
        original_lang = "en"
        target_lang = "fr"
        deepl_api_key = ""
        with open("deepl-key.json", "r") as key_file:
                deepl_api_key = json.load(key_file)["deepl-key"]

        translated_dict = translate_dict(input_dict, original_lang, target_lang, deepl_api_key)

        expected_dict = {"greetings": {"hello": "bonjour"}, "pets": {"cat": "chat", "dog": "chien"}}
        self.assertEqual(translated_dict, expected_dict)

    def test_non_string_values(self):
        # Teste la préservation des valeurs non-chaînes de caractères
        input_dict = {"number": 42, "pi": 3.14159, "flag": True}
        original_lang = "en"
        target_lang = "fr"
        deepl_api_key = ""
        with open("deepl-key.json", "r") as key_file:
                deepl_api_key = json.load(key_file)["deepl-key"]
        translated_dict = translate_dict(input_dict, original_lang, target_lang, deepl_api_key)

        expected_dict = {"number": 42, "pi": 3.14159, "flag": True}
        self.assertEqual(translated_dict, expected_dict)

    def test_empty_dict(self):
        # Teste le cas d'un dictionnaire vide
        input_dict = {}
        original_lang = "en"
        target_lang = "fr"
        deepl_api_key = ""
        with open("deepl-key.json", "r") as key_file:
                deepl_api_key = json.load(key_file)["deepl-key"]

        translated_dict = translate_dict(input_dict, original_lang, target_lang, deepl_api_key)

        expected_dict = {}
        self.assertEqual(translated_dict, expected_dict)

if __name__ == '__main__':
    unittest.main()


class TestTranslateText(unittest.TestCase):

    @patch('requests.post')
    def test_translation_success(self, mock_post):
        deepl_api_key = ""
        with open("deepl-key.json", "r") as key_file:
                deepl_api_key = json.load(key_file)["deepl-key"]
        # Configurer le mock pour renvoyer une réponse réussie
        mock_response = mock_post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "translations": [{"text": "Translated text"}]
        }

        # Appeler la fonction et vérifier le résultat
        result = translate_text("Hello", "EN", "FR", deepl_api_key)
        self.assertEqual(result, "Translated text")

    @patch('requests.post')
    def test_translation_failure(self, mock_post):
        deepl_api_key = ""
        with open("deepl-key.json", "r") as key_file:
                deepl_api_key = json.load(key_file)["deepl-key"]
        # Configurer le mock pour renvoyer une réponse avec un code d'erreur
        mock_response = mock_post.return_value
        mock_response.status_code = 400  # Code d'erreur simulé

        # Appeler la fonction et vérifier que None est renvoyé en cas d'erreur
        result = translate_text("Hello", "EN", "FR", deepl_api_key)
        self.assertIsNone(result)

    @patch('requests.post')
    def test_missing_translations_key(self, mock_post):
        deepl_api_key = ""
        with open("deepl-key.json", "r") as key_file:
                deepl_api_key = json.load(key_file)["deepl-key"]
        # Configurer le mock pour renvoyer une réponse sans la clé "translations"
        mock_response = mock_post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "other_key": "Some data"
        }

        # Appeler la fonction et vérifier que None est renvoyé en cas de clé manquante
        result = translate_text("Hello", "EN", "FR", deepl_api_key)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()