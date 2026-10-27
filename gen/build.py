import os, json, shutil, datetime as dt, html
from rules import events, GROUPS, MONTHS, HOLIDAYS, check_against_pdf, D

BASE = "https://j6-cloude.github.io/benefit-paydays"
OUT = os.path.join(os.path.dirname(__file__), "..", "docs")
CHECKED = "October 28, 2026"
esc = html.escape

SRC = {
 "ssa2026": ("SSA Publication 05-10031, Schedule of Social Security Benefit Payments 2026", "https://www.ssa.gov/pubs/EN-05-10031-2026.pdf", "2026 edition"),
 "ssa2027": ("SSA Publication 05-10031, Schedule of Social Security Benefit Payments 2027", "https://www.ssa.gov/pubs/EN-05-10031-2027.pdf", "edition dated January 2026"),
 "cola": ("SSA: Cost-of-Living Adjustment (COLA) Information for 2027", "https://www.ssa.gov/cola/", "page certified Oct 14, 2026"),
 "colafs": ("SSA: 2027 Social Security Changes fact sheet", "https://www.ssa.gov/news/en/cola/factsheets/2027.html", "page certified Oct 14, 2026"),
 "opm": ("OPM: Federal Holidays (2026, 2027, 2028 schedules)", "https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/", "OPM holiday schedule"),
 "vabull": ("VA (Veterans Benefits Administration) bulletin: VA Benefit Payment Schedule", "https://content.govdelivery.com/accounts/USVAVBA/bulletins/218218a", "sent Oct 30, 2018; payment rule only"),
 "usc5120": ("38 U.S.C. § 5120(e), payment of VA benefits when the 1st falls on a weekend or holiday", "https://www.law.cornell.edu/uscode/text/38/5120", "federal statute"),
 "snap-ca1": ("California CDSS: Frequently Asked Questions (CalFresh issuance)", "https://www.cdss.ca.gov/about-cdss/frequently-asked-questions", "CDSS FAQ"),
 "snap-ca2": ("California CalFresh (CDSS) program site", "https://calfresh.dss.ca.gov/food/immigrants/index.html", "CDSS CalFresh site"),
 "snap-tx": ("Texas HHS, Texas Works Handbook B-251 Monthly Benefit Issuance Schedule", "https://www.hhs.texas.gov/handbooks/texas-works-handbook/b-250-ebt-benefit-issuance", "Revision 23-4, effective Oct 1, 2023"),
 "snap-ct": ("Connecticut DSS: Using Your EBT Card", "https://portal.ct.gov/dss/knowledge-base/articles/snap/using-your-ebt-card", "schedule beginning March 1, 2026"),
 "snap-mi": ("Michigan DHHS, RFS 305 Bridges Transaction Deadlines and Issuance Schedules", "https://dhhs.michigan.gov/olmweb/ex/RF/Public/RFS/305.pdf", "RFB 2026-001, effective Jan 1, 2026"),
}

def cite(*keys):
    return "<p class=src>Source%s: %s. Checked %s.</p>" % ("s" if len(keys) > 1 else "", "; ".join(
        '<a href="%s" rel="noopener">%s</a> (%s)' % (SRC[k][1], esc(SRC[k][0]), esc(SRC[k][2])) for k in keys), CHECKED)

