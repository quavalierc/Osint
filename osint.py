# Projet Osint (scrapping Shein.com/nouveautée)

# Imports
from requests import get
from bs4 import BeautifulSoup as bs
from datetime import date, timedelta
import csv
import os
from genericpath import exists


# definition des catégories à récuperer
categories = {2030: "Femme", 2026: "Homme", 2031: "Enfant", 3636: "Chaussures"}
# categories = {2026: "Homme"}
class_name = 'S-product-item j-expose__product-item product-list__item'
num_page = 0
articles = []
csv_file = 'data/shein_export.csv'
date_max = "1900-01-01"
date_ext = date.today()

def build_url(date_ext, categorie, num_page):
    url = f"https://fr.shein.com/daily-new.html?daily={date_ext}&child_cat_id={categorie}&page={num_page}"
    return url

if __name__ == '__main__':

    # Check si le fichier existe déjà et dans ce cas on récupère la date de dernier chargement
    if exists(csv_file):
        file_exist = True
        file_mode = "a+"
        with open(csv_file) as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)
            for line in csv_reader:
                if line[0] > date_max:
                    date_max = line[0]
    else:
        file_exist = False
        file_mode = "w"

    if date_max == date_ext.isoformat():
        print("Extraction déjà réalisée aujourd'hui")
        exit()

    for i in range(8):

        for cat_id in categories.keys():
            # On charge la première page de la catégorie
            num_page = 1
            r = get(build_url(date_ext, cat_id, num_page))

            while True:
                soup = bs(r.text,'html.parser')
                page = soup.find_all("section", class_=class_name)

                # On arrete lorsque la page est vide (d'article)
                if len(page) == 0:
                    break
                # Pour chaque article, on récupère la date, la catégorie, l'id, la description et le lien vers une image
                for article in page:
                    articles.append(dict(Date=date_ext.isoformat(),
                                         Catégorie=categories[cat_id],
                                         Id=article["data-expose-id"].split('-')[1],
                                         Libelle=article["aria-label"],
                                         Image=article.find_next("img")["data-src"]
                                         ))

                # Page suivante
                num_page += 1
                r = get(build_url(date_ext, cat_id, num_page))

        # Date suivante
        date_ext = date_ext - timedelta(days=1)
        if date_ext.isoformat() <= date_max:
            break

    # Ecriture du résultat dans un fichier csv
    csv_columns = articles[0].keys()

    if not exists("data"):
        os.mkdir("data")

    with open(csv_file, file_mode, newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)

        if not file_exist:
            writer.writeheader()

        for article in articles:
            writer.writerow(article)

