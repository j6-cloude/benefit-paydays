import json

def home(c):
    B = c["BASE"]; data = json.dumps(c["schedule_json"]())
    snap = {k: dict(name=v["name"], digits=v["digits"], idname=v["idname"], map=c["snap_map"](k), note=v["notes"]) for k, v in c["SNAP"].items()}
    body = """<h1>When is my next benefit payment?</h1>
<p>Find your next Social Security, SSI, VA disability or SNAP deposit date. Only your birth <i>day of the month</i> is needed — never your SSN, name or full birth date. Everything runs in your browser; nothing is sent anywhere.</p>
<div class=card><form id=f onsubmit="return go()">
<label for=prog>What do you get?</label>
<select id=prog onchange=sync()><option value=ss>Social Security (retirement, survivors, SSDI)</option><option value=ssi>SSI only</option><option value=both>Both Social Security and SSI</option><option value=va>VA disability compensation or pension</option><option value=snap>SNAP / food stamps (EBT)</option></select>
<div id=ssbox><label for=bd>Day of the month you were born (1–31)</label><input id=bd type=number min=1 max=31 inputmode=numeric placeholder="e.g. 14">
<label class=chk><input type=checkbox id=old> I started getting Social Security before May 1997</label></div>
<div id=snapbox hidden><label for=st>State</label><select id=st onchange=sync()></select><label for=dg id=dgl>Digits</label><input id=dg inputmode=numeric maxlength=2 placeholder="">
<p class=muted>Only states with an official schedule we verified are listed. <a href="__B__/snap/">About SNAP dates</a>.</p></div>
<button type=submit>Show my dates</button></form><div id=out class=res aria-live=polite></div></div>
<h2>Browse dates</h2><ul>
<li><a href="__B__/social-security/">Social Security payment dates 2026–2027 by birthday</a></li>
<li><a href="__B__/ssi/">SSI payment dates 2026–2027</a></li>
<li><a href="__B__/va-disability/">VA disability payment dates 2026–2027</a></li>
<li><a href="__B__/snap/">SNAP payment dates by state</a></li>
<li><a href="__B__/cola-2027/">2027 COLA (3.6%) calculator</a></li>
<li><a href="__B__/months/">Every month, Nov 2026 – Dec 2027</a> · <a href="__B__/calendar-feeds/">Calendar (.ics) feeds</a></li></ul>
""".replace("__B__", B) + c["cite"]("ssa2026","ssa2027","vabull","opm") + """
<script>
var S=__DATA__,SN=__SNAP__,B="__B__",L={"birthdays-1-10":"Social Security (birthday 1st–10th, 2nd Wednesday)","birthdays-11-20":"Social Security (birthday 11th–20th, 3rd Wednesday)","birthdays-21-31":"Social Security (birthday 21st–31st, 4th Wednesday)","paid-on-3rd":"Social Security (paid on the 3rd)","ssi":"SSI","va":"VA"};
var st=document.getElementById('st');for(var k in SN){var o=document.createElement('option');o.value=k;o.textContent=SN[k].name;st.appendChild(o);}
function sync(){var p=document.getElementById('prog').value;document.getElementById('ssbox').hidden=!(p=='ss'||p=='both');document.getElementById('snapbox').hidden=p!='snap';
 var s=SN[st.value];document.getElementById('dgl').textContent='Enter the '+s.idname+' ('+s.digits+' digit'+(s.digits>1?'s':'')+')';document.getElementById('dg').maxLength=s.digits;}
sync();
function today(){var d=new Date();return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2);}
function nice(iso){var p=iso.split('-');var d=new Date(+p[0],p[1]-1,+p[2]);return d.toLocaleDateString('en-US',{weekday:'long',month:'long',day:'numeric',year:'numeric'});}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]});}
function list(g){var t=today(),r=S[g].filter(function(x){return x[0]>=t}).slice(0,3);
 if(!r.length)return '<p>No dates on file after today for '+L[g]+'. This site covers Nov 2026 – Dec 2027.</p>';
 return '<p><b>'+L[g]+'</b></p>'+r.map(function(x,i){return '<div class=item>'+(i==0?'<div class=big>'+nice(x[0])+'</div>':'<b>'+nice(x[0])+'</b>')+'<div>'+esc(x[1])+(x[2]?' — paid early because the regular day '+esc(x[3]):'')+' · <a href="'+B+'/'+x[4]+'">details</a></div></div>'}).join('')+'<p class=muted><a href="'+B+'/feeds/'+g+'.ics">Add all '+L[g]+' dates to your calendar (.ics)</a></p>';}
function go(){var p=document.getElementById('prog').value,o=document.getElementById('out'),h='';
 if(p=='ss'||p=='both'){var d=parseInt(document.getElementById('bd').value,10),old=document.getElementById('old').checked;
  if(p=='ss'&&!old&&!(d>=1&&d<=31)){o.innerHTML='<p>Please enter the day of the month you were born (1–31).</p>';return false;}
  var g=(old||p=='both')?'paid-on-3rd':(d<=10?'birthdays-1-10':d<=20?'birthdays-11-20':'birthdays-21-31');h+=list(g);if(p=='both')h+=list('ssi');}
 else if(p=='ssi')h=list('ssi');else if(p=='va')h=list('va');
 else{var s=SN[st.value],v=document.getElementById('dg').value.trim();if(!/^[0-9]+$/.test(v)||v.length!=s.digits){o.innerHTML='<p>Enter exactly '+s.digits+' digit(s).</p>';return false;}
  var day=s.map[v];h='<p><b>'+esc(s.name)+'</b></p><div class=big>Day '+day+' of each month</div><p>Benefits are loaded on the '+day+(day==1||day==21?'st':day==2||day==22?'nd':day==3||day==23?'rd':'th')+' of each month, per the state schedule. '+esc(s.note)+' Your approval notice shows your exact day. <a href="'+B+'/snap/'+st.value+'/">Details and source</a>.</p>';}
 o.innerHTML=h+'<p class=muted>Estimated from published rules. Confirm with your official notice. We never ask for your SSN.</p>';return false;}
</script>""".replace("__DATA__", data).replace("__SNAP__", json.dumps(snap)).replace("__B__", B)
    ld = {"@context":"https://schema.org","@type":"WebSite","name":"Benefit Paydays","url":B+"/","description":"Independent, unofficial lookup of US federal benefit payment dates."}
    c["page"]("", "When is my next Social Security, SSI, VA or SNAP payment? (2026–2027) | Benefit Paydays",
              "Free, private lookup of your next Social Security, SSI, VA disability or SNAP deposit date, Nov 2026 – Dec 2027. Independent site; we never ask for your SSN.", body, jsonld=ld)

