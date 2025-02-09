

def py_to_sql_list(py_list):
    if not py_list or  len(py_list) == 0:
        return "(NULL)"  # This is a special case for empty lists

    sql_list = "("
    for i in range(len(py_list)):
        sql_list += f"{py_list[i]}"
        if i != len(py_list) - 1:
            sql_list += ", "
    sql_list += ")"
    return sql_list