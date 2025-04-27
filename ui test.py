import tkinter as tk 
 
fenetre = tk.Tk() 
 
label_operation = tk.Label(fenetre, text="Opération :", font=("Arial", 12)) 
champ_operande1 = tk.Entry(fenetre, width=10) 
bouton_calculer = tk.Button(fenetre, text="Calculer", bg="lightgreen") 
label_resultat = tk.Label(fenetre, text="Résultat :", font=("Arial", 12, "bold")) 
 
label_operation.pack() 
champ_operande1.pack() 
bouton_calculer.pack() 
label_resultat.pack() 
 
fenetre.mainloop() 
 