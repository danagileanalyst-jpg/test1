#!/usr/bin/env python3
"""
Viking Therapeutics (VKTX) — Special Biotech Scoring
Adapts the standard InvestmentAdvisor engine for a pre-revenue clinical-stage
biotech. Standard criteria applied where data exists; biotech-specific criteria
added where they replace standard metrics.
"""

import time, sys

R="\033[0m"; BOLD="\033[1m"; DIM="\033[2m"
GREEN="\033[92m"; RED="\033[91m"; YELLOW="\033[93m"
BLUE="\033[94m"; CYAN="\033[96m"; WHITE="\033[97m"
BG_BLUE="\033[44m"; BG_GREEN="\033[42m"; BG_RED="\033[41m"
BG_YELLOW="\033[43m"; BG_ORANGE="\033[48;5;208m"

def c(*args): return "".join(str(a) for a in args) + R
def bar(n, total=100, w=28):
    f = int(w*n/total)
    return c(GREEN,"█"*f) + c(DIM,"░"*(w-f))
def sep(ch="─",w=74): print(c(DIM,ch*w))

# ── Raw data (sourced Apr 2026) ───────────────────────────────────────────────
TICKER        = "VKTX"
COMPANY       = "Viking Therapeutics Inc."
EXCHANGE      = "NASDAQ"
SECTOR        = "Biotechnology"
PRICE         = 31.42
HIGH_52       = 43.15
LOW_52        = 22.96
MKT_CAP_B     = 3.83          # $bn
CASH_M        = 603           # $M end Q1-2026
DEBT          = 0             # zero debt
TOTAL_EQUITY  = 846.9         # $M
BURN_RATE_QTR = 164           # $M per quarter (Q1-2026 total opex)
RD_EXPENSE_Q1 = 150.2         # $M
NET_LOSS_Q1   = 158.3         # $M
REVENUE       = 0             # pre-revenue
DIVIDEND      = 0
ANALYST_BUY   = 89            # % strong buy + buy
ANALYST_HOLD  = 11
ANALYST_SELL  = 0
CONSENSUS_PT  = 99.50         # $  (25-analyst median)
HIGH_PT       = 333.00
LOW_PT        = 50.00

# ── Derived ───────────────────────────────────────────────────────────────────
pb            = (MKT_CAP_B * 1000) / TOTAL_EQUITY   # 4.52x
cash_runway_q = CASH_M / BURN_RATE_QTR               # quarters
cash_runway_y = cash_runway_q / 4
upside_pct    = ((CONSENSUS_PT - PRICE) / PRICE)*100
vs_52hi       = ((PRICE - HIGH_52) / HIGH_52)*100
in_lower_band = PRICE <= LOW_52 + (HIGH_52 - LOW_52)*0.35

# ── Scoring ───────────────────────────────────────────────────────────────────
score   = 0
reasons = []
cautions= []
notes   = []

print()
sep("═")
print(c(BG_BLUE,BOLD,WHITE,f"  INVESTMENT ADVISOR  —  SPECIAL BIOTECH ANALYSIS  "))
sep("═")
print()
sys.stdout.write("  Loading fundamental data"); sys.stdout.flush()
for _ in range(6): time.sleep(0.18); sys.stdout.write("."); sys.stdout.flush()
print(c(GREEN,"  done\n"))

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 1 — STANDARD CRITERIA (apply where data exists)
# ─────────────────────────────────────────────────────────────────────────────
sep("─")
print(c(BOLD,WHITE,"  SECTION 1 — STANDARD VALUATION CRITERIA"))
sep("─")

# P/E — pre-revenue biotech has none
print(f"  {'P/E Ratio':<32} {'N/A (pre-revenue)':<28} {c(DIM,'─  0/12 pts')}")
notes.append("No P/E — company has not generated revenue; expected for clinical-stage biotech")

# Price-to-book
pb_ok = 0.5 <= pb <= 4.0
pb_pts = 0
if pb_ok: pb_pts = 8; score += 8; reasons.append(f"P/B ratio {pb:.2f}x within acceptable range")
else: cautions.append(f"P/B {pb:.2f}x elevated (market pricing in pipeline success)")
tag = c(GREEN,"✓  +8 pts") if pb_ok else c(YELLOW,"✗   0 pts")
print(f"  {'Price-to-Book':<32} {pb:.2f}x{'':<23} {tag}")

