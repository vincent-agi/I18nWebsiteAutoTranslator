# I18NWebsiteAutoTranslator
## Description
As a developer by training, I've often had to deal with static text translations for websites and web applications. Working mostly with Angular, I've often had to maintain translation JSON files (I18n). 
Difficulties quickly became apparent. Maintaining consistency in file structure, getting the right translations, getting the right keys. This work is tedious and boring to say the least, but essential.
So I created this free program that lets you translate one or more JSON files into other languages while preserving the key structure.
On the whole, it's a fairly simple program, but it does what I set out to do. I'm open to suggestions for improvements.
Feel free to do whatever you like with it.

## Features
- Translate one JSON file to another language
- Can use all languages fron Deepl API (please respect language code for aguments origin-lang and target-lang)
- Keep keys file structure
- Translate only values
- Auto check if Deepl Api key is trial key or paid account

## Why this program
- Fully Free and open source phylosophy
- Quick
- Easy
- Usable with CLI (can be integrated in other software or process quality)
- Very lighweight

## Requierements
To use this program you need :
- Python3 installed on your computer
- Deepl API Key (on create account you can get one for free)

## How to start
- First git clone this project ```git clone https://github.com/vincent-agi/I18nWebsiteAutoTranslator.git```
- Then move to project directory ```cd I18nWebsiteAutoTranslator```
- Next install python requirements ```pip install requests```
- Create Deepl Account to get free (or paid) API Key and put it in deepl-key.json file
- Finaly, Enjoy use :)

## Examples
### Translate english JSON file stored at ./tests folder and create new file it.json in ./tests with italian translations
```
python main.py --origin-lang EN --target-lang IT --input-file ./tests/en.json --output-file ./tests/it.json
```
### Show help
```
python main.py --help
```

## How to know if all work fine ?
It's not very complicated to find out if the application is working properly. First you need a Deepl api key (free or paid, it doesn't matter). Enter your key in the deepl-key.json file. Then open terminal torun the unit tests with the command
```
python tests.py
```
If you get an "Ok" response, the application is working properly.

## How to find language code
you can find all language code available on Deepl API directly on Deepl documentation
https://www.deepl.com/docs-api/translate-text

## About me
- Young french Software Developer
- Technology enthusiast
- Known by the nickname Lez@rd21 (because i love lizards)
- I studied at IUT de Bayonne et du Pays Basque under direction amazing professors
- Work at Groupe Gallium

## Disclamer
I'm not responsable your use.
I encourage you check all JSON documents producted. You must know translation API isn't fully trust.

## License
This program is under lisence GNU Affero General Public License
