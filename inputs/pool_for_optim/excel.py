import xlrd
 
from xlwt import Workbook, Formula
 
# On créer un "classeur"
classeur = Workbook()
# On ajoute une feuille au classeur
feuille = classeur.add_sheet("feuille 1")

# Ecrire "1" dans la cellule à la ligne 0 et la colonne 0
feuille.write(0, 0, 1)
# Ecrire "2" dans la cellule à la ligne 0 et la colonne 1
feuille.write(0, 1, 2)
 
# Ecriture du classeur sur le disque
classeur.save(r"C:\Users\laure\Desktop\git\ParkMines\inputs\pool_for_optim\stock.xls")