CSS = """*{box-sizing:border-box}body{margin:0;font:17px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#2b2622;background:#faf7f2}
a{color:#8a4b08}header,main,footer{max-width:820px;margin:0 auto;padding:0 16px}
header{display:flex;flex-wrap:wrap;align-items:center;gap:6px 16px;padding-top:12px}.brand{font-weight:700;font-size:20px;text-decoration:none;color:#2b2622}
.brand span{color:#b45309}nav{display:flex;flex-wrap:wrap;gap:4px 14px}nav a{font-size:15px;white-space:nowrap}
.notice{background:#fff3d6;border:2px dashed #b45309;border-radius:10px;padding:10px 12px;margin:12px 0;font-size:15px}
.notice b{color:#7c2d12}h1{font-size:28px;line-height:1.25;margin:18px 0 8px}h2{font-size:21px;margin:26px 0 8px}
table{border-collapse:collapse;width:100%;margin:10px 0;background:#fff;font-size:16px}th,td{border:1px solid #e4dccf;padding:7px 9px;text-align:left;vertical-align:top}th{background:#f1e9dc}
.card{background:#fff;border:1px solid #e4dccf;border-radius:12px;padding:16px;margin:14px 0}
.big{font-size:26px;font-weight:700;color:#7c2d12}.src{font-size:14px;color:#5c534a}.muted{color:#6b6157;font-size:15px}
label{display:block;margin:10px 0 4px;font-weight:600}input,select,button{font:inherit;padding:8px 10px;border:1px solid #c9bca8;border-radius:8px;background:#fff;max-width:100%}
button{background:#b45309;color:#fff;border:0;cursor:pointer;font-weight:600;margin-top:12px}.chk{font-weight:400}
.res{margin-top:14px}.res .item{border-top:1px solid #eee3d3;padding:8px 0}.pill{display:inline-block;background:#f1e9dc;border-radius:99px;padding:1px 9px;font-size:13px}
footer{margin-top:40px;padding-bottom:30px;font-size:14px;color:#5c534a;border-top:1px solid #e4dccf}
ul.months{columns:2;padding-left:18px}@media(max-width:600px){h1{font-size:23px}ul.months{columns:1}body{font-size:16px}}"""

NOTICE = ('<div class=notice role=note><b>Independent site, not affiliated with SSA, VA, USDA or any government agency.</b> '
          'Never share your SSN; we never ask for it. We collect no personal data: lookups run only in your browser. '
          'Always confirm with your official notice or agency.</div>')

PAGES = []  # (path, title)

