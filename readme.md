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

## Examples
### Translate english JSON file stored at ./tests folder and create new file it.json in ./tests with italian translations
```
python main.py --origin-lang EN --target-lang IT --input-file ./tests/en.json --output-file ./tests/it.json
```
### Show help
```
python main.py --help
```
## About me
- Young french Software Developer
- Technology enthusiast
- Known by the nickname Lez@rd21 (because i love lizards)
- I studied at IUT de Bayonne et du Pays Basque under direction amazing professors
- Work at Groupe Gallium

## License
This program is under lisence GNU Affero General Public License