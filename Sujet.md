# Input
Appareil        Temps           Fotoana            puissance            Total(temps * puissance)
PC              2h(9h - 11h)              AM                 50W                  100W

# Fotoana 
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