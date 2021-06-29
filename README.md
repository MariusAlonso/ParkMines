# ParkMines

Projet pour l'UE 22.

simulation.py permet de simuler de manière séquentielle l'évolution du remplissage du parking, soumis à un stock de véhicules.
La classe Simulation prend en argument un parking, un stock, et un algorithme, qui se charge de donner les instructions aux robots.

Il y a essentiellement quatre types d'évènements :
- deposit : le client arrive pour déposer un véhicule
- retrieval : le client arrive pour récupérer son véhicule
- robot_arrival : le robot, vide, arrive à une extrémité de lane pour prendre un véhicule
- robot_end_task : le robot, transportant un véhicule, arrive à une extrémité de lane pour le déposer

---------

display.py permet de visualiser l'évolution de l'occupation du parking au cours de la simulation.
Pour lancer cet affichage, il suffit d'exécuter les méthodes .start_display() et .run() de l'objet simulation.

---------

performances.py affiche des statistiques sur une ou plusieurs simulations, en faisant varier éventuellement les paramètres de l'algorithme de décision.

---------

Pour entraîner un modèle de Reinforcement Learning, il suffit d'exécuter le fichier RL_main.py, après avoir chargé l'environnement conda à partir du fichier environement.yml

L'accès aux statistiques au cours de l'entraînement se fait à l'aide de tensorboard, en exécutant la commande
"tensorboard --logdir dossierchoisipourstockerlesstatistiques" dans un invite de commande séparé. Là aussi, il faut charger l'environnement conda.

---------

Une documentation synthétique des classes et méthodes est accessible en exécutant le fichier index.html du dossier build