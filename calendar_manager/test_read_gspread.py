from calendar_manager.read_gspread import get_month_number, get_year, open_calendar_worksheet, find_cell, get_table

def test_get_month_number():
    assert get_month_number('Foo') == 0
    assert get_month_number('June') == 6
    assert get_month_number('January') == 1

def test_get_year():
    assert get_year('2001-2002', 'July') == '2001'
    assert get_year('2001-2002', 'September') == '2001'
    assert get_year('2001-2002', 'December') == '2001'
    assert get_year('2001-2002', 'January') == '2002'
    assert get_year('2001-2002', 'June') == '2002'

def test_find_cell():
    sheet = open_calendar_worksheet('Calendario de custodia compartida Elena', '2019-2020')
    all_cells = sheet.get_all_values()
    assert find_cell(all_cells, 'March') == (37, 18)

def test_get_table():
    sheet = open_calendar_worksheet('Calendario de custodia compartida Elena', '2019-2020')
    all_cells = sheet.get_all_values()
    assert get_table(all_cells, 'March', 3, 2) == [['March','L','M'],['9',' ',' ']]
    assert get_table(all_cells, 'January', 8, 1) == [['January','L','M','C','J','V','S','D']]
    assert get_table(all_cells, 'December', 2, 4) == [['December','L'],['48',' '],['',' '],['49','2']]