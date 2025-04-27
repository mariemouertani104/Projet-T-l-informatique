def menu(): #des affichages du menu textuel
    print("Welcome to the calculator server!")
    print("Please select an operation:")
    print("1. Addition")
    print("2. Subtraction")
    print("3. Multiplication")
    print("4. Division")
    print("5. Exit")
    
    while True: 
        choice = input("Enter your choice (1-5): ") #choisissez une option de 1 à 5
        if choice in ['1', '2', '3', '4']:
            a = int(input("Please enter the first operand:")) #recevoir la premiére opérande dans la variable a
            b = int(input("Please enter the second operand:"))#recevoir la deuxiéme opérande dans la variable b
            if choice == '1':   #choix d'addition
                op = '+'
            elif choice == '2': #choix de soustraction
                op = '-'
            elif choice == '3': #choix de multiplication
                op = '*'
            elif choice == '4': #choix de division
                op = '/'
            break
        elif choice == '5':     #choix de sortir (quitter)
            print("Exiting the calculator server.")
            return "exit"
        else:                   #si le choix est invalide
            print("Invalid choice. Please try again.")
    return [op, str(a), str(b)] #retour de la forme [opération, premiére opérande, deuxiéme opérande]
    