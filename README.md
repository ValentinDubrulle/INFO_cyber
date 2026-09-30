<div align="center">

# cyber-daily-digest

**Le digest quotidien de l'actualité cybersécurité, calibré pour 15 à 30 minutes de lecture.**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/LLM-Gemini-4285F4?style=flat-square&logo=googlegemini&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)
![Cost](https://img.shields.io/badge/Co%C3%BBt-0%20%E2%82%AC-2ea043?style=flat-square)
![License](https://img.shields.io/badge/Licence-MIT-lightgrey?style=flat-square)

</div>

---

## Présentation

Suivre la cybersécurité demande de parcourir des dizaines de sources chaque jour. Ce projet automatise cette veille : chaque matin, un pipeline collecte l'actualité, retire le bruit, puis produit une synthèse structurée livrée directement par email.

- **Zéro serveur** : tout tourne sur GitHub Actions.
- **Zéro coût** : palier gratuit de Gemini, cron GitHub, SMTP Gmail.
- **Lecture calibrée** : 3 000 à 6 000 mots, soit 15 à 30 minutes.
- **Sources vérifiables** : chaque item du digest renvoie vers l'article d'origine.

## Fonctionnement

```
  RSS + CISA KEV        Nettoyage           Synthèse            Livraison
 ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
 │   Collecte   │ -> │ Dédoublonnage│ -> │    Gemini    │ -> │    Email     │
 │  des sources │    │ Filtre 24 h  │    │ Tri + résumé │    │  SMTP Gmail  │
 └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

| Étape | Rôle |
|-------|------|
| Collecte | Lecture des flux RSS et du catalogue CISA KEV |
| Nettoyage | Suppression des doublons, filtre sur les dernières 24 h, mémoire des articles déjà vus |
| Synthèse | Regroupement par thème puis rédaction du digest par Gemini |
| Livraison | Envoi d'un email mis en forme, avec liens cliquables |

## Sources

| Source | Type |
|--------|------|
| CERT-FR | Alertes et avis officiels français |
| CISA | Avis de sécurité américains |
| CISA KEV | Vulnérabilités activement exploitées |
| BleepingComputer | Actualité et incidents |
| The Hacker News | Actualité et menaces |
| Krebs on Security | Enquêtes et analyses |

La liste complète est configurable dans `config/sources.yaml`.

## Contenu du digest

1. **À retenir** : les 3 informations majeures du jour
2. **Vulnérabilités** : failles critiques et exploitations actives (KEV)
3. **Menaces** : ransomware, campagnes d'attaque, groupes actifs
4. **Fuites et incidents** : compromissions de données
5. **Autres actualités** : réglementation, outils, recherche

## Stack technique

| Composant | Choix |
|-----------|-------|
| Langage | Python |
| Modèle | API Gemini (Google AI Studio, palier gratuit) |
| Planification | GitHub Actions (cron quotidien) |
| Livraison | SMTP Gmail avec mot de passe d'application |

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/ValentinDubrulle/cyber-daily-digest.git
cd cyber-daily-digest
```

### 2. Installer les dépendances

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurer les secrets

Les identifiants ne doivent jamais apparaître dans le code. Dans **Settings > Secrets and variables > Actions** du dépôt, ajouter :

| Secret | Description |
|--------|-------------|
| `GEMINI_API_KEY` | Clé API Google AI Studio |
| `GMAIL_ADDRESS` | Adresse Gmail expéditrice |
| `GMAIL_APP_PASSWORD` | Mot de passe d'application Gmail (validation en 2 étapes requise) |
| `RECIPIENT_EMAIL` | Adresse de réception du digest |

Pour un test en local, copier `.env.example` vers `.env` puis renseigner les mêmes variables. Le fichier `.env` est ignoré par Git.

### 4. Lancer

```bash
python -m digest.main
```

En production, le workflow `.github/workflows/daily.yml` exécute le pipeline chaque matin.

## Structure du projet

```
cyber-daily-digest/
├── .github/workflows/
│   └── daily.yml          # Daily scheduled run
├── config/
│   └── sources.yaml       # RSS feeds and settings
├── digest/
│   ├── collect.py         # Fetch RSS and CISA KEV
│   ├── clean.py           # Deduplicate and filter
│   ├── summarize.py       # Gemini summarization
│   ├── deliver.py         # Email sending
│   └── main.py            # Pipeline entry point
├── .env.example
├── requirements.txt
└── README.md
```

> La structure est indicative et sera ajustée au fil du développement.

## Feuille de route

- [ ] Collecte des flux RSS et du catalogue CISA KEV
- [ ] Dédoublonnage et mémoire des articles déjà vus
- [ ] Synthèse par thème avec Gemini
- [ ] Envoi de l'email et mise en forme HTML
- [ ] Workflow GitHub Actions quotidien
- [ ] Archivage des digests au format Markdown
- [ ] Notification Telegram courte avec les 3 points clés

## Limites connues

- Les quotas du palier gratuit de Gemini peuvent évoluer, il faut les vérifier régulièrement.
- Les emails peuvent arriver en spam lors des premiers envois.
- Le contenu est généré par un modèle de langage : se référer à la source originale pour toute décision de sécurité.
