# ======================================================================================================================
# Gridworld actions
# ======================================================================================================================
GW_ACT_N = "N"
GW_ACT_E = "E"
GW_ACT_S = "S"
GW_ACT_W = "W"
GW_ACT_NE = "NE"
GW_ACT_NW = "NW"
GW_ACT_SE = "SE"
GW_ACT_SW = "SW"
GW_ACT_STAY = "STAY"


def move(cell, act, steps=1):
    row, col = cell

    if act == GW_ACT_N:
        return row + steps, col

    elif act == GW_ACT_E:
        return row, col + steps

    elif act == GW_ACT_S:
        return move(cell, GW_ACT_N, -steps)

    elif act == GW_ACT_W:
        return move(cell, GW_ACT_E, -steps)

    elif act == GW_ACT_NE:
        ncell = move(cell, GW_ACT_N, steps)
        return move(ncell, GW_ACT_E, steps)

    elif act == GW_ACT_NW:
        ncell = move(cell, GW_ACT_N, steps)
        return move(ncell, GW_ACT_W, steps)

    elif act == GW_ACT_SE:
        ncell = move(cell, GW_ACT_S, steps)
        return move(ncell, GW_ACT_E, steps)

    elif act == GW_ACT_SW:
        ncell = move(cell, GW_ACT_S, steps)
        return move(ncell, GW_ACT_W, steps)

    elif act == GW_ACT_STAY:
        return cell


def bouncy_obstacle(cell, next_cells, obs):
    """
    cell: (row, col)
    next_cells: [(row, col)]
    obs: [(row, col)]
    """
    return list({ncell if ncell not in obs else cell for ncell in next_cells})


def bouncy_wall(cell, next_cells, dim):
    """
    cell: (row, col)
    next_cells: [(row, col)]
    dim: (num_rows, num_cols)
    """
    return list({
        (nrow, ncol) if ((0 <= nrow < dim[0]) and (0 <= ncol < dim[1])) else cell
        for nrow, ncol in next_cells
    })

