USE gestion_energie;

DELETE FROM utilisation;
DELETE FROM appareil;
DELETE FROM periode;

SET IDENTITY_INSERT periode ON;
INSERT INTO periode (id, nom, heure_debut, heure_fin, rendement_panneau) VALUES(1, 'Matin', '06:00:00', '17:00:00', 40),(2, 'FA', '17:00:00', '19:00:00', 20),(3, 'Soirée', '19:00:00', '06:00:00', 0);
SET IDENTITY_INSERT periode OFF;

SET IDENTITY_INSERT appareil ON;
INSERT INTO appareil (id, nom, puissance_w) VALUES
(1, 'PC Portable', 65),
(2, 'Ampoule LED', 10),
(3, 'Télévision', 120),
(4, 'Ventilateur', 45),
(5, 'Routeur WiFi', 15),
(6, 'Réfrigérateur', 150);
SET IDENTITY_INSERT appareil OFF;

SET IDENTITY_INSERT utilisation ON;
INSERT INTO utilisation (id, appareil_id, periode_id, heure_debut, heure_fin, duree_heures) VALUES
(1, 1, 1, '08:00:00', '12:00:00', 4.0),
(2, 1, 2, '17:00:00', '18:00:00', 1.0),
(3, 1, 3, '19:00:00', '23:00:00', 4.0),
(4, 2, 1, '06:30:00', '09:30:00', 3.0),
(5, 2, 2, '17:30:00', '19:00:00', 1.5),
(6, 3, 1, '10:00:00', '16:00:00', 6.0),
(7, 3, 3, '20:00:00', '23:30:00', 3.5),
(8, 4, 1, '09:00:00', '11:00:00', 2.0),
(9, 4, 2, '17:15:00', '18:45:00', 1.5),
(10, 4, 3, '19:15:00', '22:15:00', 3.0),
(11, 5, 1, '06:00:00', '23:59:00', 17.98),
(12, 6, 3, '19:00:00', '06:00:00', 11.0);
SET IDENTITY_INSERT utilisation OFF;
