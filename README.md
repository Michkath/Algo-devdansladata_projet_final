# TourismeData — Plateforme d'analyse des hébergements touristiques

> Projet final — M1 Data Engineer · Ynov · Cours Dev & Algo
> Groupe de 5 · Données ouvertes issues de [data.gouv.fr](https://www.data.gouv.fr)

---

## L'idée du projet

Ce projet simule la construction d'une plateforme de type **Airbnb** alimentée uniquement par des données publiques françaises.
À partir des hébergements classés (hôtels, campings, résidences de tourisme, etc.), nous avons construit un pipeline complet :
collecte → nettoyage → stockage → API → visualisation.

---

## L'équipe

| Membre | Rôle |
|---|---|
| **Arike** | Collecte des données (scraping data.gouv.fr, ingestion MongoDB) |
| **Goundo** | Nettoyage & transformation ETL (cleaning, normalisation) |
| **Serkaan** | Tests & qualité (tests unitaires, tests d'intégration, SOLID) |
| **Abdoulaye Camara** | Interface web (mini-site Flask/Jinja2, recherche, affichage) |
| **Sajed** | Dashboard BI (Streamlit, Plotly), API REST (Flask), coordination |

---

## Architecture du projet

```
data.gouv.fr (CSV)
        │
        ▼
  [ Scraping Python ]
        │
        ▼
  MongoDB · collection raw          ← données brutes originales
        │
        ▼
  [ Nettoyage Pandas ]
        │
        ├──▶ MongoDB · collection clean
        │
        ├──▶ Data Lake  (data_lake/processed/*.json)
        │
        ▼
  PostgreSQL · tourisme_dw          ← Star Schema analytique
        │
        ▼
  API Flask  (localhost:5000)
        │
        ├──▶ Interface Web  (localhost:5000)
        └──▶ Dashboard BI   (localhost:8501)
```

---

## Structure des fichiers

```
├── app.py                  API Flask + serveur de l'interface web
├── main.py                 Orchestration du pipeline ETL complet
├── scrapping.py            Collecte et ingestion dans MongoDB (raw)
├── cleaning.py             Nettoyage et stockage MongoDB (clean) + Data Lake
├── dw_loader.py            Chargement MongoDB → PostgreSQL
├── db.py                   Connexion PostgreSQL centralisée
├── routes.py               Blueprint API (architecture en couches)
├── hebergement_service.py  Requêtes métier PostgreSQL
├── schema.sql              Schéma Star Schema PostgreSQL
├── requirements.txt        Dépendances Python
├── docker-compose.yml      MongoDB via Docker
├── dashboard/
│   └── app_bi.py           Dashboard BI Streamlit
├── templates/
│   └── index.html          Interface web
├── data_lake/
│   ├── hebergements_classes.csv        Données brutes (21 000+ lignes)
│   └── processed/hebergements_propres.json
└── tests/
    ├── test_api1.py
    ├── test_ingestion.py
    ├── test_integration.py
    └── test_transformer.py
```

---

## Prérequis — ce qu'il faut installer

> Même si vous n'êtes pas développeur, suivez ces étapes dans l'ordre.

### 1. Python 3.12 ou 3.13

Vérifiez votre version :
```bash
python --version
```
Si vous avez Python 3.14 ou pas de Python, téléchargez Python 3.12 sur [python.org](https://www.python.org/downloads/).

### 2. Docker Desktop

Téléchargez et installez [Docker Desktop](https://www.docker.com/products/docker-desktop/).
Il sert à lancer MongoDB sans installation manuelle.

### 3. PostgreSQL + pgAdmin 4

Téléchargez [PostgreSQL](https://www.postgresql.org/download/windows/) (inclut pgAdmin 4).
Lors de l'installation, notez bien le mot de passe que vous choisissez.

---

## Installation du projet — étape par étape

### Étape 1 — Cloner ou télécharger le projet

```bash
git clone <(https://github.com/Michkath/Algo-devdansladata_projet_final.git)>
cd Algo-devdansladata_projet_final
```

### Étape 2 — Créer l'environnement Python

```bash
py -3.13 -m venv venv
source venv/Scripts/activate      # Windows Git Bash
# ou : venv\Scripts\activate      # Windows PowerShell / CMD
```

### Étape 3 — Installer les dépendances

```bash
pip install -r requirements.txt
```

### Étape 4 — Préparer la base PostgreSQL

Ouvrez **pgAdmin 4**, connectez-vous à votre serveur, puis :

1. Clic droit sur **Databases** → **Create** → **Database** → nom : `tourisme_dw` → **Save**
2. Cliquez sur `tourisme_dw` → ouvrez le **Query Tool** (icône éclair)
3. Copiez-collez le contenu de [schema.sql](schema.sql) *(sans la ligne `CREATE DATABASE`)*
4. Appuyez sur **F5** pour exécuter

> Vous devez voir 4 tables apparaître : `localisation`, `type_hebergement`, `classement`, `hebergements`

Si votre PostgreSQL tourne sur le port `5432` (standard), le code est déjà configuré.
Si vous utilisez un autre port, modifiez la ligne `port=` dans [db.py](db.py) et [dw_loader.py](dw_loader.py).

---

## Lancement — dans l'ordre

> Ouvrez **3 terminaux** dans le dossier du projet, avec le venv activé dans chacun.

### Terminal 1 — Démarrer MongoDB

```bash
docker-compose up -d mongodb
```

### Terminal 2 — Lancer le pipeline ETL (une seule fois)

```bash
source venv/Scripts/activate
python main.py
```

Résultat attendu :
```
Ingestion réussie : 21278 lignes insérées.
Fichier sauvegardé avec succès dans : data_lake/processed/hebergements_propres.json
ETL Pipeline Success
```

Puis charger PostgreSQL :
```bash
python dw_loader.py
```

Résultat attendu :
```
Nombre de documents MongoDB : 21278
Données transférées vers PostgreSQL avec succès !
```

> Ces deux commandes ne sont à faire **qu'une seule fois**. Les données restent ensuite en base.

### Terminal 2 — Lancer l'API Flask

```bash
source venv/Scripts/activate
python app.py
```

L'API est accessible sur `http://localhost:5000`

### Terminal 3 — Lancer le Dashboard BI

```bash
source venv/Scripts/activate
cd dashboard
streamlit run app_bi.py
```

Le dashboard est accessible sur `http://localhost:8501`

---

## Endpoints de l'API

| Méthode | URL | Description |
|---|---|---|
| GET | `/ping` | Vérification que l'API tourne |
| GET | `/hebergements` | Liste paginée avec filtres |
| GET | `/hebergements/<id>` | Détail d'un hébergement |
| GET | `/hebergements/export` | Tous les hébergements d'un coup (pour le dashboard) |
| GET | `/stats` | Statistiques agrégées |

**Paramètres de filtrage sur `/hebergements` :**

| Paramètre | Exemple | Description |
|---|---|---|
| `ville` | `?ville=Paris` | Filtrer par ville |
| `type` | `?type=hotel` | Filtrer par type |
| `classement` | `?classement=3` | Filtrer par classement |
| `page` | `?page=2` | Numéro de page |
| `per_page` | `?per_page=50` | Résultats par page (max 100) |
| `sort_by` | `?sort_by=ville` | Trier par champ |
| `sort_order` | `?sort_order=desc` | Ordre croissant/décroissant |

**Exemple :**
```
GET http://localhost:5000/hebergements?ville=Paris&type=hotel&page=1&per_page=20
```

---


## Dashboard BI — fonctionnalités

### Vue d'ensemble — tous les hébergements
<img width="1919" height="968" alt="Image" src="https://github.com/user-attachments/assets/8948dc2d-8ea9-49e1-8069-7eb82470f77c" />

### Filtre par type — Hôtels uniquement
<img width="1919" height="862" alt="Image" src="https://github.com/user-attachments/assets/38de4bac-141d-4738-ad27-932d8d573137" />

### Cartographie — densité des hôtels 5 étoiles par département
<img width="1912" height="856" alt="Image" src="https://github.com/user-attachments/assets/f7e2d869-a212-4571-9041-c79343ac2cd0" />

### Analyse croisée — capacité par type et par étoiles
<img width="1900" height="842" alt="Image" src="https://github.com/user-attachments/assets/1f68e9b7-4f15-4883-8564-3098c6777087" />

### Export CSV de la sélection
<img width="1919" height="1021" alt="Image" src="https://github.com/user-attachments/assets/ed201cbd-a149-4a24-a815-d3dec78f66a9" />


Le dashboard Streamlit propose 3 onglets :

- **Vue Globale** — KPIs (nombre d'établissements, capacité totale, moyenne étoiles, communes couvertes), répartition par type, top 10 des communes, export CSV
- **Cartographie** — carte choroplèthe de France par département (densité d'hébergements)
- **Analyse Croisée** — capacité moyenne par type, distribution de la capacité par nombre d'étoiles

Les filtres dans la barre latérale (type, commune, étoiles) s'appliquent à tous les onglets.

---

## Interface Web

<img width="1919" height="968" alt="Image" src="https://github.com/user-attachments/assets/74bd661c-8604-401d-a844-c16e4dbf565e" />

Accessible sur `http://localhost:5000`, l'interface permet :
- Recherche par ville, type, classement
- Affichage en grille avec pagination
- Vue détail d'un hébergement (modal)
- Export CSV de la sélection
- Documentation interactive des endpoints API
- Visualisation du schéma de base de données

---

## Schéma de la base de données (Star Schema)

```
         localisation
        ┌─────────────────┐
        │ id_localisation │◄──┐
        │ adresse         │   │
        │ code_postal     │   │
        │ commune         │   │
        └─────────────────┘   │
                              │
  type_hebergement            │     hebergements (table de faits)
 ┌──────────────────────┐     │    ┌────────────────────────┐
 │ id_type_hebergement  │◄────┼────│ id_hebergement         │
 │ typologie            │     │    │ nom_commercial         │
 │ categorie            │     ├────│ id_localisation        │
 │ type_sejour          │     │    │ id_type_hebergement    │
 │ mention              │     │    │ id_classement          │
 └──────────────────────┘     │    │ capacite_accueil       │
                              │    │ nombre_chambres        │
        classement            │    └────────────────────────┘
        ┌─────────────────┐   │
        │ id_classement   │◄──┘
        │ classement      │
        │ date_classement │
        │ classement_proroge│
        └─────────────────┘
```

---

## Lancer les tests

```bash
source venv/Scripts/activate
pytest tests/ -v
```

---

## Données

- **Source** : [data.gouv.fr — Hébergements touristiques classés](https://www.data.gouv.fr)
- **Volume** : 21 278 établissements
- **Types** : Hôtels, campings, résidences de tourisme, villages de vacances, chambres d'hôtes, meublés de tourisme
- **Couverture** : France entière
