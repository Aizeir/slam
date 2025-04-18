import numpy as np
import matplotlib.pyplot as plt



distances = np.random.uniform(50, 100, 100)
angles = np.random.uniform(0, 2*np.pi, 100)
player = (0,0)

# Extraire les coordonnées x et y des points
x_points = player[0] + distances * np.cos(angles)
y_points = player[1] + distances * np.sin(angles)

# Visualisation du nuage de points
plt.scatter(x_points, y_points, c='blue', label='Points', marker='.')
plt.scatter(*player, c='red', label='Rond', marker='o')

# Ajouter des labels et un titre
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Visualisation d\'un Nuage de Points')

# Afficher la légende
plt.legend()

# Afficher le graphique
plt.show()
