-- ============================
-- 1️. Création de la base
-- ============================
CREATE DATABASE tourisme_dw;

-- À exécuter séparément dans pgAdmin :
-- Puis se connecter à la base tourisme_dw avant la suite

-- ============================
-- 2️. Table : localisation
-- ============================
CREATE TABLE IF NOT EXISTS localisation (
    id_localisation SERIAL PRIMARY KEY,
    adresse TEXT,
    code_postal VARCHAR(10),
    commune VARCHAR(100)
);

-- ============================
-- 3️. Table : type_hebergement
-- ============================
CREATE TABLE IF NOT EXISTS type_hebergement (
    id_type_hebergement SERIAL PRIMARY KEY,
    typologie VARCHAR(100),
    categorie VARCHAR(100),
    type_sejour VARCHAR(100),
    mention VARCHAR(50)
);

-- ============================
-- 4️. Table : classement
-- ============================
CREATE TABLE IF NOT EXISTS classement (
    id_classement SERIAL PRIMARY KEY,
    classement VARCHAR(50),
    date_classement DATE,
    classement_proroge BOOLEAN
);

-- ============================
-- 5️. Table : hebergements (table principale)
-- ============================
CREATE TABLE IF NOT EXISTS hebergements (
    id_hebergement SERIAL PRIMARY KEY,
    
    nom_commercial TEXT,
    site_internet TEXT,

    id_localisation INT REFERENCES localisation(id_localisation),
    id_type_hebergement INT REFERENCES type_hebergement(id_type_hebergement),
    id_classement INT REFERENCES classement(id_classement),

    capacite_accueil INT,
    nombre_chambres INT,
    nombre_emplacements INT,
    nombre_unites INT,
    nombre_logements INT
);
-- ============================
-- 6️. Index pour performances
-- ============================
CREATE INDEX idx_commune ON localisation(commune);
CREATE INDEX idx_typologie ON type_hebergement(typologie);
CREATE INDEX idx_classement ON classement(classement);