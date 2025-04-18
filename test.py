import numpy as np
import matplotlib.pyplot as plt

# Coordonnées initiales
x = np.random.rand(10)
y = np.random.rand(10)

# Initialisation de la figure et des points
fig, ax = plt.subplots()
scatter = ax.scatter(x, y)

# Mettre à jour les points après un certain temps
# Exemple : après 2 secondes, on met à jour les points
plt.pause(2)  # Attendre 2 secondes

# Nouvelle position des points
new_x = np.random.rand(10)
new_y = np.random.rand(10)

# Mise à jour des points avec les nouvelles coordonnées
scatter.set_offsets(np.c_[new_x, new_y])

# Afficher les points mis à jour
plt.draw()  # Redessine la figure avec les nouveaux points
plt.show()