def page(path, title, desc, body, crumbs=None, jsonld=None, extra_head=""):
    url = BASE + "/" + path
    ld = []
    if crumbs:
        ld.append({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":i+1,"name":n,"item":BASE+"/"+p} for i,(n,p) in enumerate(crumbs)]})
    if jsonld: ld.append(jsonld)
    ldh = "".join('<script type="application/ld+json">%s</script>' % json.dumps(x) for x in ld)
    bc = ""
    if crumbs:
        bc = '<p class=muted>' + " › ".join('<a href="%s/%s">%s</a>' % (BASE, p, esc(n)) for n, p in crumbs[:-1]) + " › " + esc(crumbs[-1][0]) + "</p>"
    doc = f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name=description content="{esc(desc)}"><link rel=canonical href="{url}">
<meta property=og:title content="{esc(title)}"><meta property=og:description content="{esc(desc)}"><meta property=og:url content="{url}"><meta property=og:type content=website>
<style>{CSS}</style>{ldh}{extra_head}</head><body>
<header><a class=brand href="{BASE}/">Benefit<span>Paydays</span></a><nav><a href="{BASE}/">Next payment</a><a href="{BASE}/social-security/">Social Security</a><a href="{BASE}/ssi/">SSI</a><a href="{BASE}/va-disability/">VA</a><a href="{BASE}/snap/">SNAP</a><a href="{BASE}/cola-2027/">2027 COLA</a></nav></header>
<main>{NOTICE}{bc}{body}</main>
<footer><p><b>Independent site, not affiliated with SSA, VA, USDA or any government agency.</b> Never share your SSN; we never ask for it. No ads, no tracking, no cookies.</p>
<p>Dates are computed from each agency's published rules and the OPM federal holiday calendar, and checked against SSA's published schedules. Bank posting times vary; paper checks may take up to three more mailing days (per SSA). Last checked {CHECKED}.</p>
<p><a href="{BASE}/sources/">Sources</a> · <a href="{BASE}/about/">About</a> · <a href="{BASE}/privacy/">Privacy</a> · <a href="{BASE}/calendar-feeds/">Calendar feeds</a> · <a href="{BASE}/months/">All months</a></p></footer>
</body></html>"""
    fp = os.path.join(OUT, path, "index.html") if (path == "" or path.endswith("/")) else os.path.join(OUT, path)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w").write(doc)
    PAGES.append(path)

def fmt(d): return d.strftime("%A, %B ") + str(d.day) + d.strftime(", %Y")
def fmts(d): return d.strftime("%a %b ") + str(d.day) + d.strftime(", %Y")
def mkey(y, m): return "%04d-%02d" % (y, m)
def mname(y, m): return D(y, m, 1).strftime("%B %Y")

EV = events()
def in_month(g, y, m): return [e for e in EV if e["group"] == g and (e["paid"].year, e["paid"].month) == (y, m)]
def due_month(g, y, m): return [e for e in EV if e["group"] == g and (e["due"].year, e["due"].month) == (y, m)]

SRCS_FOR = {"ssi":("ssa2026","ssa2027","opm"), "va":("vabull","usc5120","opm")}
def srcs(g): return SRCS_FOR.get(g, ("ssa2026","ssa2027","opm"))

VA_2027_12 = ("<p><b>Unconfirmed:</b> VA has not published a dated calendar. January 1, 2028 is a Saturday and OPM lists Friday, December 31, 2027 as the observed New Year's Day holiday. "
              "Under VA's 'last business day prior to the first' rule that gives <b>Thursday, December 30, 2027</b>; the statute (38 U.S.C. 5120(e)) speaks of 'the Friday immediately preceding' a Saturday, so it could arrive Friday, December 31. Check your bank or VA.gov.</p>")

def ev_line(e):
    s = "<b>%s</b> — %s" % (fmt(e["paid"]), esc(e["forlab"]))
    if e["early"]:
        s += " <span class=pill>paid early</span> (the regular day, %s, %s)" % (fmts(e["due"]), esc(e["reason"]))
    if (e["paid"].year, e["paid"].month) != (e["due"].year, e["due"].month) and e["group"] != "va":
        s += ". This is the payment for <b>%s</b>, not an extra payment." % e["due"].strftime("%B %Y")
    return s

def gpath(g, y, m):
    if g in ("birthdays-1-10","birthdays-11-20","birthdays-21-31","paid-on-3rd"): return "social-security/%s/%s/" % (mkey(y,m), g)
    if g == "ssi": return "ssi/%s/" % mkey(y,m)
    return "va-disability/%s/" % mkey(y,m)

def group_title(g, y, m):
    mn = mname(y, m)
    return {
     "birthdays-1-10": f"Social Security payment date {mn} for birthdays 1st–10th",
     "birthdays-11-20": f"Social Security payment date {mn} for birthdays 11th–20th",
     "birthdays-21-31": f"Social Security payment date {mn} for birthdays 21st–31st",
     "paid-on-3rd": f"Social Security payment date {mn}: paid on the 3rd (before May 1997 or SS + SSI)",
     "ssi": f"SSI payment date {mn}",
     "va": f"VA disability payment date {mn}",
    }[g]

def group_page(g, y, m, prev, nxt):
    paid = in_month(g, y, m); due = due_month(g, y, m)
    label, short, who = GROUPS[g]
    body = "<h1>%s</h1>" % esc(group_title(g, y, m))
    body += "<p>For %s. Regular rule: <b>%s</b> of each month%s.</p>" % (esc(who), esc(short),
            ", moved to the previous business day if it falls on a weekend or federal holiday" if g != "va" else ", for the previous month's benefits; if the 1st is a weekend or holiday, VA pays on the last business day before it")
    body += '<div class=card>'
    if paid:
        body += "<p class=muted>Deposited in %s:</p>" % mname(y, m) + "".join("<div class=big>%s</div><p>%s</p>" % (fmt(e["paid"]), ev_line(e)) for e in paid)
    else:
        body += "<p class=big>No %s deposit lands in %s.</p>" % (esc(label), mname(y, m))
    for e in due:
        if e not in paid:
            body += "<p>The %s was paid early on <b>%s</b> because %s %s. See <a href=\"%s/%s\">%s</a>.</p>" % (
                esc(e["forlab"]), fmt(e["paid"]), fmts(e["due"]), esc(e["reason"]), BASE, gpath(g, e["paid"].year, e["paid"].month), mname(e["paid"].year, e["paid"].month))
    if g == "va" and (y, m) == (2027, 12): body += VA_2027_12
    body += "</div>"
    if g == "va":
        body += "<p class=muted>VA does not publish a dated payment calendar. This date applies VA's published rule (benefits for a month are paid the first business day of the following month; earlier when that is a non-business day) to the OPM federal holiday calendar.</p>"
    if g == "ssi" or g == "paid-on-3rd":
        body += "<p class=muted>If you get both Social Security and SSI, SSA pays SSI on the 1st and Social Security on the 3rd (each moved earlier for weekends and holidays).</p>"
    body += cite(*srcs(g))
    body += '<p>Add every %s date to your calendar: <a href="%s/feeds/%s.ics">%s.ics feed</a> (<a href="%s/calendar-feeds/">how to subscribe</a>).</p>' % (esc(label), BASE, g, g, BASE)
    body += "<p>"
    if prev: body += '<a href="%s/%s">← %s</a> · ' % (BASE, gpath(g, *prev), mname(*prev))
    body += '<a href="%s/m/%s/">All benefit dates in %s</a>' % (BASE, mkey(y, m), mname(y, m))
    if nxt: body += ' · <a href="%s/%s">%s →</a>' % (BASE, gpath(g, *nxt), mname(*nxt))
    body += "</p>"
    other = [x for x in GROUPS if x != g]
    body += "<h2>Other payment groups in %s</h2><ul>" % mname(y, m) + "".join('<li><a href="%s/%s">%s</a></li>' % (BASE, gpath(o, y, m), esc(group_title(o, y, m))) for o in other) + "</ul>"
    d0 = paid[0]["paid"] if paid else None
    desc = ("%s: %s. Rule explained, weekend/holiday shifts, official source links. Independent site, not a government agency." % (group_title(g, y, m), fmts(d0) if d0 else "no deposit this month"))[:300]
    sec = {"ssi":("SSI","ssi/"), "va":("VA disability","va-disability/")}.get(g, ("Social Security","social-security/"))
    page(gpath(g, y, m), group_title(g, y, m) + " | Benefit Paydays", desc, body,
         crumbs=[("Home",""), sec, (mname(y, m), gpath(g, y, m))])

def month_overview(y, m, prev, nxt):
    rows = []
    for g in GROUPS:
        for e in in_month(g, y, m):
            rows.append((e["paid"], g, e))
    rows.sort(key=lambda r: r[0])
    title = "Social Security, SSI & VA payment dates %s" % mname(y, m)
    body = "<h1>%s</h1><p>Every federal benefit deposit date in %s that this site tracks, in date order.</p>" % (esc(title), mname(y, m))
    body += "<table><tr><th>Date</th><th>Who</th><th>Note</th></tr>"
    for d, g, e in rows:
        note = esc(e["forlab"])
        if e["early"]: note += " — paid early (%s %s)" % (fmts(e["due"]), esc(e["reason"]))
        body += '<tr><td><b>%s</b></td><td><a href="%s/%s">%s</a></td><td>%s</td></tr>' % (fmts(d), BASE, gpath(g, y, m), esc(GROUPS[g][0]), note)
    body += "</table>"
    hol = [(d, n) for d, n in sorted(HOLIDAYS.items()) if (d.year, d.month) == (y, m)]
    if hol:
        body += "<p>Federal holidays this month (OPM): " + "; ".join("%s — %s" % (fmts(d), esc(n)) for d, n in hol) + ".</p>"
    if (y, m) == (2027, 12): body += VA_2027_12
    body += "<p>SNAP (food stamps) dates depend on your state and case number — see <a href=\"%s/snap/\">SNAP schedules by state</a>.</p>" % BASE
    body += cite("ssa2026", "ssa2027", "vabull", "opm")
    body += "<p>"
    if prev: body += '<a href="%s/m/%s/">← %s</a> · ' % (BASE, mkey(*prev), mname(*prev))
    if nxt: body += '<a href="%s/m/%s/">%s →</a>' % (BASE, mkey(*nxt), mname(*nxt))
    body += "</p>"
    page("m/%s/" % mkey(y, m), title + " | Benefit Paydays", ("All %s Social Security, SSI and VA deposit dates with weekend/holiday shifts and official sources." % mname(y, m)), body,
         crumbs=[("Home",""), ("All months","months/"), (mname(y, m), "m/%s/" % mkey(y, m))])

def section_page(path, title, intro, groups, srcs_):
    body = "<h1>%s</h1>%s" % (esc(title), intro)
    body += "<table><tr><th>Month</th>" + "".join("<th>%s</th>" % esc(GROUPS[g][0].replace("Social Security, ","")) for g in groups) + "</tr>"
    for (y, m) in MONTHS:
        body += "<tr><td>%s</td>" % mname(y, m)
        for g in groups:
            ps = in_month(g, y, m)
            body += "<td>%s</td>" % ("<br>".join('<a href="%s/%s">%s</a>%s' % (BASE, gpath(g, y, m), e["paid"].strftime("%a %b ") + str(e["paid"].day), " *" if e["early"] or e["paid"].month != e["due"].month else "") for e in ps) or "—")
        body += "</tr>"
    body += "</table><p class=muted>* Moved earlier because the regular day is a weekend or federal holiday; a date at the end of a month can be the payment for the next month.</p>"
    body += cite(*srcs_)
    page(path, title + " | Benefit Paydays", (title + ": full Nov 2026 – Dec 2027 schedule, rules explained, official sources."), body, crumbs=[("Home",""), (title, path)])

def schedule_json():
    out = {}
    for g in GROUPS:
        out[g] = [[e["paid"].isoformat(), e["forlab"], e["early"], e["reason"], gpath(g, e["paid"].year, e["paid"].month)] for e in EV
                  if e["group"] == g and D(2026,11,1) <= e["paid"] <= D(2027,12,31)]
        out[g].sort()
    return out

SNAP = {
 "california": dict(name="California (CalFresh)", src=("snap-ca1","snap-ca2"), idname="last digit of your county case number", digits=1,
     table=[(str(i), "%d%s" % (i, "st" if i==1 else "nd" if i==2 else "rd" if i==3 else "th")) for i in range(1,10)] + [("0","10th")],
     map={**{str(i): i for i in range(1,10)}, "0": 10},
     notes="CDSS says CalFresh benefits are always sent within the first 10 days of every month, even if that day is a weekend or holiday."),
 "texas": dict(name="Texas (SNAP / Lone Star Card)", src=("snap-tx",), idname="last two digits of your SNAP EDG number", digits=2,
     table=[("00-03",1),("04-06",2),("07-10",3),("11-13",4),("14-17",5),("18-20",6),("21-24",7),("25-27",8),("28-31",9),("32-34",10),("35-38",11),("39-41",12),("42-45",13),("46-49",14),("50-53",15),("54-57",16),("58-60",17),("61-64",18),("65-67",19),("68-71",20),("72-74",21),("75-78",22),("79-81",23),("82-85",24),("86-88",25),("89-92",26),("93-95",27),("96-99",28)],
     notes="Texas HHS: households certified before May 1, 2023 keep their existing issuance schedule (based on when benefits were first certified) unless benefits had a break of at least six months and the household reapplied after May 1, 2023. Your award letter (TF0001) shows your day."),
 "connecticut": dict(name="Connecticut (SNAP)", src=("snap-ct",), idname="last two digits of your Client ID", digits=2,
     table=[("00-12",1),("13-24",2),("25-37",3),("38-49",4),("50-62",5),("63-74",6),("75-87",7),("88-99",8)],
     notes="Connecticut DSS: beginning March 1, 2026, SNAP benefits are issued over the first 8 days of the month; cash benefits on the 1st only."),
 "michigan": dict(name="Michigan (Food Assistance Program)", src=("snap-mi",), idname="last digit of the head of household's recipient ID", digits=1,
     table=[("0",3),("1",5),("2",7),("3",9),("4",11),("5",13),("6",15),("7",17),("8",19),("9",21)],
     notes="Michigan DHHS: the recipient ID number does not appear on the Bridge card; the EBT schedule is mailed to each client."),
}
def snap_map(st):
    s = SNAP[st]
    if "map" in s: return s["map"]
    mp = {}
    for r, day in s["table"]:
        if "-" in r:
            a, b = r.split("-")
            for i in range(int(a), int(b)+1): mp["%02d" % i] = day
        else: mp[r] = day
    return mp

def ics(g):
    lines = ["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//Benefit Paydays//benefit-paydays//EN","CALSCALE:GREGORIAN","METHOD:PUBLISH",
             "X-WR-CALNAME:%s (Benefit Paydays, unofficial)" % GROUPS[g][0], "X-PUBLISHED-TTL:P7D", "REFRESH-INTERVAL;VALUE=DURATION:P7D"]
    stamp = "20261028T000000Z"
    for e in sorted((e for e in EV if e["group"] == g and D(2026,11,1) <= e["paid"] <= D(2027,12,31)), key=lambda e: e["paid"]):
        d = e["paid"]; n = d + dt.timedelta(days=1)
        summ = "%s payment" % ("VA" if g == "va" else "SSI" if g == "ssi" else "Social Security")
        desc = "%s. Expected deposit date from published rules; confirm with your agency. Independent site, not affiliated with any government agency. Never share your SSN." % e["forlab"]
        if g == "va" and d == D(2027,12,30): desc += " Unconfirmed: may arrive Dec 31, 2027."
        url = BASE + "/" + gpath(g, d.year, d.month)
        lines += ["BEGIN:VEVENT","UID:%s-%s@benefit-paydays" % (g, d.isoformat()),"DTSTAMP:"+stamp,"DTSTART;VALUE=DATE:"+d.strftime("%Y%m%d"),"DTEND;VALUE=DATE:"+n.strftime("%Y%m%d"),
                  "SUMMARY:"+summ,"DESCRIPTION:"+desc.replace(",", "\\,").replace(";","\\;"),"URL:"+url,"TRANSP:TRANSPARENT","END:VEVENT"]
    lines.append("END:VCALENDAR")
    out = []
    for l in lines:
        while len(l.encode()) > 74:
            out.append(l[:73]); l = " " + l[73:]
        out.append(l)
    os.makedirs(os.path.join(OUT, "feeds"), exist_ok=True)
    open(os.path.join(OUT, "feeds", g + ".ics"), "w", newline="").write("\r\n".join(out) + "\r\n")

from pages import home, cola, snap_pages, static_pages

def main():
    check_against_pdf()
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    ctx = dict(page=page, BASE=BASE, cite=cite, esc=esc, GROUPS=GROUPS, MONTHS=MONTHS, SNAP=SNAP, snap_map=snap_map, schedule_json=schedule_json,
               mname=mname, mkey=mkey, gpath=gpath, group_title=group_title, SRC=SRC, CHECKED=CHECKED, fmts=fmts, in_month=in_month)
    home(ctx)
    for i, (y, m) in enumerate(MONTHS):
        prev = MONTHS[i-1] if i else None; nxt = MONTHS[i+1] if i+1 < len(MONTHS) else None
        month_overview(y, m, prev, nxt)
        for g in GROUPS: group_page(g, y, m, prev, nxt)
    section_page("social-security/", "Social Security payment dates 2026–2027 by birthday",
        "<p>SSA pays retirement, survivors and disability (SSDI) benefits on a Wednesday chosen by your birth date: 1st–10th → second Wednesday, 11th–20th → third Wednesday, 21st–31st → fourth Wednesday. If you got benefits before May 1997, or get both Social Security and SSI, Social Security is paid on the 3rd. Any of these days that falls on a weekend or federal holiday moves to the business day before.</p>",
        ["birthdays-1-10","birthdays-11-20","birthdays-21-31","paid-on-3rd"], ("ssa2026","ssa2027","opm"))
    section_page("ssi/", "SSI payment dates 2026–2027",
        "<p>SSA pays Supplemental Security Income on the 1st of each month. When the 1st is a weekend or federal holiday, SSI arrives on the business day before — so some months have two SSI deposits and the next month has none. That early deposit is next month's payment, not a bonus.</p>",
        ["ssi"], ("ssa2026","ssa2027","opm"))
    section_page("va-disability/", "VA disability payment dates 2026–2027",
        "<p>VA says compensation, pension, education and survivors benefits are paid monthly; benefits for a month are normally paid on the first business day of the following month, and when that day is a non-business day or holiday, on the last business day before the 1st. VA does not publish a dated calendar, so the dates below apply that rule to the OPM holiday calendar. The December 2027 date is unconfirmed (see the December 2027 page).</p>",
        ["va"], ("vabull","usc5120","opm"))
    ml = "<h1>All months: benefit payment dates Nov 2026 – Dec 2027</h1><ul class=months>" + "".join('<li><a href="%s/m/%s/">%s</a></li>' % (BASE, mkey(y,m), mname(y,m)) for y, m in MONTHS) + "</ul>"
    page("months/", "Benefit payment dates by month, Nov 2026 – Dec 2027 | Benefit Paydays", "Month-by-month Social Security, SSI and VA payment dates, Nov 2026 to Dec 2027.", ml, crumbs=[("Home",""),("All months","months/")])
    cola(ctx); snap_pages(ctx); static_pages(ctx)
    for g in GROUPS: ics(g)
    # sitemap, robots, 404, nojekyll
    sm = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in PAGES:
        if p == "404.html": continue
        sm.append("<url><loc>%s/%s</loc><lastmod>2026-10-28</lastmod></url>" % (BASE, p))
    sm.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w").write("\n".join(sm) + "\n")
    open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % BASE)
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    print("pages:", len([p for p in PAGES if p != "404.html"]))

if __name__ == "__main__":
    main()