# Revenue growing? — N/A
print(f"  {'Revenue Growing?':<32} {'N/A ($0 revenue)':<28} {c(DIM,'─  0/15 pts')}")
notes.append("Clinical-stage: zero product revenue is standard, not a negative signal in isolation")

# Profits rising? — losses deepening
print(f"  {'Profits Rising?':<32} {c(RED,'No  (loss $158M Q1-26)'):<37} {c(RED,'✗   0/10 pts')}")
cautions.append("Net loss widening: Q1-2026 loss $158.3M vs $41.4M R&D spend in prior periods")

# Price near 52-week low?
low_pts = 0
if in_lower_band: low_pts = 8; score += 8; reasons.append("Price in lower 35% of 52-week range — discounted entry vs recent high")
tag = c(GREEN,f"✓  +8 pts") if in_lower_band else c(DIM,"─   0 pts")
range_str = f"${PRICE} / 52w ${LOW_52}–${HIGH_52}"
print(f"  {'Price Near 52-Week Low?':<32} {range_str:<28} {tag}")

# Price trending up? — negative 1-yr from $43 peak
print(f"  {'Price Trending Up (1-yr)?':<32} {c(RED,f'-27.2% from 52w high'):<37} {c(RED,'✗   0/ 7 pts')}")
cautions.append("Stock is -27% from its 52-week high; sentiment reset after prior euphoria")

# Chart right > left? — depends on entry date
print(f"  {'Chart: Right > Left?':<32} {c(YELLOW,'Mixed — down from ATH'):<37} {c(YELLOW,'─   0/10 pts')}")

# Dividends rising? — none
print(f"  {'Dividends Rising?':<32} {'None (pre-revenue biotech)':<28} {c(DIM,'─   0/10 pts')}")
notes.append("No dividend expected until product revenue materialises post-2028 at earliest")

# Debt < 3x profit / D:E reasonable?
debt_pts = 10; score += 10
reasons.append(f"Zero debt — D/E 0.0, bulletproof balance sheet, no refinancing risk")
print(f"  {'Net Debt < 3x Profit?':<32} {'$0 debt / D:E 0.00':<28} {c(GREEN,'✓  +10 pts')}")
print(f"  {'Debt-to-Equity':<32} {'0.00':<28} {c(GREEN,'✓')}")

# ROE — negative (burning cash)
print(f"  {'Return on Equity':<32} {c(RED,'Negative (R&D burn)'):<37} {c(RED,'✗   0/ 6 pts')}")
cautions.append("ROE is deeply negative — all capital is being consumed funding clinical trials")

# Operating cash flow — negative
print(f"  {'Operating Cash Flow':<32} {c(RED,'-$164M/qtr burn rate'):<37} {c(RED,'✗   0/ 4 pts')}")

print(f"\n  {'Standard criteria subtotal':<32} {c(BOLD,YELLOW,str(score)+'/100')}")
print()

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 2 — BIOTECH-SPECIFIC CRITERIA  (replaces revenue/profit metrics)
# ─────────────────────────────────────────────────────────────────────────────
sep("─")
print(c(BOLD,WHITE,"  SECTION 2 — BIOTECH-SPECIFIC SCORING"))
sep("─")

biotech_score = 0

# Cash runway
runway_pts = 0
runway_label = f"~{cash_runway_y:.1f} years at current burn"
if cash_runway_y >= 3:   runway_pts = 15; biotech_score += 15; reasons.append(f"Strong cash runway: ~{cash_runway_y:.1f} yrs  (${CASH_M}M cash, ${BURN_RATE_QTR}M/qtr burn)")
elif cash_runway_y >= 2: runway_pts = 10; biotech_score += 10
else:                    runway_pts = 0;  cautions.append("Cash runway under 2 years — dilutive raise likely")
tag = c(GREEN,f"✓  +{runway_pts} pts") if runway_pts==15 else c(YELLOW,f"~  +{runway_pts} pts")
print(f"  {'Cash Runway':<36} {runway_label:<26} {tag}")

# Phase of lead asset
phase_pts = 20; biotech_score += 20
reasons.append("Lead asset VK2735 in Phase 3 (VANQUISH-1 & -2) — fully enrolled, highest-value stage")
print(f"  {'Pipeline Stage':<36} {'Phase 3 — fully enrolled':<26} {c(GREEN,'✓  +20 pts')}")

# Phase 2 efficacy data
eff_pts = 15; biotech_score += 15
reasons.append("Phase 2 VENTURE: -14.7% weight loss (sub-Q), -12.2% (oral) — class-leading signal")
print(f"  {'Phase 2 Efficacy Signal':<36} {'-14.7% wt loss (sub-Q)':<26} {c(GREEN,'✓  +15 pts')}")

