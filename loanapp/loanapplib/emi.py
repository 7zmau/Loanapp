def calculate_emi(p, r, t): 
    r = r / (12 * 100) # one month interest
    t = t # one month period 
    emi = (p * r * pow(1 + r, t)) / (pow(1 + r, t) - 1) 
    return round(emi, 2)
