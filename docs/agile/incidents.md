# Journal des incidents - Sprint 1

## 2026-05-05 - Auth GitHub sur WSL Ubuntu (ME)
**Severite** : Bloquante temporaire
**Probleme** : ME ne pouvait pas push depuis WSL avec son mot de passe GitHub.
**Cause** : GitHub a supprime l'auth par mot de passe en 2021.
**Resolution** : Generation d'un Personal Access Token (PAT) avec scope repo.
**Action future** : Documenter dans CONTRIBUTING.md la procedure pour WSL/Linux users.

## 2026-05-05 - PowerShell BOM dans fichiers config (HK)
**Severite** : Mineure
**Probleme** : nginx refusait de demarrer (unknown directive "server").
**Cause** : PowerShell Set-Content -Encoding utf8 ajoute un BOM par defaut.
**Resolution** : Utiliser [System.IO.File]::WriteAllText avec UTF8Encoding(false).
**Action future** : Editer les fichiers config directement dans VS Code.

## 2026-05-05 - COPY conditionnel dans Dockerfile (HK)
**Severite** : Mineure
**Probleme** : docker build echouait sur COPY nginx.conf* avec syntax Bash.
**Cause** : Confusion entre syntaxe Bash (2>/dev/null) et instructions Docker.
**Resolution** : COPY direct sans redirection shell.
**Lecon** : Les instructions Docker COPY/ADD n'executent pas de shell.