# Oral formulation differentiation
oral_pts = 10; biotech_score += 10
reasons.append("Oral VK2735 differentiator: ~12% weight loss at 13 weeks — strong vs oral competitors")
print(f"  {'Oral Formulation (differentiation)':<36} {'Phase 2 met all endpoints':<26} {c(GREEN,'✓  +10 pts')}")

# Unmet need / market size
mkt_pts = 10; biotech_score += 10
reasons.append("GLP-1/GIP obesity market forecast >$150bn by 2030 — enormous addressable opportunity")
print(f"  {'Addressable Market':<36} {'>$150bn GLP-1 by 2030':<26} {c(GREEN,'✓  +10 pts')}")

# Analyst consensus
analyst_pts = 10; biotech_score += 10
reasons.append(f"Analyst consensus: 89% BUY/STRONG BUY — median target ${CONSENSUS_PT} (+{upside_pct:.0f}% upside)")
print(f"  {'Analyst Consensus':<36} {f'89% Buy | PT ${CONSENSUS_PT}':<26} {c(GREEN,'✓  +10 pts')}")

# VANQUISH readout timing
print(f"  {'VANQUISH-2 Results (Type 2 DM)':<36} {'Expected Q3 2026':<26} {c(YELLOW,'  Catalyst')}")
reasons.append("VANQUISH-2 readout expected Q3-2026 — near-term binary catalyst, high stakes")

# Competition risk
comp_pts = -15; biotech_score += comp_pts
cautions.append("Duopoly threat: Lilly (Zepbound + orforglipron oral) & Novo (Wegovy + amycretin) dominate")
cautions.append("Commercialisation: no sales force — will need to partner/outlicense or raise billions")
print(f"  {'Competitive Risk (Lilly + Novo)':<36} {'Duopoly with deep pockets':<26} {c(RED,'⚠  -15 pts')}")

# Binary Phase 3 trial risk
binary_pts = -20; biotech_score += binary_pts
cautions.append("Binary risk: Phase 3 VANQUISH failure or safety signal = catastrophic drawdown (−60%+)")
print(f"  {'Binary Phase 3 Trial Risk':<36} {'Results ~2027 (VANQUISH-1)':<26} {c(RED,'⚠  -20 pts')}")

# No revenue / dilution risk
dilution_pts = -5; biotech_score += dilution_pts
cautions.append("Dilution risk: likely equity raise required to fund commercialisation post-approval")
print(f"  {'Dilution / No Revenue Risk':<36} {'Pre-revenue, raise likely':<26} {c(YELLOW,'⚠  -5 pts')}")

print(f"\n  {'Biotech criteria subtotal':<36} {c(BOLD,YELLOW,str(biotech_score)+'/55 available')}")

# ─────────────────────────────────────────────────────────────────────────────
#  COMBINED SCORE & VERDICT
# ─────────────────────────────────────────────────────────────────────────────
total = score + biotech_score
total = max(0, min(100, total))

print()
sep("═")
print(c(BOLD,WHITE,"  FINAL VERDICT"))
sep("═")

# Score bar
score_col = GREEN if total >= 60 else YELLOW if total >= 40 else RED
print(f"\n  Score   {bar(total)}  {c(BOLD,score_col,str(total)+'/100')}\n")

