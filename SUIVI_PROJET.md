# Suivi de projet — Supply Chain Security Scanner

## Objectif du projet

Creer un outil de cybersecurite open source permettant d'analyser la chaine d'approvisionnement logicielle d'un projet applicatif. L'outil analyse les dependances declarees dans les fichiers de manifeste Python, Node.js et Maven, detecte les composants vulnerables via une base de donnees offline, calcule un score de risque, genere des rapports et s'integre dans un pipeline CI/CD.

Le projet est concu pour etre valorisable dans un contexte professionnel DevSecOps, presentable a un recruteur en cybersecurite ou AppSec, et utilisable comme demonstration dans un entretien technique.

---

## Journal de construction

### Etape 1 — Initialisation du repository

**Ce qui a ete cree :**
- Structure de dossiers conforme a la specification
- `.gitignore` Python/Node/SQLite/IDE
- `LICENSE` MIT
- Dossier `reports/` avec `.gitkeep`

**Pourquoi ces choix :**
- Separation claire entre backend, CLI et frontend pour permettre un deploiement independant de chaque composant
- La CLI peut appeler le backend directement via import Python sans passer par HTTP, ce qui simplifie l'usage local

**Fichiers concernes :**
`.gitignore`, `LICENSE`, `reports/.gitkeep`

---

### Etape 2 — Architecture backend

**Ce qui a ete cree :**
- `backend/app/core/config.py` : configuration centralisee via Pydantic Settings avec support `.env`
- `backend/app/models/schemas.py` : tous les schemas de donnees Pydantic (Component, ScanResult, SBOM, etc.)
- `backend/app/db/database.py` : modele SQLAlchemy, creation de la base SQLite au demarrage
- `backend/app/main.py` : application FastAPI avec lifespan, CORS, routes health/version

**Decisions techniques :**
- SQLite choisi pour sa simplicite de deploiement (zero configuration, volume Docker)
- Pydantic v2 pour la validation des schemas et la serialisation JSON
- CORS permissif en dev pour simplifier l'integration frontend

**Fichiers concernes :**
`backend/app/core/config.py`, `backend/app/models/schemas.py`, `backend/app/db/database.py`, `backend/app/main.py`

---

### Etape 3 — Parsers de dependances

**Ce qui a ete cree :**
- `backend/app/parsers/base.py` : classe abstraite `BaseParser`
- `backend/app/parsers/python_parser.py` : `RequirementsTxtParser` (regex PEP 508) + `PyprojectTomlParser` (tomllib)
- `backend/app/parsers/node_parser.py` : `PackageJsonParser` (JSON natif, production/dev/peer)
- `backend/app/parsers/maven_parser.py` : `PomXmlParser` (xml.etree, resolution des proprietes `${version}`, scopes)
- `backend/app/parsers/__init__.py` : `detect_and_parse()` qui parcourt recursivement le projet

**Limites connues :**
- `requirements.txt` avec `-r` (inclusions recursives) n'est pas suivi
- Yarn.lock, Pipfile et build.gradle ne sont pas supportes dans cette version
- La resolution des proprietes Maven est limitee aux proprietes simples (`<properties>`)

**Tests associes :**
`backend/tests/test_parsers.py` — 5 tests couvrant Python/Node/Maven

---

### Etape 4 — Base de vulnerabilites offline

**Ce qui a ete cree :**
- `backend/data/vulnerability_db.json` : 25 entrees de demonstration couvrant Python (10), npm (7), Maven (8)

**Format des donnees :**
```json
{
  "id": "DEMO-CVE-2024-XXXX",
  "package": "nom-du-package",
  "ecosystem": "python|npm|maven",
  "affected_versions": "<X.Y.Z",
  "severity": "critical|high|medium|low",
  "cvss": 0.0,
  "summary": "...",
  "recommendation": "...",
  "references": [...]
}
```

**Pourquoi un mode offline existe :**
L'outil doit fonctionner dans des environnements sans acces Internet (pipelines CI internes, machines isolees, containers sans egress). La base offline garantit un comportement deterministe et reproductible. L'integration OSV est prevue en roadmap.

**Choix des entrees :**
Les vulnerabilites sont fictives mais realistes, inspirees de vulnerabilites connues (Log4Shell, Spring4Shell, Text4Shell, prototype pollution Node.js). Elles ne correspondent pas a des CVE reels pour eviter tout risque d'exploitation.

---

