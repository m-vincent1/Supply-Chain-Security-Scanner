# Supply Chain Security Scanner

[![CI](https://github.com/USERNAME/supply-chain-security-scanner/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/supply-chain-security-scanner/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Outil de cybersecurite pour analyser la chaine d'approvisionnement logicielle d'un projet applicatif. Il parcourt les fichiers de dependances, detecte les composants vulnerables, calcule un score de risque global et genere des rapports utilisables dans un contexte DevSecOps.

---

## Probleme traite

Les dependances open source representent plus de 80 % du code d'une application moderne. Une seule dependance vulneree suffit a compromettre toute la chaine. Les equipes DevSecOps ont besoin d'un outil capable d'analyser rapidement l'inventaire logiciel d'un projet, de detecter les risques connus et de produire des rapports actionables.

---

## Fonctionnalites

- Analyse des dependances Python (`requirements.txt`, `pyproject.toml`), Node.js (`package.json`) et Maven (`pom.xml`)
- Generation d'un inventaire SBOM simplifie en JSON
- Detection des vulnerabilites via une base offline de demonstration (25 entrees couvrant Python, npm, Maven)
- Score de risque global et par dependance (0-100, formule documentee)
- Recommandations de remediation avec commande indicative
- Rapports en JSON, Markdown et HTML
- CLI professionnelle (`scs-scanner`) avec support `--fail-on` pour l'integration CI/CD
- API backend FastAPI avec persistance SQLite
- Dashboard React/TypeScript avec graphiques

---

## Architecture

```
scs-scanner (CLI)         React Dashboard
      |                         |
      v                         v
  FastAPI Backend  <--- REST API
      |
      +-- Parsers (Python / Node / Maven)
      +-- Vulnerability Service (offline DB)
      +-- Risk Scorer
      +-- Report Generator (JSON / HTML / Markdown)
      +-- SQLite (resultats persistants)
```

---

## Installation rapide

### Prerequis

- Python 3.11+
- Node.js 20+
- Docker et Docker Compose (optionnel)

### Via Docker Compose (recommande)

```bash
git clone https://github.com/USERNAME/supply-chain-security-scanner.git
cd supply-chain-security-scanner
make docker-up
```

Acces :

```
Frontend  : http://localhost:5173
Backend   : http://localhost:8000
API docs  : http://localhost:8000/docs
```

### Installation locale

```bash
# Backend
cd backend && pip install -e ".[dev]"

# CLI
cd cli && pip install -e ".[dev]"

# Frontend
cd frontend && npm install
```

---

## Utilisation CLI

```bash
# Scan de base (sortie terminal)
scs-scanner scan ./mon-projet

# Rapport Markdown
scs-scanner scan ./mon-projet --format markdown --output reports/rapport.md

# Rapport HTML
scs-scanner scan ./mon-projet --format html --output reports/rapport.html

# Gate CI/CD : echec si vulnerabilite haute ou critique detectee
scs-scanner scan . --fail-on high

# SBOM uniquement
scs-scanner sbom ./mon-projet --output sbom.json

# Verifier si le projet contient des fichiers de dependances supportes
scs-scanner validate ./mon-projet
```

---

## Utilisation Docker

```bash
# Lancer tous les services
make docker-up

# Arreter
make docker-down

# Lancer un scan via l'API (avec Docker actif)
curl -X POST http://localhost:8000/api/scans \
  -H "Content-Type: application/json" \
  -d '{"project_path": "/sample-projects/python-vulnerable"}'
```

---

## Scenario de demonstration

### Projet vulnere (Python)

```bash
scs-scanner scan sample-projects/python-vulnerable --format markdown --output reports/python-vulnerable.md --verbose
```

Resultat attendu :

```
Project: python-vulnerable
Dependencies analyzed: 9
Vulnerabilities found: 8
  Critical: 2
  High: 3
  Medium: 3
  Low: 0
Risk score: 85/100
Status: Critical
```

### Projet securise (Python)

```bash
scs-scanner scan sample-projects/python-secure --format markdown --output reports/python-secure.md
```

Resultat attendu :

```
Project: python-secure
Dependencies analyzed: 9
Vulnerabilities found: 0
Risk score: 0/100
Status: Low
```

---

## Exemple de rapport JSON

```json
{
  "scan_id": "abc123",
  "project_name": "python-vulnerable",
  "risk_score": { "total": 85.0, "level": "Critical" },
  "total_dependencies": 9,
  "total_vulnerabilities": 8,
  "vulnerabilities_by_severity": {
    "critical": 2, "high": 3, "medium": 3, "low": 0
  },
  "vulnerabilities": [
    {
      "vulnerability_id": "DEMO-CVE-2024-0002",
      "package": "django",
      "installed_version": "3.2.0",
      "severity": "critical",
      "cvss": 9.3,
      "recommendation": "Upgrade django to version 4.2.8 or later."
    }
  ]
}
```

---

## Scoring de risque

| Plage | Niveau   |
|-------|----------|
| 0-20  | Low      |
| 21-50 | Medium   |
| 51-75 | High     |
| 76-100| Critical |

Formule : `score = f(severite, CVSS, scope production/dev, repetition, dependances non pinees)`

Documentation complete : [docs/risk-scoring.md](docs/risk-scoring.md)

---

## Integration CI/CD

```yaml
# .github/workflows/security.yml
- name: Scan dependances
  run: scs-scanner scan . --fail-on high --format json --output reports/scan.json

- name: Upload rapport
  uses: actions/upload-artifact@v4
  with:
    name: security-report
    path: reports/scan.json
```

Documentation complete : [docs/devsecops-integration.md](docs/devsecops-integration.md)

---

## Structure du projet

```
supply-chain-security-scanner/
├── backend/              # API FastAPI + logique metier
│   ├── app/
│   │   ├── api/          # Routes REST
│   │   ├── core/         # Config, version matcher
│   │   ├── db/           # SQLite / SQLAlchemy
│   │   ├── models/       # Schemas Pydantic
│   │   ├── parsers/      # Parsers de dependances
│   │   ├── reporters/    # Generateurs JSON/HTML/MD
│   │   ├── scoring/      # Calcul du score de risque
│   │   └── services/     # Orchestration, detection vulns
│   ├── data/
│   │   └── vulnerability_db.json
│   └── tests/
├── cli/                  # CLI Typer (scs-scanner)
│   ├── scs_scanner/
│   └── tests/
├── frontend/             # Dashboard React/TypeScript
│   └── src/
├── sample-projects/      # Projets de demonstration
│   ├── python-vulnerable/
│   ├── python-secure/
│   ├── node-vulnerable/
│   ├── node-secure/
│   ├── java-vulnerable/
│   └── mixed-project/
├── docs/                 # Documentation technique
├── reports/              # Rapports generes
├── .github/workflows/    # CI GitHub Actions
├── docker-compose.yml
├── Makefile
└── SUIVI_PROJET.md
```

---

## Limites connues

- La base de vulnerabilites est une base de demonstration (25 entrees). Elle ne contient pas de donnees CVE reelles et ne doit pas etre utilisee pour des decisions de conformite en production.
- Les dependances transitives ne sont pas resolues. Seules les dependances directement declarees dans les fichiers de manifeste sont analysees.
- Le matching de versions pour npm et Maven utilise une heuristique simplifiee. La librairie `packaging` de Python est utilisee pour l'ecosysteme Python (semantique PEP 440 complete).
- L'analyse de licences n'est pas implementee dans cette version.

---

## Roadmap

- Integration OSV (osv.dev) complete avec mise a jour automatique de la base
- Support CycloneDX et SPDX conformes
- Analyse de licences (detection de licences incompatibles ou permissives)
- Detection de packages typosquattes
- Resolution des dependances transitives
- Integration GitLab CI native
- Authentification dashboard (JWT)
- Historique avance et comparaison entre deux scans
- Export PDF des rapports
- Support Dockerfile et images conteneur
- Support Pipfile et yarn.lock

---

## Avertissement

This tool is intended for defensive security, software supply chain risk analysis, DevSecOps workflows and educational purposes. It must only be used on projects you own or are authorized to assess.

---

## Licence

MIT — voir [LICENSE](LICENSE)
