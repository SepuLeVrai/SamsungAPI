# Guide de configuration Home Assistant

## Étape 1 — Vérifier le flux réseau

Depuis un terminal de Home Assistant, et non un navigateur d'un autre PC :

~~~sh
curl -sS --max-time 5 http://192.0.2.10:8001/api/v2/
curl -sS --max-time 5 http://192.0.2.11:8001/api/v2/
~~~

Dans chaque réponse JSON, vérifier **device.PowerState : on** lorsque la TV fonctionne, et **device.PowerState : standby** en veille.

La présence d'un appareil sur le réseau n'est jamais suffisante pour considérer son écran allumé.

## Étape 2A — Installation via Marketplace (HA 2026.11+)

Depuis Home Assistant 2026.11, **HACS est remplacé par Marketplace**, intégré nativement.

1. **Paramètres → Marketplace → Ajouter depuis un lien**.
2. Saisir **https://github.com/SepuLeVrai/SamsungAPI**.
3. Si demandé, sélectionner le type **Integration**, puis cliquer **Ajouter**.
4. Connecter GitHub par l'autorisation de l'appareil si nécessaire.
5. Ouvrir SamsungAPI et cliquer **Installer**.
6. Redémarrer HA si nécessaire, puis passer à l'étape 3.

Cette installation n'a pas encore été validée directement sur un vrai HA ; si le Marketplace refuse le dépôt, suivre la procédure manuelle ci-dessous.

## Étape 2B — Installation manuelle depuis GitHub



Télécharger le ZIP GitHub puis copier le répertoire **custom_components/samsung_tv_true_power** vers :

~~~text
/config/
  custom_components/
    samsung_tv_true_power/
      __init__.py
      manifest.json
      config_flow.py
      coordinator.py
      power_logic.py
      binary_sensor.py
      sensor.py
      const.py
      strings.json
      translations/
        fr.json
        en.json
~~~

Redémarrer complètement Home Assistant.

## Étape 3 — Ajouter la TV du pièce principale

Dans **Paramètres → Appareils et services → Ajouter une intégration → Samsung TV Local Power** :
- Adresse IPv4 : **192.0.2.10**
- Nom : **TV Pièce principale**

Valider. **Aucune notification d'autorisation Samsung n'est attendue**, car la lecture REST n'utilise pas la télécommande.

## Étape 4 — Ajouter la TV de la seconde pièce

Faire **Ajouter une intégration** une deuxième fois :
- Adresse IPv4 : **192.0.2.11**
- Nom : **TV Seconde pièce**

Les TV peuvent être configurées séparément, avec des réglages de filtrage distincts. Deux entrées avec la même IPv4 ne sont pas autorisées.

## Étape 5 — Identifier les nouveaux capteurs

Dans **Appareils et services → Samsung TV Local Power → TV Pièce principale → Entités**, relever :
- le **binary_sensor** nommé « Écran allumé » ;
- le **sensor** nommé « État alimentation API REST ».

Répéter pour la seconde pièce. Les identifiants d'entité sont générés par Home Assistant : **copier les identifiants réels**, plutôt que de les deviner.

## Étape 6 — Valider les états en situation réelle

Dans **Outils de développement → États** :
1. TV en veille : REST **standby** et binaire **off**.
2. Allumer la TV : REST **on** et binaire **on** après 15 secondes environ.
3. Éteindre la TV : REST **standby** et binaire **off** au prochain sondage.
4. Laisser la TV en veille au moins une heure : **aucun faux allumage** à cause de l'interface réseau.

Si l'API ne renvoie pas standby dans la situation attendue, ne pas modifier l'automatisation LED avant diagnostic.

## Étape 7 — Migrer l'automatisation LED

Ouvrir [l'exemple YAML](../examples/automatisation_bandeaux.yaml), puis remplacer :
- **binary_sensor.tv_piece_principale_ecran_allume** par le vrai ID du pièce principale ;
- **binary_sensor.tv_seconde pièce_ecran_allume** par le vrai ID de la seconde pièce.

Conserver les entités de lumière **light.tv_piece_principale** et **light.tv_seconde_piece**, déjà présentes dans l'automatisation initiale.

Enregistrer, déclencher des essais, puis désactiver l'ancienne automatisation utilisant les capteurs de ping.

## Étape 8 — Ajuster les délais

Dans **Configurer** sur chaque TV :
- ON continu : 15 s par défaut, pour ignorer les impulsions parasites ;
- Perte réseau : OFF *supposé* après 30 s, ajustable ;
- Sondage API : toutes les 5 s, ajustable.

La modification des options redémarre l'entrée d'intégration.

## Mise à jour manuelle

Remplacer les fichiers du répertoire custom_components/samsung_tv_true_power avec ceux du dernier commit de GitHub, puis redémarrer Home Assistant. **Ne pas supprimer** les entrées TV configurées.
