# Dépannage de l'intégration SamsungAPI

## L'intégration Samsung officielle ne montre pas de notification sur l'écran

Cela ne concerne pas SamsungAPI. La lecture HTTP locale de **device.PowerState** ne passe **pas** par le WebSocket de télécommande et ne requiert pas cette autorisation. L'intégration officielle et SamsungAPI peuvent coexister.

## Le navigateur affiche le JSON, mais Home Assistant ne voit rien

Les deux appareils peuvent être dans des VLAN différents. Tester **depuis Home Assistant**. Autoriser les flux sortants de l'IP de HA vers les IP TV en **TCP 8001**, et le retour des connexions établies. Aucun accès large inter-VLAN ni SNAT n'est nécessaire si l'API HTTP fonctionne.

## Sens des valeurs du diagnostic

| Valeur | Interprétation |
| --- | --- |
| on | Tizen annonce un écran actif ; confirmation ON en cours ou acquise |
| standby | Tizen confirme la veille, le binaire doit être off |
| unreachable | Pas de réponse API ; après délai, le binaire passe à off **supposé**, pas confirmé |
| unsupported | Réponse HTTP sans PowerState exploitable ; binaire unavailable |

## Le bandeau reste allumé alors que la TV est en veille

Contrôler dans **Outils de développement → États** le binaire puis le diagnostic. Si le binaire est off mais le bandeau reste allumé : vérifier l'ID de l'entité dans le YAML, les traces d'automatisation et l'existence éventuelle d'une autre automatisation de bandeaux.

## Les LED s'éteignent alors que la TV est allumée

Contrôler la valeur **unreachable** ou **standby** dans les diagnostics. Si le réseau est perdu pendant 30 secondes, l'intégration force un **OFF supposé** pour économiser l'énergie. Ajuster le délai de perte dans **Configurer**, ou corriger le pare-feu / la connectivité.

## API sur ON pendant la veille

Si Tizen renvoie réellement **on** lorsque l'écran est éteint, la détection est limitée par la précision de l'API. Augmenter le délai de confirmation ON peut filtrer les réveils courts, mais une mesure électrique de la TV peut s'avérer nécessaire si cela persiste.

## Logs

Activer temporairement le journal détaillé dans configuration.yaml :

~~~yaml
logger:
  default: warning
  logs:
    custom_components.samsung_tv_true_power: debug
~~~

Redémarrer Home Assistant. Les données réseau sensibles et secrets éventuels ne doivent pas être publiés dans une issue GitHub publique.
