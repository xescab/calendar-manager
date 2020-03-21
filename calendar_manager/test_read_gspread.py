import pytest
from calendar_manager.read_gspread import get_month_number, get_year, open_calendar_worksheet, find_cell, get_table, read_month, get_event_templates, get_caregivers
from calendar_manager.events import EventTemplate

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
    with pytest.raises(ValueError):
        find_cell(all_cells, 'Foo')

def test_get_table():
    sheet = open_calendar_worksheet('Calendario de custodia compartida Elena', '2019-2020')
    all_cells = sheet.get_all_values()
    assert get_table(all_cells, 'March', 3, 2) == [['March','L','M'],['9',' ',' ']]
    assert get_table(all_cells, 'January', 8, 1) == [['January','L','M','C','J','V','S','D']]
    assert get_table(all_cells, 'December', 2, 4) == [['December','L'],['48',' '],['',' '],['49','2']]

def test_read_month():
    # 5 weeks are expected
    # 7 weekdays are expected
    all_cells = [
        ['March','Mo','Tu','We','Th','Fr','Sa','Su'],
        ['9','','','','','','','1'],
        [' ','','','','','','','M'],
        ['10','2','3','4','5','6','7','8'],
        [' ','D','D','M','D','D','D','D'],
        ['11','9','10','11','12','13','14','15'],
        [' ','M','M','D','M','M','M','M'],
        ['12','16','17','18','19','20','21','22'],
        ['Party uncle Tom','D','D','M','D','D','D','D'],
        ['13','23','24','25','26','27','28','29'],
        [' ','M','M','D','M','M','M','M']
    ]
    with pytest.raises(ValueError):
        read_month(all_cells, '2001-2002', 'April')
    assert type(read_month(all_cells, '2001-2002', 'March')) == dict
    assert read_month(all_cells, '2001-2002', 'March').get('month') == 3
    assert read_month(all_cells, '2001-2002', 'March').get('year') == 2002
    assert type(read_month(all_cells, '2001-2002', 'March').get('weeks')) == list
    assert read_month(all_cells, '2001-2002', 'March').get('weeks')[0].get('week_number') == '9'
    assert read_month(all_cells, '2001-2002', 'March').get('days').get('20') == 'D'
    assert read_month(all_cells, '2001-2002', 'March').get('days').get('24') == 'M'

def test_get_event_templates():
    all_cells = [
        ['Event templates','Summary','Description','Start','End','Apply to caregivers','Apply to weekdays'],
        ['schoolday_dad','Dad','Schoolday with Dad','','','D','0,1,2,3,4'],
        ['weekend_mum','Mum','Weekend with Mum','','','M','5,6'],
        ['piano','Piano lesson','Piano lesson at school (Tue,Thu)','17:00','18:00','D,M','1,3']
    ]
    assert type(get_event_templates(all_cells)) == list
    assert type(get_event_templates(all_cells)[0]) == EventTemplate
    assert get_event_templates(all_cells)[0].name == 'schoolday_dad'
    assert get_event_templates(all_cells)[2].summary == 'Piano lesson'

def test_get_caregivers():
    all_cells = [
        ['Caregivers','Name','Color'],
        ['D','Dad','3'],
        ['M','Mum','5']
    ]
    assert type(get_caregivers(all_cells)) == dict
    assert get_caregivers(all_cells).get('D').get('name') == 'Dad'
    assert get_caregivers(all_cells).get('M').get('color') == '5'