def cola(c):
    B = c["BASE"]
    body = """<h1>2027 Social Security COLA calculator (3.6%)</h1>
<p>SSA announced a <b>3.6% cost-of-living adjustment</b> for 2027. It starts with benefits payable to nearly 72 million Social Security beneficiaries in January 2027; increased payments to about 7.3 million SSI recipients begin on December 31, 2026.</p>
<div class=card><label for=cur>Your current monthly Social Security benefit, before any Medicare deduction ($)</label><input id=cur type=number min=0 step=0.01 inputmode=decimal placeholder="e.g. 2095">
<button onclick="calc()">Estimate my 2027 benefit</button><div id=r class=res aria-live=polite></div>
<p class=muted>This is a simple estimate (current × 1.036). SSA's own rounding and any Medicare Part B premium change are not included — the 2027 Part B premium had not been announced by CMS when we checked. Your COLA notice from SSA has your exact amount (SSA says notices go online in late November 2026 for <i>my Social Security</i> account holders who sign up by November 18, 2026).</p></div>
<script>function calc(){var v=parseFloat(document.getElementById('cur').value);var r=document.getElementById('r');if(!(v>0)){r.innerHTML='<p>Enter an amount.</p>';return;}
var n=v*1.036;r.innerHTML='<div class=big>≈ $'+n.toFixed(2)+' / month</div><p>About $'+(n-v).toFixed(2)+' more per month (estimate).</p>';}</script>
<h2>Key 2027 amounts from SSA</h2>
<table><tr><th>Item</th><th>2026</th><th>2027</th></tr>
<tr><td>SSI federal payment standard, individual</td><td>$994/mo</td><td><b>$1,029/mo</b></td></tr>
<tr><td>SSI federal payment standard, couple</td><td>$1,491/mo</td><td><b>$1,544/mo</b></td></tr>
<tr><td>SSI resource limit, individual / couple</td><td>$2,000 / $3,000</td><td>$2,000 / $3,000</td></tr>
<tr><td>Maximum benefit, worker retiring at full retirement age</td><td>$4,152/mo</td><td>$4,188/mo</td></tr>
<tr><td>Earnings test, under full retirement age</td><td>$24,480/yr ($2,040/mo)</td><td>$25,560/yr ($2,130/mo)</td></tr>
<tr><td>Earnings test, year you reach full retirement age</td><td>$65,160/yr ($5,430/mo)</td><td>$67,920/yr ($5,660/mo)</td></tr>
<tr><td>Maximum taxable earnings</td><td>$184,500</td><td>$192,300</td></tr>
<tr><td>Quarter of coverage</td><td>$1,890</td><td>$1,970</td></tr>
<tr><td>Substantial gainful activity, non-blind / blind</td><td>$1,690 / $2,830 per mo</td><td>$1,770 / $2,950 per mo</td></tr>
<tr><td>Trial work period</td><td>$1,210/mo</td><td>$1,270/mo</td></tr></table>
<h2>Estimated average monthly benefits (SSA)</h2>
<table><tr><th>Type</th><th>Before 3.6% COLA</th><th>After</th></tr>
<tr><td>All retired workers</td><td>$2,095</td><td>$2,170</td></tr><tr><td>Aged couple, both receiving benefits</td><td>$3,238</td><td>$3,355</td></tr>
<tr><td>Widowed mother with two children</td><td>$3,932</td><td>$4,074</td></tr><tr><td>Aged widow(er) alone</td><td>$1,936</td><td>$2,005</td></tr>
<tr><td>Disabled worker, spouse and one or more children</td><td>$2,970</td><td>$3,077</td></tr><tr><td>All disabled workers</td><td>$1,642</td><td>$1,701</td></tr></table>
<p>The first SSI payment at the new 2027 rate arrives <a href="__B__/ssi/2026-12/">Thursday, December 31, 2026</a> (it is the January 2027 payment). The first Social Security payments at the new rate arrive in January 2027: <a href="__B__/m/2027-01/">see January 2027 dates</a>.</p>
<p><b>Medicare 2027 Part B premium / IRMAA:</b> not covered yet — CMS had not published 2027 figures when we checked on __C__. We will not guess.</p>
""".replace("__B__", B).replace("__C__", c["CHECKED"]) + c["cite"]("cola", "colafs")
    c["page"]("cola-2027/", "2027 Social Security COLA calculator: 3.6% raise, SSI $1,029 max | Benefit Paydays",
              "Estimate your 2027 Social Security benefit with SSA's 3.6% COLA. 2027 SSI maximums $1,029 / $1,544, earnings limits, taxable max. Independent site.", body,
              crumbs=[("Home",""),("2027 COLA","cola-2027/")])

