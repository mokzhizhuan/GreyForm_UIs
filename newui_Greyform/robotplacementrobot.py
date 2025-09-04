def robotplacement(meshbounds):
    robotplacements = []
    robotplacements.append(
        {
            "Placement 1": [
                (meshbounds[0] + meshbounds[1]) / 4,
                (meshbounds[2] + meshbounds[3]) / 2,
                50,
            ],
            "Placement 2": [
                (meshbounds[0] + meshbounds[1]) / 4 * 3,
                (meshbounds[2] + meshbounds[3]) / 2,
                50,
            ]
        }
    )  # robot placement theory
    return robotplacements
