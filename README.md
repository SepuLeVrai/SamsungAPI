# Samsung TV Local Power

Intégration **Home Assistant personnalisée et locale**, destinée à distinguer l'écran **réellement allumé** d'un téléviseur Samsung Tizen de son **interface réseau active en veille**.

> **Usage principal :** supprimer les allumages parasites des bandeaux LED lorsque les TV Samsung se réveillent brièvement sur Ethernet. Cette intégration ne remplace pas les fonctions de télécommande de l'intégration Samsung officielle.

**Version 0.2.0 — prototype à valider sur une installation réelle de Home Assistant.**

## Comment ça fonctionne

L'intégration interroge **GET http://IP_TV:8001/api/v2/** et lit le champ JSON **device.PowerState** :

| Réponse REST | Interprétation | Capteur binaire « Écran allumé » |
| --- | --- | --- |
| on | Samsung déclare l'écran actif | ON après 15 secondes continues, par défaut |
| standby / off / poweroff | Samsung déclare la veille ou l'arrêt | OFF au prochain sondage |
| unreachable | Aucune réponse HTTP exploitable | Conserve le dernier état 30 s, puis OFF **supposé** |
| unsupported | API répond sans PowerState valide | Indisponible, jamais ON par simple présence réseau |

Une perte prolongée du réseau provoque un **OFF présumé**, pour éviter de laisser les LED allumées inutilement. **Ce n'est pas une mesure certaine de la veille :** consulter le capteur de diagnostic (unreachable versus standby). Cette stratégie peut éteindre les LED si le réseau tombe pendant le visionnage.

Pas de SmartThings, pas de WebSocket, pas d'appairage ou de popup sur la TV. Lecture HTTP locale uniquement sur **TCP 8001**.

### Compatibilité

La compatibilité dépend du firmware. Vérifiez si votre TV expose une valeur exploitable dans device.PowerState via le port TCP 8001, à la fois en marche et en veille. Aucune liste de matériel privé ni de résultats d'installation spécifiques n'est publiée.

Les adresses 192.0.2.10 et 192.0.2.11 ci-dessous sont des adresses fictives réservées à la documentation (RFC 5737) ; remplacez-les par celles de vos appareils.

## Installation depuis GitHub

### A. Installation manuelle (recommandée pour la première validation)

1. Cliquer sur **Code → Download ZIP** dans ce dépôt.
2. Décompresser l'archive et localiser le répertoire **custom_components/samsung_tv_true_power**.
3. Copier ce dossier entier dans **/config/custom_components/** sur Home Assistant.
4. Vérifier que **/config/custom_components/samsung_tv_true_power/manifest.json** existe.
5. Redémarrer **Home Assistant** (le rechargement des automatisations seul ne suffit pas).
6. Aller dans **Paramètres → Appareils et services → Ajouter une intégration**.
7. Rechercher **Samsung TV Local Power** puis ajouter chaque TV séparément.

Si le répertoire custom_components n'existe pas encore, le créer sous /config. Il n'est pas nécessaire de modifier configuration.yaml.

### B. Installation depuis Marketplace (Home Assistant 2026.11 ou plus récent)

Depuis **Home Assistant 2026.11**, le Marketplace remplace HACS : inutile d'installer HACS séparément.

1. Aller dans **Paramètres → Marketplace**.
2. Cliquer sur **Ajouter depuis un lien** (Add from link).
3. Coller **https://github.com/SepuLeVrai/SamsungAPI**.
4. Cliquer **Ajouter**. Si nécessaire, choisir le type **Integration**, puis ajouter à nouveau.
5. Autoriser la connexion GitHub par code appareil si Home Assistant le demande (lecture des dépôts publics uniquement).
6. Ouvrir la fiche **SamsungAPI**, puis choisir **Installer**.
7. Redémarrer Home Assistant si demandé, puis **Paramètres → Appareils et services → Ajouter une intégration** pour configurer les deux TV.

Le dépôt possède le fichier **hacs.json** et la structure attendue. **La validation effective par le Marketplace sur ton instance reste à confirmer.** Si son installateur refuse le projet, utiliser la méthode manuelle ci-dessus.

Documentation officielle : https://www.home-assistant.io/integrations/marketplace/

### C. HACS (Home Assistant 2026.10 et antérieur seulement)

Sur une installation HA antérieure à 2026.11 disposant déjà de HACS : **HACS → menu ⋮ → Dépôts personnalisés**, ajouter **https://github.com/SepuLeVrai/SamsungAPI** en catégorie **Integration**, télécharger, puis redémarrer Home Assistant.

HACS ne doit plus être installé séparément sur les versions 2026.11 et ultérieures.

