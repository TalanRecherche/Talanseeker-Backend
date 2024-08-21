# Talan Seeker

​

Talan est une API fastapi basée sur l'IA pour aider au staffing en facilitant la recherche de profils. Il est destiné aux personnes devant proposer des consultants pour répondre aux demandes des clients.​

 ​
A partir de CVs fournis dans un format bureautique, l'outil établit un profil structuré des consultants et permet de chercher une ou plusieurs personnes. Il présente une fiche profil du consultant qui affiche ses compétences et met en exergue celles correspondant à la demande. L'outil permet aussi de contacter les profils trouvés et leur référent.​


## Installation

Pour installer et configurer votre environnement local pour le développement avec Talan Seeker, suivez les étapes ci-dessous :

### Prérequis

Avant de commencer, assurez-vous d'avoir installé les outils suivants :
- Git : Téléchargez et installez Git depuis [git-scm.com](https://git-scm.com).
- Docker : Téléchargez et installez Docker depuis [Docker Hub](https://docker.com).
- DBeaver Community : Téléchargez et installez DBeaver depuis [DBeaver.io](https://dbeaver.io).

Docker servira à simuler les bases de données PostgreSQL et BLOB Azure (stockage des CVs)

### Récupération du code

Clonez le dépôt GitLab du projet Talan Seeker :

```bash
git clone https://gitlab.com/a.garcon.a/talanseeker-backend.git
cd talanseeker-backend
```

### Configuration de l'environnement avec Conda

Pour configurer votre environnement de développement en utilisant Conda, suivez les instructions ci-dessous. Assurez-vous d'avoir Anaconda ou Miniconda installé sur votre système. Si ce n'est pas le cas, vous pouvez le télécharger depuis [le site officiel d'Anaconda](https://www.anaconda.com/products/individual).

Ouvrez un terminal et créez un nouvel environnement Conda nommé `talanseeker` :

```bash
conda create --name talanseeker python=3.10
conda activate talanseeker
pip install -r requirements.txt
```

### Demander le fichier .env au centre de recherche

Le fichier .env est essentiel pour gérer de manière sécurisée les variables d'environnement, car il stocke des informations critiques telles que les clés API et les configurations de bases de données.

### Initialiser Docker pour la base de données

```bash
docker-compose up
```

### Utilisation de Docker pour la base de données

Merci de bien vouloi suivre les étapes contenues dans ce fichier : [### Utilisation de Docker pour la base de données](https://talan0.sharepoint.com/:w:/r/sites/GRP-CentredeRechercheetdInnovation-NeoStaffplus/Shared%20Documents/TalanSeeker/Dossier%20technique/readme_talanseeker_backend.docx?d=wce425e37b9504b259974d8b424772f06&csf=1&web=1&e=dXwidu)

## Utilisation

Cette section guide à travers les étapes pour démarrer l'API localement et interagir avec celle-ci, facilitant ainsi les tests et le développement avant une mise à jour sur l'application web Azure via un merge request sur la branch 'dev'.

### Démarrer l'API localement

1. **Assurez-vous que votre environnement est activé** :
   Activez votre environnement Conda où toutes les dépendances ont été installées.

   ```bash
   conda activate talanseeker
   ```


2. **Lancez l'API Talan Seeker** :
   À partir du répertoire racine du projet, exécutez la commande suivante pour démarrer le serveur local.

   ```bash
   sudo python main.py
   ```
   on execute avec sudo car on ne sait pas pourquoi mais ça ne marche pas sans.

3. **Consultez le SWAGGER pour intéragir avec l'API** :
   À partir du répertoire racine du projet, exécutez la commande suivante pour démarrer le serveur local.

   ```bash
   sudo python main.py
   ```
   on execute avec sudo car on ne sait pas pourquoi mais ça ne marche pas sans.


## Participants au projet

* **Antoine Garçon** - *développement du POC* 
* **Jordan Gonzales** - *développement du POC* 
* **Damien Jacob** - *développement du POC et du MVP* 
* **Marouane Fahli** - *développement du POC et du MVP* 
* **Rizk Ait Brik** - *développement du POC et du MVP* 
* **Youness Boumalek** - *développement du MVP* 
* **Steve Bellart** - *développement du MVP* 
* **Arnaud Deleruyelle** - *développement du MVP* 

