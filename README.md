# UE-AD-A1-MIXTE

Ce TP met en place une architecture mixte composée de quatre micro-services.
Le service principal, Users, est en REST. Le service Movie est en GraphQL. Les services Booking et Showtime sont en gRPC.

## Auteurs
- Marc Blanchet
- Louis Bruneteau

## Installation

### Création d'un environnement virtuel
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Lancement des micro-services
```bash
chmod +x launch.sh
./launch.sh
```

Chaque micro-service peut également être lancé individuellement en utilisant la commande `python3 <nom_du_micro_service>.py` depuis son répertoire.

## Ports
- User: 3004
- Movie: 3001
- Booking: 3002
- Showtime: 3003

