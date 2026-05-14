# Architecture — Supply Chain Security Scanner

## Schema textuel

```
+------------------+        +-------------------+        +--------------------+
|   CLI (Typer)    |        |  Frontend (React)  |        |   User / CI/CD     |
| scs-scanner scan |        | Dashboard Web      |        | GitHub Actions     |
+--------+---------+        +--------+----------+        +--------+-----------+
         |                           |                             |
         |  Python call              | HTTP REST                   | HTTP REST
         v                           v                             v
+--------+----------------------------------------------------------+----------+
|                           Backend FastAPI                                     |
|                                                                               |
|  /health   /version   /api/scans   /api/vulnerabilities                      |
|                                                                               |
|  +-------------------+  +------------------+  +---------------------------+  |
|  | Dependency Parser |  | Vuln Service     |  | Risk Scorer               |  |
|  | - requirements.txt|  | - vuln_db.json   |  | - CVSS weight             |  |
|  | - package.json    |  | - version match  |  | - scope multiplier        |  |
|  | - pom.xml         |  | - OSV connector  |  | - unpinned penalty        |  |
|  +-------------------+  +------------------+  +---------------------------+  |
|                                                                               |
|  +-------------------+  +------------------+                                 |
|  | Report Generator  |  | SBOM Builder     |                                 |
|  | - JSON / HTML / MD|  | - simplified SBOM|                                 |
|  +-------------------+  +------------------+                                 |
|                                                                               |
|  SQLite (ScanRecord) — stores scan results persistently                       |
+-------------------------------------------------------------------------------+
         |
         v
+--------+---------+
|  File system     |
|  sample-projects |
|  reports/        |
+------------------+
```

## Role du backend

Le backend est une API FastAPI qui expose les endpoints de scan, de consultation des resultats et de la base de vulnerabilites. Il orchestre les parsers, le service de vulnerabilites, le scoring et les reporters. Il stocke les resultats dans SQLite.

## Role du frontend

Interface React/TypeScript consommant l'API REST. Affiche le dashboard, la liste des scans, le detail de chaque scan et la base de vulnerabilites. Ne fait aucun traitement metier.

## Role de la CLI

La CLI Typer permet d'utiliser le scanner sans serveur. Elle importe directement les modules backend Python. Elle est utilisable dans une pipeline CI/CD via `--fail-on`.

## Flux d'un scan

1. L'utilisateur fournit un chemin vers un projet.
2. Les parsers detectent et parsent tous les fichiers de dependances supportes.
3. Le service de vulnerabilites compare chaque composant contre la base offline.
4. Le scoring calcule un score global et un niveau de risque.
5. Les remediations sont generees pour chaque vulnerabilite.
6. Le SBOM simplifie est construit.
7. Le rapport est genere (JSON, Markdown ou HTML).
8. Le resultat est stocke en base SQLite (via l'API) ou affiche en console (via la CLI).

## Stockage

SQLite est utilise pour la persistance legere, sans dependance externe. Chaque scan est stocke avec ses metadonnees et son resultat JSON complet. Le fichier de base est monte en volume Docker pour la persistance entre redemarrages.
