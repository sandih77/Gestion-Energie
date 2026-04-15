CREATE DATABASE gestion_energie
USE gestion_energie;

CREATE TABLE appareil (id INT IDENTITY(1,1) PRIMARY KEY,nom VARCHAR(100) NOT NULL,puissance_w INT NOT NULL);

CREATE TABLE periode (id INT IDENTITY(1,1) PRIMARY KEY,nom VARCHAR(50),heure_debut TIME,heure_fin TIME,rendement_panneau FLOAT);

CREATE TABLE utilisation (id INT IDENTITY(1,1) PRIMARY KEY,appareil_id INT,periode_id INT,heure_debut TIME,heure_fin TIME,duree_heures FLOAT,FOREIGN KEY (appareil_id) REFERENCES appareil(id),FOREIGN KEY (periode_id) REFERENCES periode(id));