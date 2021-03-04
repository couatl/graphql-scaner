const fs = require('fs');
const path = require('path');

module.exports.allFilms = fs.readFileSync(path.join(__dirname, 'allFilms.gql'), 'utf8');
module.exports.film = fs.readFileSync(path.join(__dirname, 'film.gql'), 'utf8');
module.exports.allPeople = fs.readFileSync(path.join(__dirname, 'allPeople.gql'), 'utf8');
module.exports.person = fs.readFileSync(path.join(__dirname, 'person.gql'), 'utf8');
module.exports.allPlanets = fs.readFileSync(path.join(__dirname, 'allPlanets.gql'), 'utf8');
module.exports.planet = fs.readFileSync(path.join(__dirname, 'planet.gql'), 'utf8');
module.exports.allSpecies = fs.readFileSync(path.join(__dirname, 'allSpecies.gql'), 'utf8');
module.exports.species = fs.readFileSync(path.join(__dirname, 'species.gql'), 'utf8');
module.exports.allStarships = fs.readFileSync(path.join(__dirname, 'allStarships.gql'), 'utf8');
module.exports.starship = fs.readFileSync(path.join(__dirname, 'starship.gql'), 'utf8');
module.exports.allVehicles = fs.readFileSync(path.join(__dirname, 'allVehicles.gql'), 'utf8');
module.exports.vehicle = fs.readFileSync(path.join(__dirname, 'vehicle.gql'), 'utf8');
module.exports.node = fs.readFileSync(path.join(__dirname, 'node.gql'), 'utf8');