def snap_pages(c):
    B = c["BASE"]; esc = c["esc"]
    body = "<h1>SNAP (food stamps) payment dates by state</h1><p>Each state sets its own SNAP issuance schedule, usually by a digit of your case or ID number. We only list states whose schedule we verified on the state agency's own site. Your approval notice is the final word.</p><ul>"
    for k, s in c["SNAP"].items():
        body += '<li><a href="%s/snap/%s/">%s SNAP payment schedule</a></li>' % (B, k, esc(s["name"]))
    body += "</ul><p class=muted>More states will be added only after we can verify them on an official state page.</p>"
    c["page"]("snap/", "SNAP EBT payment schedule by state (2026–2027) | Benefit Paydays", "When SNAP benefits load on your EBT card in California, Texas, Connecticut and Michigan, from official state schedules.", body, crumbs=[("Home",""),("SNAP","snap/")])
    for k, s in c["SNAP"].items():
        t = "%s SNAP EBT deposit schedule 2026–2027" % s["name"].split(" (")[0]
        b = "<h1>%s</h1><p>%s benefits are loaded according to the <b>%s</b>.</p><table><tr><th>%s</th><th>Benefits available on day</th></tr>" % (esc(t), esc(s["name"]), esc(s["idname"]), esc(s["idname"].capitalize()))
        for r, d in s["table"]:
            b += "<tr><td>%s</td><td>%s</td></tr>" % (esc(str(r)), esc(str(d)))
        b += "</table><p>%s</p>" % esc(s["notes"])
        b += "<p class=muted>The same day applies every month. Never give your EBT card number or PIN to anyone who calls or texts you.</p>" + c["cite"](*s["src"])
        c["page"]("snap/%s/" % k, t + " | Benefit Paydays", ("%s: which day SNAP benefits load, by %s. From the official state schedule." % (t, s["idname"]))[:300], b,
                  crumbs=[("Home",""),("SNAP","snap/"),(s["name"],"snap/%s/" % k)])

