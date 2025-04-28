def calcule(op,a,b):
    """
    Fonction qui effectue le calcul binaire entre deux entiers selon l'opérateur
    :param a: premier opérande
    :param b: second opérande
    :param op: opérateur
    :return: résultat du calcul
    """
    if op == "+":
        return a + b
    elif op == "-":
        return a - b
    elif op == "*":
        return a * b
    elif op == "/":
        if b != 0:
            return a / b
        else:
            return "Division par zéro impossible"   """---gestion des erruers possibles---"""
    else:
        raise ValueError("Opérateur invalide")     #---gestion des erruers possibles---
        
        