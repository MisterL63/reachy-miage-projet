const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

// -------------------------------------------------------------
// ROUTES PUBLIQUES (Ne nécessitent pas la carte étudiante)
// -------------------------------------------------------------

// Route pour récupérer tout le planning
app.get('/api/plannings', (req, res) => {
    const plannings = require('./data/plannings.json');
    res.json(plannings);
});

// Route pour savoir si un professeur spécifique est en cours
// Exemple d'URL : http://localhost:3000/api/plannings/professeur/Dupont
app.get('/api/plannings/professeur/:nom_prof', (req, res) => {
    const plannings = require('./data/plannings.json');
    const nomProf = req.params.nom_prof.toLowerCase();
    
    const coursDuProf = plannings.find(cours => cours.professeur.toLowerCase().includes(nomProf));
    
    if (coursDuProf) {
        res.json({
            trouve: true,
            message: `${coursDuProf.professeur} donne actuellement un cours de ${coursDuProf.matiere} en ${coursDuProf.salle}.`
        });
    } else {
        res.json({
            trouve: false,
            message: `Je ne trouve pas de cours prévu pour le professeur ${req.params.nom_prof} en ce moment.`
        });
    }
});

// -------------------------------------------------------------
// ROUTES PRIVÉES (Nécessitent le scan de la carte étudiante)
// -------------------------------------------------------------

//(EXEMPLE) Route sécurisée pour récupérer le dossier d'un étudiant via l'ID de sa carte
// Le robot Python enverra une requête POST avec l'ID lu par la caméra
app.post('/api/etudiants/dossier', (req, res) => {
    const idCarteScanne = req.body.id_carte; // L'ID envoyé par le robot
    
    if (!idCarteScanne) {
        return res.status(400).json({ erreur: "L'identifiant de la carte est manquant." });
    }

    const etudiants = require('./data/etudiants.json');
    const etudiantTrouve = etudiants.find(etu => etu.id_carte === idCarteScanne);

    if (etudiantTrouve) {
        // On renvoie les données privées
        res.json({
            authentification: "Succès",
            donnees: etudiantTrouve
        });
    } else {
        res.status(404).json({
            authentification: "Échec",
            erreur: "Aucun dossier trouvé pour cette carte."
        });
    }
});

// Lancement du serveur
app.listen(PORT, () => {
    console.log(`Serveur Reachy Middleware démarré sur http://localhost:${PORT}`);
    console.log(`Testez la route publique : http://localhost:${PORT}/api/plannings`);
});