def static_pages(c):
    B = c["BASE"]; esc = c["esc"]; G = c["GROUPS"]
    feeds = "<h1>Benefit payment calendar feeds (.ics)</h1><p>Subscribe once and your phone or computer calendar shows every expected deposit date. In Google Calendar: <i>Other calendars → + → From URL</i> and paste the link. On iPhone: <i>Settings → Calendar → Accounts → Add Account → Other → Add Subscribed Calendar</i>. In Outlook: <i>Add calendar → Subscribe from web</i>.</p><table><tr><th>Group</th><th>Feed URL</th></tr>"
    for g, (lab, short, who) in G.items():
        feeds += '<tr><td>%s</td><td><a href="%s/feeds/%s.ics">%s/feeds/%s.ics</a></td></tr>' % (esc(lab), B, g, B, g)
    feeds += "</table><p class=muted>Feeds cover Nov 2026 – Dec 2027. They contain only dates, no personal data. Subscribing sends no information about you to us (this site has no server code and no analytics).</p>"
    c["page"]("calendar-feeds/", "Social Security, SSI & VA payment calendar feeds (.ics) | Benefit Paydays", "Free subscribable calendar feeds of Social Security, SSI and VA payment dates, Nov 2026 – Dec 2027.", feeds, crumbs=[("Home",""),("Calendar feeds","calendar-feeds/")])
    s = "<h1>Sources</h1><p>Every date and amount on this site comes from these official pages, fetched and read on %s. Dates for months SSA has printed were checked against SSA's schedules; all Nov 2026 – Dec 2027 Social Security and SSI dates on this site match SSA's 2026 and 2027 schedules exactly.</p><ul>" % c["CHECKED"]
    for k, (n, u, note) in c["SRC"].items():
        s += '<li><a href="%s" rel="noopener">%s</a> — %s</li>' % (u, esc(n), esc(note))
    s += "</ul><h2>Not included (could not verify)</h2><ul><li>Medicare 2027 Part B premium, deductible and IRMAA brackets — not yet published by CMS.</li><li>A dated VA payment calendar — VA publishes the rule only; dates here are computed from it.</li><li>SNAP schedules for states other than those listed.</li></ul>"
    c["page"]("sources/", "Sources for benefit payment dates and 2027 COLA | Benefit Paydays", "Official SSA, VA, OPM and state sources used for every payment date and amount on Benefit Paydays.", s, crumbs=[("Home",""),("Sources","sources/")])
    a = "<h1>About Benefit Paydays</h1><p>Benefit Paydays is an <b>independent, unofficial</b> site. It is not affiliated with, endorsed by, or connected to the Social Security Administration, the Department of Veterans Affairs, USDA, any state agency, or any government body. We do not handle claims, payments or applications and cannot see your benefits.</p><p>We publish expected deposit dates computed from each agency's published rules and the federal holiday calendar, and we cite the official source on every page. If an agency's notice to you says something different, the agency is right.</p><p><b>Scam warning:</b> SSA, VA and state agencies will not threaten you, demand payment by gift card, crypto or wire, or ask for your full SSN by text. Never share your SSN, EBT PIN or bank login with a caller or website. We never ask for your SSN.</p><p>No ads, no tracking, no accounts.</p>"
    c["page"]("about/", "About Benefit Paydays (independent, not a government site)", "Benefit Paydays is an independent site, not affiliated with SSA, VA, USDA or any government agency.", a, crumbs=[("Home",""),("About","about/")])
    p = "<h1>Privacy</h1><p>This is a static website. It has no server-side code, no forms that submit anywhere, no cookies, no analytics, no ads and no third-party scripts. The payment lookup and COLA calculator run entirely in your browser; what you type never leaves your device. We never ask for your Social Security number, name, address or full birth date.</p><p>The site is hosted on GitHub Pages; GitHub may keep standard server logs (see GitHub's privacy statement).</p>"
    c["page"]("privacy/", "Privacy | Benefit Paydays", "No data collected: lookups run in your browser. No cookies, analytics or ads.", p, crumbs=[("Home",""),("Privacy","privacy/")])
    c["page"]("404.html", "Page not found | Benefit Paydays", "Page not found.", '<h1>Page not found</h1><p><a href="%s/">Find your next payment date</a></p>' % B)
