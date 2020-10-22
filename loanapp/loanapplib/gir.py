def get_interest_rate(tenure):
    if int(tenure) <= 5:
        return 10
    elif int(tenure) > 5 and int(tenure) <= 24:
        return 12
    else:
        return 15
