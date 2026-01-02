import re

def create_table(table_name: str, columns: list, mapper: dict = None) -> str:
    sql_types = []
    for row in columns:
        dict_row = {c: data for c, data in zip(['name', 'type_code', 'data_length', 'internal_size', 'data_precision', 'data_scale', 'null_ok'], row)}
        if mapper:
            dict_row['new_data_type'] = mapper[int(dict_row['type_code'])](dict_row)
        sql_types.extend([dict_row])
    # Query para la creacion de la tabla en sql server
    query = f"CREATE TABLE {table_name} ("
    for i in sql_types:
        if mapper:
            query += f"{i['name']} {i['new_data_type']},"
        else:
            query += f"{i['name']} {i['type_code']},"
    query = query[:-1]
    query += ")"
    
    return query