#!/usr/bin/env python3
"""
Mortgage Overpayment Calculator
Generates a formatted HTML illustration of overpayment scenarios.

Usage:
  python3 mortgage_calculator.py           # interactive prompt
  python3 mortgage_calculator.py 350       # pass overpayment on command line
"""

import os
import sys
from datetime import date

# ── Mortgage parameters ────────────────────────────────────────────────────────
INITIAL_BALANCE = 465_000.00
ANNUAL_RATE     = 4.02
MONTHLY_RATE    = ANNUAL_RATE / 100 / 12
TERM_YEARS      = 29
TERM_MONTHS     = TERM_YEARS * 12          # 348
BASE_PAYMENT    = 2_000.00

PRESET_OVERPAYMENTS = [0, 300, 500]        # always shown for comparison

CONFIG_FILE = os.path.expanduser("~/.mortgage_overpayment")
OUTPUT_DIR  = os.path.expanduser("~/mortgage_reports")


# ── Date helper ────────────────────────────────────────────────────────────────

def add_months(d: date, n: int) -> date:
    total = d.month - 1 + n
    return date(d.year + total // 12, total % 12 + 1, 1)


# ── Simulation ─────────────────────────────────────────────────────────────────

def simulate(extra_monthly: float) -> dict:
    today   = date.today()
    start   = date(today.year, today.month, 1)
    balance = INITIAL_BALANCE
    payment = BASE_PAYMENT + extra_monthly
    total_interest = 0.0
    snaps   = {}
    end_month = TERM_MONTHS

    for m in range(1, TERM_MONTHS + 1):
        if balance < 0.005:
            end_month = m - 1
            balance   = 0.0
            break

        mo_interest = balance * MONTHLY_RATE
        principal   = payment - mo_interest
        total_interest += mo_interest

        if principal >= balance:          # clears this month
            balance   = 0.0
            end_month = m
            for yr in (5, 10, 15):
                if yr not in snaps:
                    snaps[yr] = _snap(0.0, total_interest)
            break

        if principal > 0:
            balance -= principal
        # if principal <= 0, payment < interest → balance grows (edge case, tracked)

        if m in (60, 120, 180):
            snaps[m // 12] = _snap(balance, total_interest)
    else:
        for yr in (5, 10, 15):
            if yr not in snaps:
                snaps[yr] = _snap(balance, total_interest)

    return {
        "extra":           extra_monthly,
        "monthly_payment": payment,
        "snaps":           snaps,
        "end_month":       end_month,
        "end_date":        add_months(start, end_month),
        "total_interest":  round(total_interest, 2),
        "final_balance":   round(balance, 2),
    }


def _snap(balance: float, total_interest: float) -> dict:
    return {
        "balance":       round(balance, 2),
        "interest_paid": round(total_interest, 2),
        "equity":        round(INITIAL_BALANCE - balance, 2),
    }


# ── Formatting helpers ─────────────────────────────────────────────────────────

def fc(v: float) -> str:   return f"£{v:,.0f}"
def fc2(v: float) -> str:  return f"£{v:,.2f}"
def fy(d: date) -> str:    return d.strftime("%B %Y")


# ── CSS ────────────────────────────────────────────────────────────────────────

CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Segoe UI', Arial, sans-serif;
  background: #f0f4f8;
  color: #2c3e50;
  padding: 2rem;
  max-width: 1100px;
  margin: 0 auto;
}
h1  { color: #1a3c5e; font-size: 2rem; margin-bottom: 0.25rem; }
h2  { color: #1a3c5e; font-size: 1.25rem; margin: 2.5rem 0 0.8rem;
      border-bottom: 3px solid #2c6496; padding-bottom: 0.4rem; }
h3  { color: #2c6496; font-size: 1.05rem; margin: 0 0 1rem; }
.header-meta { color: #7f8c8d; font-size: 0.9rem; margin-bottom: 1.5rem; }

.mortgage-params {
  display: flex; flex-wrap: wrap; gap: 1rem;
  background: linear-gradient(135deg, #1a3c5e, #2c6496);
  color: white; border-radius: 10px; padding: 1.2rem 1.5rem;
  margin-bottom: 2rem; box-shadow: 0 3px 10px rgba(0,0,0,.2);
}
.param { text-align: center; min-width: 120px; }
.param .label { font-size: 0.7rem; opacity: 0.75; text-transform: uppercase;
                letter-spacing: 0.07em; margin-bottom: 0.3rem; }
.param .value { font-size: 1.25rem; font-weight: 700; }
.param.highlight-param { background: rgba(255,255,255,0.15); border-radius: 6px; padding: 0.4rem 0.8rem; }

.card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 0.5rem; }
.card {
  background: white; border-radius: 10px; padding: 1.4rem 1.5rem;
  box-shadow: 0 2px 6px rgba(0,0,0,.08);
}
.card.actual-card { border: 2px solid #f39c12; }
.card h3 { border-bottom: 1px solid #eef0f3; padding-bottom: 0.6rem; }

.metric { margin-top: 0.8rem; border-left: 3px solid #2c6496; padding-left: 0.8rem; }
.metric .label { font-size: 0.75rem; color: #7f8c8d; margin-bottom: 0.15rem; }
.metric .value { font-size: 1.05rem; font-weight: 600; color: #1a3c5e; }
.metric.green { border-color: #27ae60; }
.metric.green .value { color: #1e8449; }
.metric.amber { border-color: #f39c12; }
.metric.amber .value { color: #d68910; }
.metric.red { border-color: #c0392b; }
.metric.red .value { color: #c0392b; }

table { width: 100%; border-collapse: collapse; background: white;
        border-radius: 10px; overflow: hidden;
        box-shadow: 0 2px 6px rgba(0,0,0,.08); margin-bottom: 1rem; }
th { background: #2c6496; color: white; padding: 0.75rem 1rem;
     text-align: right; font-size: 0.9rem; }
th:first-child { text-align: left; }
td { padding: 0.65rem 1rem; border-bottom: 1px solid #eef0f3;
     text-align: right; font-size: 0.9rem; }
td:first-child { text-align: left; font-weight: 500; color: #34495e; }
tr:last-child td { border-bottom: none; }
tr:nth-child(even) td { background: #f9fbfd; }
tr.section-header td { background: #dce8f5; font-weight: 700;
                        color: #1a3c5e; font-size: 0.85rem;
                        text-transform: uppercase; letter-spacing: 0.05em; }
tr.total-row td { background: #1a3c5e !important; color: white;
                  font-weight: 700; }
.saving  { color: #1e8449 !important; font-weight: 700; }
.warning { color: #c0392b; }
.note    { color: #7f8c8d; font-size: 0.8rem; font-style: italic; margin-top: 0.4rem; }
.badge {
  display: inline-block; padding: 0.15rem 0.5rem; border-radius: 12px;
  font-size: 0.75rem; font-weight: 600; margin-left: 0.4rem;
  background: #f39c12; color: white; vertical-align: middle;
}
footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #d5dbdb;
         color: #aab7b8; font-size: 0.78rem; text-align: center; line-height: 1.8; }
"""


# ── HTML builder ───────────────────────────────────────────────────────────────

def scenario_label(s: dict) -> str:
    if s["extra"] == 0:
        return "No overpayment"
    return f"+{fc(s['extra'])}/mo"


def build_html(scenarios: list, actual_extra: float) -> str:
    base  = scenarios[0]   # no-overpayment baseline
    today = date.today()

    # ── Scenario cards ─────────────────────────────────────────────────────────
    def card(s: dict) -> str:
        lbl       = scenario_label(s)
        is_actual = (s["extra"] == actual_extra and actual_extra > 0)
        badge     = '<span class="badge">Your amount</span>' if is_actual else ""
        paid_off  = s["final_balance"] < 0.01
        extra     = s["extra"]

        if paid_off:
            end_str   = fy(s["end_date"])
            end_class = "green"
        else:
            end_str   = f"{fy(s['end_date'])} — {fc2(s['final_balance'])} still owed"
            end_class = "red"

        saving_metrics = ""
        if extra > 0:
            int_saved    = base["total_interest"] - s["total_interest"]
            months_saved = base["end_month"] - s["end_month"]
            saving_metrics = f"""
      <div class="metric green">
        <div class="label">Interest saved (full term)</div>
        <div class="value saving">{fc2(int_saved)}</div>
      </div>
      <div class="metric green">
        <div class="label">Time saved</div>
        <div class="value saving">{months_saved} months ({months_saved/12:.1f} yrs)</div>
      </div>"""

        return f"""
  <div class="card{'  actual-card' if is_actual else ''}">
    <h3>{lbl}{badge}</h3>
    <div class="metric">
      <div class="label">Monthly payment</div>
      <div class="value">{fc2(s['monthly_payment'])}</div>
    </div>
    <div class="metric">
      <div class="label">Total interest paid</div>
      <div class="value">{fc2(s['total_interest'])}</div>
    </div>
    <div class="metric {end_class}">
      <div class="label">Mortgage ends</div>
      <div class="value">{end_str}</div>
    </div>{saving_metrics}
  </div>"""

    cards_html = "\n".join(card(s) for s in scenarios)

    # ── Snapshot table ─────────────────────────────────────────────────────────
    col_headers = "".join(f"<th>{scenario_label(s)}</th>" for s in scenarios)

    snap_rows = []
    for yr in (5, 10, 15):
        snap_rows.append(
            f'<tr class="section-header"><td colspan="{1 + len(scenarios)}">Year {yr}</td></tr>'
        )
        for metric, key in (
            ("Remaining balance", "balance"),
            ("Interest paid to date", "interest_paid"),
            ("Equity built", "equity"),
        ):
            cells = "".join(
                f"<td>{fc2(s['snaps'].get(yr, {}).get(key, 0.0))}</td>"
                for s in scenarios
            )
            snap_rows.append(f"<tr><td>{metric}</td>{cells}</tr>")

    snap_table = f"""
<table>
  <thead><tr><th>Metric</th>{col_headers}</tr></thead>
  <tbody>
{''.join(snap_rows)}
  </tbody>
</table>"""

    # ── Interest saved table ───────────────────────────────────────────────────
    saved_rows = []
    for yr in (5, 10, 15):
        cells = ""
        for s in scenarios:
            if s["extra"] == 0:
                cells += "<td>—</td>"
            else:
                saved = (
                    base["snaps"].get(yr, {}).get("interest_paid", 0.0)
                    - s["snaps"].get(yr, {}).get("interest_paid", 0.0)
                )
                cls = ' class="saving"' if saved > 0 else ""
                cells += f"<td{cls}>{fc2(max(0, saved))}</td>"
        saved_rows.append(f"<tr><td>Interest saved by year {yr}</td>{cells}</tr>")

    # Full-term row
    total_cells = ""
    for s in scenarios:
        if s["extra"] == 0:
            total_cells += "<td>—</td>"
        else:
            saved = base["total_interest"] - s["total_interest"]
            total_cells += f'<td class="saving">{fc2(saved)}</td>'
    saved_rows.append(f'<tr class="total-row"><td>Total interest saved</td>{total_cells}</tr>')

    saved_table = f"""
<table>
  <thead><tr><th>Interest Saved vs No Overpayment</th>{col_headers}</tr></thead>
  <tbody>
{''.join(saved_rows)}
  </tbody>
</table>"""

    # ── Full-term summary table ────────────────────────────────────────────────
    term_rows = []
    for label_txt, key, fmt_fn in (
        ("Total paid (principal + interest)", None, None),
        ("Total interest paid", "total_interest", fc2),
        ("Final balance at term", "final_balance", fc2),
    ):
        cells = ""
        for s in scenarios:
            if key is None:
                v = BASE_PAYMENT * s["end_month"] + s["extra"] * s["end_month"]
                cells += f"<td>{fc2(v)}</td>"
            else:
                cells += f"<td>{fmt_fn(s[key])}</td>"
        term_rows.append(f"<tr><td>{label_txt}</td>{cells}</tr>")

    # End date row
    cells = "".join(
        f"<td>{fy(s['end_date'])}</td>" for s in scenarios
    )
    term_rows.append(f"<tr><td>Mortgage ends</td>{cells}</tr>")

    # Months saved row
    cells = ""
    for s in scenarios:
        if s["extra"] == 0:
            cells += "<td>—</td>"
        else:
            ms = base["end_month"] - s["end_month"]
            cells += f'<td class="saving">{ms} mo ({ms/12:.1f} yrs)</td>'
    term_rows.append(f'<tr class="total-row"><td>Time saved vs no overpayment</td>{cells}</tr>')

    term_table = f"""
<table>
  <thead><tr><th>Full-Term Totals</th>{col_headers}</tr></thead>
  <tbody>
{''.join(term_rows)}
  </tbody>
</table>"""

    # ── Assemble ───────────────────────────────────────────────────────────────
    actual_label = fc(actual_extra) if actual_extra > 0 else "£0"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mortgage Overpayment Illustration – {today.strftime('%B %Y')}</title>
  <style>{CSS}</style>
</head>
<body>

<h1>Mortgage Overpayment Illustration</h1>
<p class="header-meta">Generated on {today.strftime('%d %B %Y')} &nbsp;·&nbsp; Your overpayment: {actual_label}/mo</p>

<div class="mortgage-params">
  <div class="param"><div class="label">Outstanding Balance</div><div class="value">£465,000</div></div>
  <div class="param"><div class="label">Interest Rate</div><div class="value">4.02% p.a.</div></div>
  <div class="param"><div class="label">Remaining Term</div><div class="value">29 years</div></div>
  <div class="param"><div class="label">Base Payment</div><div class="value">£2,000/mo</div></div>
  <div class="param highlight-param"><div class="label">Your Overpayment</div><div class="value">{actual_label}/mo</div></div>
</div>

<h2>Scenario Overview</h2>
<div class="card-grid">
{cards_html}
</div>
<p class="note">&#9888;&#65039; With a base payment of £2,000/mo the mortgage does not fully amortise within 29 years.
Any overpayment accelerates payoff and reduces total interest significantly.</p>

<h2>Snapshots at Years 5, 10 &amp; 15</h2>
{snap_table}

<h2>Interest Saved vs No Overpayment</h2>
{saved_table}

<h2>Full-Term Summary</h2>
{term_table}

<footer>
  This illustration assumes a constant interest rate of 4.02% throughout the remaining term.<br>
  Actual figures will vary if the rate changes. Always check your mortgage T&amp;Cs before making overpayments —<br>
  many lenders cap penalty-free overpayments at 10% of the outstanding balance per year.
</footer>

</body>
</html>"""
    return html


# ── Input / config handling ────────────────────────────────────────────────────

def get_overpayment() -> float:
    # Command-line argument
    if len(sys.argv) > 1:
        try:
            val = float(sys.argv[1].lstrip("£").replace(",", ""))
            with open(CONFIG_FILE, "w") as f:
                f.write(str(val))
            return val
        except ValueError:
            print(f"Invalid amount: {sys.argv[1]}", file=sys.stderr)
            sys.exit(1)

    # Interactive
    if sys.stdin.isatty():
        print("\n" + "=" * 60)
        print("  Mortgage Overpayment Calculator")
        print("  Balance £465,000 · 4.02% · 29 yrs · Base £2,000/mo")
        print("=" * 60)
        while True:
            try:
                raw = input("\n  Enter your actual monthly overpayment amount (£): ").strip()
                val = float(raw.lstrip("£").replace(",", ""))
                if val < 0:
                    print("  Please enter 0 or a positive amount.")
                    continue
                with open(CONFIG_FILE, "w") as f:
                    f.write(str(val))
                return val
            except ValueError:
                print("  Please enter a number, e.g. 350 or 0.")
            except (EOFError, KeyboardInterrupt):
                print()
                sys.exit(0)

    # Non-interactive (cron): read saved config
    if os.path.exists(CONFIG_FILE):
        try:
            val = float(open(CONFIG_FILE).read().strip())
            print(f"[cron] Using saved overpayment: £{val:,.0f}/mo", file=sys.stderr)
            return val
        except (ValueError, IOError):
            pass

    print("[cron] No saved overpayment found – defaulting to £0.", file=sys.stderr)
    return 0.0


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    actual_extra = get_overpayment()

    extras = list(PRESET_OVERPAYMENTS)
    if actual_extra not in extras:
        extras.append(actual_extra)
    extras.sort()

    print(f"\n  Calculating {len(extras)} scenarios: " +
          ", ".join(f"£{e:,.0f}/mo" for e in extras) + " ...")

    scenarios = [simulate(e) for e in extras]
    html      = build_html(scenarios, actual_extra)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"mortgage_{date.today().strftime('%Y-%m')}.html"
    out_path = os.path.join(OUTPUT_DIR, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n  ✓ Report saved → {out_path}\n")
    return out_path


if __name__ == "__main__":
    main()
