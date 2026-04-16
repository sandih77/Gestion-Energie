# Input
Appareil        Temps           Période            puissance            Total(temps * puissance)
PC              2h(9h - 11h)              AM                 50W                  100W

# Période 
Matin : 6h -> 17h
FA : 17h -> 19h
Soirée : 19h -> 6h

# Output 
- Puissance panneau solaire et batterie necessaire

# Paramètre 
- Matin, puissance réelle panneau utiliser 40% de sa puissance
- FA, puissance panneau 50% du 40% (pas de soleil)
- Soirée, en utilise la batterie

# Technologie
- Base de donnée : sql server
- Python Tkinter

# Logique
- Calcul batterie
    - on utilise la batterie pendant la soirée(19h à 6h) 
    - puissance batt utile = puissance appareil * duree utilisation
    - il faut tenir compte des chevauchements de période gerne utilisation de télé commence à 18 à 22h donc 18h à 19h il est encore sous la charge du panneau, 19h à 22h charge de la batterie
    - En fait, tout ceci est le cas théorique mais en vrai il y le cas pratique (réelle) genre en vrai la batterie ne peut fournir que 50% de plus de sa puissance donc il faut ajouter 50%(variable) au cas théorique
- Calcul panneau solaire 
    - on utilise le panneau solaire pendant le matin et la fin d' après-midi (fa)
      - Pendant le matin il n' y a rien de special
      - Pendant la fin d' après-midi il ne fournit que 50% de sa puissance (ceci est une variable modifiable) donc si il a besoin de 100w pour allumer le télé pendant le matin il a besoin de 200w en vrai pour l' allumer pendant la fin d'après-midi 
    - La puissance du panneau utile est la puissance max des appareils
    - Si il y a deux appareils qui sont utilisés simultanément donc on fait la somme
    - donc il faut tenir compte de la réduction de puissance pendant la fin d'après-midi à cause de l absence du soleil
    - Dans cette calcul, il y a aussi de cas théorique et pratique, genre le panneau ne fourni que 40%(variable) donc il faut ajouter 40% au cas théorique. Cette logique concerne le matin et la fin d'après-midi
- Ajouter une nouvelle onglet dans l'interface pour afficher la puissance théorique et pratique du batterie et panneau solaire 

Ajoutons une convertisseur
Donc il faut trouver la puissance pic durant la journée(matin, fa, soirée)
donc la puissance de la convertisseur est la puissance pic * 2

dans le dimensionnement on va dire que tous ces réglages sont pour panneau p1
Ajoutons les meme réglages mais juste pour panneau P2

Donc le système propose 2 Résultats celle qui vient du réglage de P1 et P2

La convertisseur concerne les deux donc il faut afficher aussi la puissance du convertisseur