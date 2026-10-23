from datetime import date,timedelta
def test_date_logic():
    due=date.today()-timedelta(days=1)
    assert due < date.today()
    assert date.today() >= date.today()