### Etape 5 — Moteur de matching des versions

**Ce qui a ete cree :**
- `backend/app/core/version_matcher.py`

**Approche choisie :**
- Ecosysteme Python : bibliotheque `packaging` (PEP 440 complet, operateurs `==`, `!=`, `<`, `<=`, `>`, `>=`, `~=`, plages `>=1.0,<2.0`)
- Ecosystemes npm et Maven : heuristique numerique interne (`_match_semver_simple`) supportant les memes operateurs de base

**Cas supportes :**
`==`, `!=`, `<`, `<=`, `>`, `>=`, `~=`, plages avec virgule, versions sans operateur (converties en `<X` pour Maven)

**Limites :**
- Semver complet (pre-releases, build metadata) non gere pour npm
- Ranges Maven complexes (`[1.0,2.0)`) partiellement supportes

**Tests associes :**
`backend/tests/test_version_matcher.py` — 18 cas parametres

---

### Etape 6 — Scoring de risque

**Ce qui a ete cree :**
- `backend/app/scoring/risk_scorer.py`

**Formule :**
```
raw = sum(base_weight(severity) * cvss/10 * scope_multiplier * repeat_factor)
raw += unpinned_production_deps * 1.5
score = min(100, raw / 200 * 100)
```

**Hypotheses :**
- Une dependance de production vulneree a un impact 2x superieur a une dependance de developpement
- Les packages avec plusieurs vulnerabilites voient leur score amplified de 10 % par vulnerabilite supplementaire
- Les dependances non pinees augmentent le risque meme en l'absence de vulnerabilite detectee

**Niveaux :**
Low (0-20), Medium (21-50), High (51-75), Critical (76-100)

**Documentation complete :** `docs/risk-scoring.md`

---

### Etape 7 — Generation de rapports

**Ce qui a ete cree :**
- `backend/app/reporters/json_reporter.py` : serialisation Pydantic native
- `backend/app/reporters/markdown_reporter.py` : tables Markdown, sections structurees
- `backend/app/reporters/html_reporter.py` : template Jinja2 inline, CSS embed, badges par severite

**Formats supportes :** JSON, Markdown, HTML

**Structure des rapports :**
Tous les formats incluent : resume executif, score, vulnérabilités par severite, liste detaillee des vulnerabilites, recommandations, SBOM simplifie, limites d'analyse, date du scan.

---

### Etape 8 — CLI

**Ce qui a ete cree :**
- `cli/scs_scanner/__init__.py` : version
- `cli/scs_scanner/commands.py` : logique des commandes (scan, sbom, validate)
- `cli/scs_scanner/main.py` : application Typer avec `scan`, `sbom`, `validate`, `version`
- `cli/pyproject.toml` : entrypoint `scs-scanner`

**Commandes disponibles :**
```bash
scs-scanner scan PATH [--format] [--output] [--fail-on] [--offline] [--include-dev] [--verbose]
scs-scanner sbom PATH [--output]
scs-scanner validate PATH
scs-scanner version
```

**Choix technique :**
La CLI importe directement les modules backend par ajout du chemin au `sys.path`. Cela evite un appel HTTP et permet d'utiliser la CLI sans serveur actif.

---

### Etape 9 — API FastAPI

**Ce qui a ete cree :**
- `backend/app/api/routes.py` : 7 endpoints REST
- `backend/app/services/scan_service.py` : orchestration du scan complet
- `backend/app/services/vulnerability_service.py` : chargement de la base, matching, remediations

**Endpoints :**
```
GET  /health
GET  /version
POST /api/scans
GET  /api/scans
GET  /api/scans/{scan_id}
GET  /api/scans/{scan_id}/sbom
GET  /api/scans/{scan_id}/report
GET  /api/vulnerabilities
```

**Choix techniques :**
- FastAPI + Pydantic v2 pour la validation automatique des entrees/sorties
- SQLAlchemy ORM pour la persistance SQLite
- Chaque scan stocke son resultat complet en JSON dans la colonne `result_json` pour un acces rapide sans rejoindre plusieurs tables

---

### Etape 10 — Frontend dashboard