## Configuration de plusieurs téléviseurs

Ajoutez une entrée par TV depuis Appareils et services, avec une adresse IPv4 fixe et un nom au choix. Exemple fictif : 192.0.2.10 (TV Pièce principale) et 192.0.2.11 (TV Seconde pièce). Saisissez uniquement l'adresse IP sans protocole ni port.

Chaque entrée fournit un binary_sensor Écran allumé et un sensor de diagnostic État alimentation API REST. Relevez les identifiants réellement créés par Home Assistant ; les noms de l'exemple d'automatisation ne sont pas les vôtres.

### Réglages disponibles (bouton « Configurer »)

| Option | Valeur par défaut | Plage |
| --- | --- | --- |
| Confirmation ON continu | 15 secondes | 5–180 secondes |
| Délai sans réponse avant OFF présumé | 30 secondes | 5–300 secondes |
| Intervalle de sondage REST | 5 secondes | 3–60 secondes |

Un vrai allumage sera détecté en environ **15 à 20 s** avec les réglages par défaut. La veille déclarée par l'API est détectée au prochain sondage.

## pare-feu et VLAN TV

La connexion réseau indispensable est **Home Assistant → TV Samsung : TCP destination 8001**, plus les réponses des sessions établies. Utiliser idéalement une règle dédiée :
- Source : adresse de Home Assistant.
- Destination : les deux IP de télévision, **192.0.2.10 et 192.0.2.11**.
- Port : TCP **8001**.
- Aucun accès général du VLAN TV vers les autres VLAN.

Pour ce capteur local, **aucune découverte mDNS/SSDP, aucun SNAT et aucun port 8002** ne sont nécessaires lorsque le port 8001 fonctionne.

**Attention au test :** un navigateur sur un PC peut accéder à la TV alors que Home Assistant n'y accède pas. Tester depuis un terminal du réseau de HA :

~~~sh
curl -sS --max-time 5 http://192.0.2.10:8001/api/v2/
curl -sS --max-time 5 http://192.0.2.11:8001/api/v2/
~~~

Le JSON doit inclure **device.PowerState** à on ou standby, même si la TV reste visible au ping dans les deux états.

## Automatisation des bandeaux

Le fichier **[examples/automatisation_bandeaux.yaml](examples/automatisation_bandeaux.yaml)** contient une automatisation complète, compatible avec :
- le bandeau pièce principale : **light.tv_piece_principale** ;
- le bandeau seconde pièce : **light.tv_seconde_piece** ;
- la gestion du coucher et du lever de soleil.

Le YAML contient **des identifiants binary_sensor d'exemple**. Il faut obligatoirement les remplacer par les IDs créés dans votre Home Assistant, puis **désactiver l'ancienne automatisation basée sur le ping**, sinon elles peuvent se contredire.

**Procédure conseillée :** installer d'abord l'intégration, observer la veille et la marche sur les deux capteurs, adapter le YAML, et seulement ensuite retirer l'ancienne automatisation.

## Dépannage et limites

| Symptomatique | Action |
| --- | --- |
| API : unreachable | Tester TCP 8001 depuis HA ; vérifier pare-feu VLAN et IP |
| API : unsupported | JSON absent ou PowerState non reconnu ; examiner la réponse brute |
| Le capteur indique OFF juste après mise en marche | Normal pendant la confirmation ON ; attendre 15 s |
| LED s'éteint pendant une panne réseau | OFF présumé après 30 s ; ajuster ce délai via Configurer |
| La TV demande une autorisation de télécommande | Cela concerne l'intégration Samsung officielle, pas SamsungAPI |
| L'intégration n'apparaît pas après installation | Vérifier le chemin, manifest.json, le redémarrage HA et le cache navigateur |

**Limitations :** l'API peut changer suivant les modèles et firmwares. PowerState=on ne garantit pas une image diffusée (ex. Art Mode). Une API unreachable n'est pas une confirmation de veille. Les champs name/id du JSON sont parfois vides lorsque la TV est allumée : SamsungAPI identifie chaque TV par **son adresse IPv4 configurée**.

Documentation détaillée :
- [Configuration pas à pas](docs/CONFIGURATION.md)
- [Dépannage](docs/DEPANNAGE.md)
- [Changelog](CHANGELOG.md)
- [Signaler un problème](https://github.com/SepuLeVrai/SamsungAPI/issues)

## Vérifications techniques

~~~sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q custom_components
~~~

Un workflow GitHub Actions effectue également la compilation Python, la validation des JSON et les tests unitaires. **Ces tests ne remplacent pas une vérification sur ton instance Home Assistant.**

Licence : [MIT](LICENSE).
