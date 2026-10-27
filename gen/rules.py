"""Payment-date rules. Every rule and holiday is from an official source fetched 2026-10-28.
See SOURCES in content.py."""
import datetime as dt

D = dt.date
# OPM federal holiday schedule (opm.gov/policy-data-oversight/pay-leave/federal-holidays/),
# observed dates as listed by OPM (2026, 2027, and the 2028 New Year's Day observed on Fri Dec 31, 2027).
HOLIDAYS = {
    D(2026,1,1):"New Year's Day", D(2026,1,19):"Birthday of Martin Luther King, Jr.",
    D(2026,2,16):"Washington's Birthday", D(2026,5,25):"Memorial Day",
    D(2026,6,19):"Juneteenth National Independence Day", D(2026,7,3):"Independence Day (observed)",
    D(2026,9,7):"Labor Day", D(2026,10,12):"Columbus Day", D(2026,11,11):"Veterans Day",
    D(2026,11,26):"Thanksgiving Day", D(2026,12,25):"Christmas Day",
    D(2027,1,1):"New Year's Day", D(2027,1,18):"Birthday of Martin Luther King, Jr.",
    D(2027,2,15):"Washington's Birthday", D(2027,5,31):"Memorial Day",
    D(2027,6,18):"Juneteenth National Independence Day (observed)", D(2027,7,5):"Independence Day (observed)",
    D(2027,9,6):"Labor Day", D(2027,10,11):"Columbus Day", D(2027,11,11):"Veterans Day",
    D(2027,11,25):"Thanksgiving Day", D(2027,12,24):"Christmas Day (observed)",
    D(2027,12,31):"New Year's Day 2028 (observed)",
}

def nonbusiness(d):
    return d.weekday() >= 5 or d in HOLIDAYS

def why(d):
    if d.weekday() == 5: return "falls on a Saturday"
    if d.weekday() == 6: return "falls on a Sunday"
    if d in HOLIDAYS: return "is a federal holiday (%s)" % HOLIDAYS[d]
    return ""

def shift_back(d):
    """SSA (schedule PDF) and VA (VBA bulletin; 38 U.S.C. 5120(e)): if the due day is a weekend or
    federal holiday, pay on the preceding business day."""
    while nonbusiness(d):
        d -= dt.timedelta(days=1)
    return d

def nth_wed(y, m, n):
    d = D(y, m, 1)
    d += dt.timedelta(days=(2 - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n-1)

GROUPS = {
  # key: (label, short, who)
  "birthdays-1-10":  ("Social Security, birthdays 1st–10th", "2nd Wednesday", "Social Security (retirement, survivors, SSDI) recipients whose birthday falls on the 1st–10th of the month and who started benefits after April 1997"),
  "birthdays-11-20": ("Social Security, birthdays 11th–20th", "3rd Wednesday", "Social Security (retirement, survivors, SSDI) recipients whose birthday falls on the 11th–20th and who started benefits after April 1997"),
  "birthdays-21-31": ("Social Security, birthdays 21st–31st", "4th Wednesday", "Social Security (retirement, survivors, SSDI) recipients whose birthday falls on the 21st–31st and who started benefits after April 1997"),
  "paid-on-3rd":     ("Social Security paid on the 3rd", "the 3rd", "people who got Social Security before May 1997, or who get both Social Security and SSI"),
  "ssi":             ("SSI (Supplemental Security Income)", "the 1st", "SSI recipients"),
  "va":              ("VA disability compensation & pension", "1st business day", "VA disability compensation, pension, DIC and survivors pension recipients"),
}

def nominal(group, y, m):
    if group == "birthdays-1-10": return nth_wed(y, m, 2)
    if group == "birthdays-11-20": return nth_wed(y, m, 3)
    if group == "birthdays-21-31": return nth_wed(y, m, 4)
    if group == "paid-on-3rd": return D(y, m, 3)
    return D(y, m, 1)  # ssi, va

def add_month(y, m, k=1):
    t = y*12 + (m-1) + k
    return t//12, t%12 + 1

MONTHS = [(2026,11),(2026,12)] + [(2027,m) for m in range(1,13)]

def events():
    """All payments whose due date is Nov 2026 .. Jan 2028. Each: dict(group, due, paid, for_label).
    'due' month for SSA/SSI is the month the payment is due; for VA it is paid for the prior month."""
    out = []
    for g in GROUPS:
        for (y, m) in MONTHS + [(2028,1)]:
            due = nominal(g, y, m)
            paid = shift_back(due)
            if g == "va":
                py, pm = add_month(y, m, -1)
                forlab = "VA benefits for %s" % D(py, pm, 1).strftime("%B %Y")
            else:
                forlab = "%s payment" % due.strftime("%B %Y")
            out.append(dict(group=g, due=due, paid=paid, forlab=forlab, early=(paid != due), reason=why(due) if paid != due else ""))
    return out

# Dates as printed in SSA Publication 05-10031 (2026 and 2027 editions) for the months we cover.
SSA_PDF = {
 "ssi": ["2026-10-30","2026-12-01","2026-12-31","2027-02-01","2027-03-01","2027-04-01","2027-04-30","2027-06-01","2027-07-01","2027-07-30","2027-09-01","2027-10-01","2027-11-01","2027-12-01","2027-12-30"],
 "paid-on-3rd": ["2026-11-03","2026-12-03","2026-12-31","2027-02-03","2027-03-03","2027-04-02","2027-05-03","2027-06-03","2027-07-02","2027-08-03","2027-09-03","2027-10-01","2027-11-03","2027-12-03"],
 "birthdays-1-10": ["2026-11-10","2026-12-09","2027-01-13","2027-02-10","2027-03-10","2027-04-14","2027-05-12","2027-06-09","2027-07-14","2027-08-11","2027-09-08","2027-10-13","2027-11-10","2027-12-08"],
 "birthdays-11-20": ["2026-11-18","2026-12-16","2027-01-20","2027-02-17","2027-03-17","2027-04-21","2027-05-19","2027-06-16","2027-07-21","2027-08-18","2027-09-15","2027-10-20","2027-11-17","2027-12-15"],
 "birthdays-21-31": ["2026-11-25","2026-12-23","2027-01-27","2027-02-24","2027-03-24","2027-04-28","2027-05-26","2027-06-23","2027-07-28","2027-08-25","2027-09-22","2027-10-27","2027-11-24","2027-12-22"],
}

def check_against_pdf():
    ev = events()
    for g, lst in SSA_PDF.items():
        got = sorted(e["paid"].isoformat() for e in ev if e["group"] == g and e["due"] <= D(2028,1,31))
        # restrict computed to the PDF window: Oct 30 2026 .. Dec 31 2027
        got = [x for x in got if "2026-10-30" <= x <= "2027-12-31"]
        if g != "ssi" and g != "paid-on-3rd":
            pass
        assert got == lst, (g, got, lst)
    return True

if __name__ == "__main__":
    print(check_against_pdf())
    for e in events():
        if e["group"] == "va": print(e["paid"], e["forlab"], e["reason"])
