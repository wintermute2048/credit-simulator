
# notary fees follow the law GNotKG
# For simplicity, we assume 1.5%
NOTARY_FEE_RATE = .015
LAND_REGISTRY_FEE_RATE = .005

# Property transfer tax by state from
# https://de.statista.com/statistik/daten/studie/202071/umfrage/aktueller-grunderwerbssteuersatz-in-deutschland-nach-bundeslaendern/
PROPERTY_TRANSFER_TAX = {
    "Baden-Württemberg": .05,
    "Bavaria": .035,
    "Berlin": .06,
    "Brandenburg": .065,
    "Bremen": .05,
    "Hamburg": .055,
    "Hesse": .06,
    "Lower Saxony": .05,
    "Mecklenburg-Vorpommern": .06,
    "North Rhine-Westphalia": .065,
    "Rhineland-Palatinate": .05,
    "Saarland": .065,
    "Saxony": .055,
    "Saxony-Anhalt": .05,
    "Schleswig-Holstein": .065,
    "Thuringia": .05,
}

STATES = list(PROPERTY_TRANSFER_TAX.keys())

# def process_side_fees()