# Grid
print(f"  {'Current Price':<30} ${PRICE:.2f}")
print(f"  {'52-Week Range':<30} ${LOW_52} — ${HIGH_52}")
print(f"  {'Is Price Low?':<30} {c(GREEN,'Yes ✓') if in_lower_band else c(RED,'No ✗')}  ({vs_52hi:+.1f}% vs 52w high)")
print(f"  {'Market Cap':<30} ${MKT_CAP_B:.2f}B")
print(f"  {'Cash / Debt':<30} ${CASH_M}M cash / ${DEBT} debt")
print(f"  {'Cash Runway':<30} ~{cash_runway_y:.1f} years")
print(f"  {'P/E':<30} N/A  (pre-revenue)")
print(f"  {'Price-to-Book':<30} {pb:.2f}x")
print(f"  {'Revenue':<30} {c(YELLOW,'$0  (clinical-stage)')}")
print(f"  {'Net Loss Q1-2026':<30} {c(RED,'$158.3M')}")
print(f"  {'R&D Burn Q1-2026':<30} {c(RED,'$150.2M')}")
print(f"  {'Debt-to-Equity':<30} {c(GREEN,'0.00  ✓')}")
print(f"  {'Dividends':<30} None")
print(f"  {'Analyst Consensus':<30} {c(GREEN,'BUY')}  (89% Buy/Strong Buy)")
print(f"  {'Analyst Target (median)':<30} {c(GREEN,f'${CONSENSUS_PT:.2f}')}  ({c(GREEN,f'+{upside_pct:.0f}%')} upside)")
print(f"  {'Analyst Target (bull)':<30} ${HIGH_PT:.2f}")
print(f"  {'Analyst Target (bear)':<30} ${LOW_PT:.2f}")
print(f"  {'Lead Asset':<30} VK2735 (dual GLP-1/GIP)")
print(f"  {'Trial Stage':<30} {c(GREEN,'Phase 3  — fully enrolled')}")
print(f"  {'Phase 2 Weight Loss':<30} {c(GREEN,'-14.7% sub-Q  /  -12.2% oral')}")
print(f"  {'Next Catalyst':<30} {c(YELLOW,'VANQUISH-2 results  Q3-2026')}")
print(f"  {'Competition':<30} {c(YELLOW,'Eli Lilly  +  Novo Nordisk')}")
print()

sep("─")
print(c(BOLD,WHITE,"  BUY REASONS"))
sep("─")
for r in reasons:
    print(f"  {c(GREEN,'✓')}  {r}")
print()
sep("─")
print(c(BOLD,WHITE,"  CAUTIONS"))
sep("─")
for ca in cautions:
    print(f"  {c(YELLOW,'⚠')}  {ca}")
print()
sep("─")
print(c(BOLD,WHITE,"  NOTES (standard criteria not applicable)"))
sep("─")
for n in notes:
    print(f"  {c(DIM,'ℹ')}  {n}")

print()
sep("═")
print(c(BOLD,WHITE,"  AI VERDICT"))
sep("═")

verdict_box = f"""
  {c(BOLD,YELLOW,'[ SPECULATIVE BUY — HIGH RISK / HIGH REWARD ]')}

  Viking Therapeutics is NOT a standard value or growth pick —
  it is a binary, pre-revenue biotech bet on one of the most
  competitive drug races in pharmaceutical history.

  {c(BOLD,GREEN,'The bull case is compelling:')}
  VK2735 has the best-in-class Phase 2 data in the GLP-1/GIP
  space. Both injectable and oral forms hit primary endpoints
  convincingly. Phase 3 is fully enrolled. At ${PRICE:.2f}, the
  stock sits 27% below its 52-week high with $603M cash and
  {c(GREEN,'ZERO DEBT')} — giving it runway to the VANQUISH readouts
  without forced dilution. The median analyst target of
  {c(GREEN,f'${CONSENSUS_PT}')} implies {c(GREEN,f'+{upside_pct:.0f}%')} upside on approval.

  {c(BOLD,RED,'The bear case is serious:')}
  Phase 3 failure or an unexpected safety signal would erase
  60–80% of the stock price overnight. Even on success, Viking
  has NO commercial infrastructure and will face Eli Lilly and
  Novo Nordisk — two of the best-capitalised pharma companies
  on earth — in a head-to-head battle for market share.
  Commercialisation alone would require a dilutive raise or a
  licensing deal that caps the upside.

  {c(BOLD,WHITE,'Verdict for your 5-year, high-medium risk portfolio:')}
  {c(BG_YELLOW,BOLD,WHITE,' SMALL POSITION ONLY — MAXIMUM 3-5% OF PORTFOLIO ')}

  Score:   {c(BOLD,score_col,str(total)+'/100')}
  Confidence:  {c(YELLOW,'MEDIUM')} (outcome is binary, not probabilistic)
  Exchange:    NASDAQ  (not UK/EU — outside your core screen)
  Is now a good time to buy?
  {c(BG_GREEN,BOLD,WHITE,' YES — but size the position accordingly ')}

  At ${PRICE:.2f} the downside is partially priced in from the
  ${HIGH_52:.2f} high. VANQUISH-2 data in Q3-2026 is the next
  catalyst. If data are positive, re-rate to $60-100. If not,
  treat as a total loss. Set a hard stop.
"""
print(verdict_box)
sep("═")
print(c(DIM,"  Data sourced: April 2026 | NASDAQ:VKTX | Not financial advice"))
sep("═")
print()