**Ce qui a ete cree :**
- `frontend/src/App.tsx` : routeur React
- `frontend/src/components/Layout.tsx` + `Layout.css` : sidebar de navigation
- `frontend/src/components/SeverityBadge.tsx` : badge colore par severite
- `frontend/src/components/ScoreGauge.tsx` : indicateur visuel du score
- `frontend/src/pages/Dashboard.tsx` : page principale avec graphiques (BarChart, PieChart via Recharts)
- `frontend/src/pages/ScanList.tsx` : liste des scans
- `frontend/src/pages/ScanDetail.tsx` : detail complet d'un scan
- `frontend/src/pages/Vulnerabilities.tsx` : base de vulnerabilites avec filtres

**Composants principaux :**
React Router v6, Recharts pour les graphiques, axios pour les appels API, TypeScript strict.

---

### Etape 11 — Docker et CI/CD

**Ce qui a ete cree :**
- `backend/Dockerfile` : image Python 3.11-slim
- `frontend/Dockerfile` : build multi-stage Node + nginx
- `frontend/nginx.conf` : reverse proxy vers le backend
- `docker-compose.yml` : orchestration backend + frontend avec volume SQLite
- `Makefile` : raccourcis `install`, `test`, `lint`, `run-api`, `run-frontend`, `docker-up`, `docker-down`, `demo`
- `.github/workflows/ci.yml` : CI avec 4 jobs (backend-tests, cli-tests, frontend-build, demo-scan)

---

### Etape 12 — Tests et validation

**Ce qui a ete cree :**
- `backend/tests/test_parsers.py` : 5 tests (requirements.txt, package.json, pom.xml)
- `backend/tests/test_version_matcher.py` : 18 cas parametres
- `backend/tests/test_scoring.py` : 6 tests (scores, penalites, plafonnement)
- `backend/tests/test_scan_service.py` : 5 tests (scan complet, SBOM, projets exemples)
- `backend/tests/test_reporters.py` : 7 tests (JSON valide, Markdown, HTML)
- `backend/tests/test_api.py` : 8 tests (health, vulnerabilites, scans, erreurs)
- `cli/tests/test_cli.py` : 5 tests (version, scan, fail-on, projet securise)

**Commandes de validation :**
```bash
# Backend
cd backend && python -m pytest tests/ -v

# Ou via Makefile
make test
```

**Resultats attendus :**
Tous les tests passent. Les tests dependant des sample-projects sont conditionnes par `skipif` si les dossiers n'existent pas.

---

### Etape 13 — Documentation finale

**Ce qui a ete cree :**
- `README.md` : complet, professionnel, valorisable
- `docs/architecture.md` : schema textuel, roles, flux
- `docs/risk-scoring.md` : formule documentee, limites
- `docs/sbom-format.md` : format SBOM, comparaison CycloneDX/SPDX
- `docs/security-model.md` : perimetre defensif, menaces evitees
- `docs/devsecops-integration.md` : GitHub Actions, GitLab CI, bonnes pratiques
- `docs/api.md` : reference des endpoints
- `docs/cli.md` : reference des commandes

---

## Decisions techniques importantes

| Decision | Justification |
|----------|---------------|
| SQLite plutot que PostgreSQL | Zero configuration, portable, suffisant pour un usage mono-instance |
| Mode offline par defaut | Fonctionnement garanti sans reseau, deterministe en CI |
| CLI par import Python direct | Evite la dependance a un serveur HTTP actif pour l'usage local |
| Pydantic v2 | Performance, typage strict, serialisation JSON native |
| `packaging` pour Python versions | Semantique PEP 440 complete, fiable, standard |
| Template Jinja2 inline | Simplifie le packaging, pas de dependance aux fichiers statiques |

---

## Difficultes rencontrees et solutions

- **Namespace XML Maven** : les fichiers pom.xml peuvent contenir ou non le namespace `xmlns`. Solution : detection dynamique du namespace dans le tag racine.
- **Versions pinned npm** : les specifiers npm (`^1.0.0`, `~1.0.0`) ne correspondent pas a des versions exactes. Solution : extraction du numero de version de base pour le matching.
- **Versions avec suffixe Maven** : `4.1.94.Final` n'est pas parseable directement en tuple numerique. Solution : extraction du prefixe numerique par regex.

---

## Limites connues

- La base de vulnerabilites est une demonstration. Ne pas utiliser pour des decisions de conformite reelles.
- Les dependances transitives ne sont pas resolues.
- L'analyse de licences n'est pas implementee.
- Le support yarn.lock, Pipfile et build.gradle n'est pas implemente.
- Le matching Semver complet (pre-releases npm) n'est pas implemente.

---

## Ameliorations futures

Voir section Roadmap dans le README.
