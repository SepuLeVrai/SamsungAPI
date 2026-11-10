# Releases et versioning

## Convention
Versions sémantiques `MAJOR.MINOR.PATCH`. Chaque version publiée est un tag `vMAJOR.MINOR.PATCH`, correspondant au champ `version` du `manifest.json`.

## Publier une version
1. Modifier `custom_components/samsung_tv_true_power/manifest.json` pour la nouvelle version.
2. Mettre à jour `CHANGELOG.md` et créer `releases/X.Y.Z.md` avec les notes publiques.
3. Vérifier que le code, les exemples et les notes ne contiennent aucune information spécifique à une installation personnelle.
4. Fusionner sur `main`. Le workflow **Publish release** s'exécute si le manifeste a changé.
5. Le workflow contrôle Python/JSON, tests et adresses privées, crée une archive ZIP, puis un tag et une GitHub Release.
6. Vérifier le résultat dans **Actions** puis **Releases**.

Le workflow peut aussi être lancé manuellement via **Actions → Publish release → Run workflow**. Il ne crée pas de doublon pour une version déjà publiée.

## Home Assistant
Les releases GitHub servent de référence pour les mises à jour de Home Assistant Marketplace / HACS. La propagation peut demander plusieurs heures. Pour une installation manuelle, télécharger le ZIP associé à la release.

Une réussite des tests automatisés ne constitue pas une validation fonctionnelle sur une vraie installation Home Assistant.
