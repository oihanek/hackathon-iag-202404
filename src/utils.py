
def parse_extraction_service_result(result):

    docu_fields = result.documents[0].fields
    fields = [f"{k} {docu_fields[k].get('content','')}" for k in docu_fields if docu_fields[k].get('content', False)]
    pairs = []
    for kv_pair in result.key_value_pairs:
        try:
            pairs.append(f'{kv_pair.key.content}: {kv_pair.value.content}\n')
        except Exception as _:
            pass

    # Process tables
    tables = []
    for table_idx, table in enumerate(result.tables):
        table_txt = f'Table {table_idx} (in csv format):\n'
        current_row = 0
        for cell in table.cells:
            table_txt += f'{cell.content},'
            if cell.row_index != current_row:
                table_txt = table_txt[:-1] + '\n'
                current_row = cell.row_index
        table_txt += '\n'
        tables.append(table_txt)

    jump = "\n"

    return f"""
    {jump.join(fields)}
    {jump.join(pairs)}
    {jump.join(tables)}
    """

