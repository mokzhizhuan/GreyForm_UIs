def robotplacement(count_plus_y, count_minus_y, meshbounds):
    robotplacements = []
    if count_plus_y == 2:
        robotplacements.append(
            {
                "Wall 1": [
                    (meshbounds[0] + meshbounds[1]) / 4 * 3,
                    (meshbounds[2] + meshbounds[3]) / 2,
                    50,
                ],
                "Wall 2": [
                    (meshbounds[0] + meshbounds[1]) / 4,
                    (meshbounds[2] + meshbounds[3]) / 2,
                    50,
                ],
                "Wall 3": [
                    (meshbounds[0] + meshbounds[1]) / 4,
                    (meshbounds[2] + meshbounds[3]) / 2,
                    50,
                ],
                "Wall 4": [
                    (meshbounds[0] + meshbounds[1]) / 2,
                    (meshbounds[2] + meshbounds[3]) / 2,
                    50,
                ],
                "Wall 5": [
                    (meshbounds[0] + meshbounds[1]) / 8 * 7,
                    (meshbounds[2] + meshbounds[3]) / 4,
                    50,
                ],
                "Wall 6": [
                    (meshbounds[0] + meshbounds[1]) / 8 * 6,
                    (meshbounds[2] + meshbounds[3]) / 4,
                    50,
                ],
                "Floor": [
                    (meshbounds[0] + meshbounds[1]) / 4,
                    (meshbounds[2] + meshbounds[3]) / 2,
                    50,
                ],
                "Floor": [
                    (meshbounds[0] + meshbounds[1]) / 4 * 3,
                    (meshbounds[2] + meshbounds[3]) / 2,
                    50,
                ],
            }
        )  # robot placement theory
    else:
        robotplacements.append(
            {
                "Wall 1": [
                    (meshbounds[0] + meshbounds[1]) / 4 * 3,
                    (meshbounds[2] + meshbounds[3]) / 2,
                    50,
                ],
                "Wall 2": [
                    (meshbounds[0] + meshbounds[1]) / 4 * 3,
                    (meshbounds[2] + meshbounds[3]) / 4,
                    50,
                ],
                "Wall 3": [
                    (meshbounds[0] + meshbounds[1]) / 4 * 3,
                    (meshbounds[2] + meshbounds[3]) / 8 * 3,
                    50,
                ],
                "Wall 4": [
                    (meshbounds[0] + meshbounds[1]) / 2,
                    (meshbounds[2] + meshbounds[3]) / 2,
                    50,
                ],
                "Wall 5": [
                    (meshbounds[0] + meshbounds[1]) / 8 * 6,
                    (meshbounds[2] + meshbounds[3]) / 4 * 3,
                    50,
                ],
                "Wall 6": [
                    (meshbounds[0] + meshbounds[1]) / 8 * 6,
                    (meshbounds[2] + meshbounds[3]) / 4 * 3,
                    50,
                ],
                "Floor": [
                    (meshbounds[0] + meshbounds[1]) / 4,
                    (meshbounds[2] + meshbounds[3]) / 2,
                    50,
                ],
                "Floor": [
                    (meshbounds[0] + meshbounds[1]) / 4 * 3,
                    (meshbounds[2] + meshbounds[3]) / 2,
                    50,
                ],
            }
        )  # robot placement theory
    return robotplacements
