#!/usr/bin/env python3
"""
Investment Advisor — Daily Simulation
Mirrors the Kotlin RecommendationEngine and StockRepository exactly.
"""

import time
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Optional

# ── ANSI colours ────────────────────────────────────────────────────────────
R  = "\033[0m"
BOLD = "\033[1m"
DIM  = "\033[2m"
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
BG_BLUE   = "\033[44m"
BG_GREEN  = "\033[42m"
BG_RED    = "\033[41m"
BG_YELLOW = "\033[43m"
BG_DARK   = "\033[40m"

def clr(text, *codes): return "".join(codes) + str(text) + R
def bar(n, total=100, width=20):
    filled = int(width * n / total)
    return clr("█" * filled, GREEN) + clr("░" * (width - filled), DIM)

# ── Data model ───────────────────────────────────────────────────────────────
@dataclass
class Stock:
    ticker: str
    company: str
    sector: str
    description: str
    exchange: str
    market: str
    currency: str
    price: float
    price_chg_pct: float
    high_52: float
    low_52: float
    market_cap: float       # £M
    pe: float
    pb: float
    roe: float
    debt_equity: float
    net_debt_profit: float
    ocf: float              # £M
    revenue: float          # £M
    revenue_prev: float
    profit: float           # £M
    profit_prev: float
    div_yield: float
    div_prev: float
    next_statement: str
    perf_1yr: float
    analyst: str
    target: float
    negatives: str = ""

    # ── computed ──
    @property
    def is_price_low(self):
        return self.price <= self.low_52 + (self.high_52 - self.low_52) * 0.35

    @property
    def is_trending_up(self):
        return self.price_chg_pct > 0 and self.perf_1yr > 0

    @property
    def is_cheap(self):
        return 1.0 <= self.pe <= 18.0

    @property
    def rev_growing(self):
        return self.revenue_prev > 0 and self.revenue > self.revenue_prev

    @property
    def profits_rising(self):
        return self.profit_prev > 0 and self.profit > self.profit_prev

    @property
    def divs_rising(self):
        return self.div_prev > 0 and self.div_yield > 0

    @property
    def debt_ok(self):
        return self.net_debt_profit < 3.0 and self.debt_equity < 1.5

    @property
    def chart_up(self):
        return self.perf_1yr > 0

    @property
    def rev_growth_pct(self):
        if self.revenue_prev <= 0: return 0.0
        return ((self.revenue - self.revenue_prev) / self.revenue_prev) * 100

    @property
    def profit_growth_pct(self):
        if self.profit_prev <= 0: return 0.0
        return ((self.profit - self.profit_prev) / self.profit_prev) * 100

    @property
    def upside(self):
        if self.price <= 0 or self.target <= 0: return 0.0
        return ((self.target - self.price) / self.price) * 100

    @property
    def has_negatives(self):
        return bool(self.negatives.strip())

@dataclass
class Recommendation:
    stock: Stock
    score: int
    ai_text: str
    good_to_buy: bool
    reasons: List[str]
    cautions: List[str]
    confidence: str   # HIGH / MEDIUM / LOW

# ── Scoring engine ───────────────────────────────────────────────────────────
def evaluate(s: Stock) -> Recommendation:
    reasons, cautions, score = [], [], 0

    # Valuation (20 pts)
    if s.is_cheap:
        score += 12
        reasons.append(f"Attractive P/E ratio ({s.pe:.1f}x)")
    if 0.5 <= s.pb <= 4.0:
        score += 8
        reasons.append(f"Reasonable price-to-book ({s.pb:.1f}x)")

    # Growth (25 pts)
    if s.rev_growing:
        pts = 15 if s.rev_growth_pct >= 25 else 10 if s.rev_growth_pct >= 15 else 5
        score += pts
        reasons.append(f"Revenue growing {s.rev_growth_pct:.1f}% YoY")
    else:
        cautions.append("Revenue not growing")

    if s.profits_rising:
        pts = 10 if s.profit_growth_pct >= 25 else 6 if s.profit_growth_pct >= 10 else 3
        score += pts
        reasons.append(f"Pre-tax profit up {s.profit_growth_pct:.1f}%")
    else:
        cautions.append("Profits not rising")

    # Price action (15 pts)
    if s.is_price_low:
        score += 8
        reasons.append("Price near 52-week low — potential value entry")
    if s.is_trending_up:
        score += 7
        reasons.append("Short-term price trend is positive")
    elif not s.is_price_low:
        cautions.append("Price not trending up")

    # Chart trend (10 pts)
    if s.chart_up:
        score += 10
        reasons.append(f"1-year chart trend positive (+{s.perf_1yr:.1f}%)")
    else:
        cautions.append("Annual chart trend is negative")

    # Dividends (10 pts)
    if s.divs_rising:
        pts = 10 if s.div_yield >= 4.0 else 6
        score += pts
        reasons.append(f"Dividends rising; yield {s.div_yield:.1f}%")

    # Balance sheet (10 pts)
    if s.debt_ok:
        score += 10
        reasons.append(f"Healthy debt: net debt/profit {s.net_debt_profit:.1f}x")
    else:
        cautions.append(f"Elevated debt (D/E {s.debt_equity:.1f})")

    # Quality (10 pts)
    if s.roe >= 15:
        score += 6
        reasons.append(f"Strong ROE: {s.roe:.1f}%")
    if s.ocf > 0:
        score += 4
        reasons.append("Positive operating cash flow")

    # Analyst / outlook (bonus 10 pts)
    if s.analyst == "BUY":
        score += 6
        reasons.append(f"Analyst consensus: BUY (target {s.currency} {s.target:,.0f})")
    if s.upside >= 20:
        score += 4
        reasons.append(f"Analyst upside {s.upside:.0f}% to target")

    # Negatives penalty
    if s.has_negatives:
        score -= 10
        for flag in s.negatives.split(","):
            cautions.append(flag.strip())

    score = max(0, min(100, score))

    confidence = "HIGH" if score >= 70 else "MEDIUM" if score >= 45 else "LOW"
    good_buy = score >= 55 and not s.has_negatives

    verdict = "STRONG BUY" if (good_buy and score >= 70) else "BUY" if good_buy else "WATCH" if score >= 40 else "AVOID"
    horizon = "Over a 5-year horizon with a high-medium risk appetite"
    growth_note = (f"{s.company} demonstrates the >20% growth threshold you seek."
                   if s.rev_growth_pct >= 20 else
                   f"{s.company} shows measured growth that may compound well over 5 years.")
    debt_note = ("Balance sheet is clean, supporting resilience through market cycles."
                 if s.debt_ok else
                 "Elevated debt requires monitoring — watch refinancing risk.")
    buy_note = "Now looks like a good entry point." if good_buy else "Wait for better conditions."
    ai_text = f"[{verdict}] {horizon}, {growth_note} {debt_note} Score: {score}/100. {buy_note}"

    return Recommendation(s, score, ai_text, good_buy, reasons, cautions, confidence)

# ── Stock universe ───────────────────────────────────────────────────────────
STOCKS = [
    Stock("AZN","AstraZeneca PLC","Healthcare",
          "Global biopharmaceutical focused on oncology, CVRM and rare diseases.",
          "LSE","UK","GBp",10850,0.72,12850,9420,168000,31.2,5.8,18.4,0.82,1.9,8200,
          45800,42700,6100,5200,2.1,1.9,"2025-05-08",8.3,"BUY",12400),
    Stock("ASML","ASML Holding NV","Technology",
          "World's sole supplier of EUV lithography machines for chip manufacturing.",
          "EURONEXT","Europe","EUR",685.4,1.14,1010,603,269000,28.6,19.2,51.7,0.31,0.4,7800,
          27900,21600,8100,6200,1.2,0.9,"2025-04-16",-22.4,"BUY",880),
    Stock("SAP","SAP SE","Technology",
          "Europe's largest software company leading enterprise ERP cloud transition.",
          "XETRA","Europe","EUR",218.5,0.45,258,158,252000,41.0,6.9,16.3,0.45,1.2,5600,
          34500,30900,5300,3600,1.0,0.8,"2025-04-22",16.2,"BUY",250),
    Stock("GSK","GSK PLC","Healthcare",
          "UK pharma giant with strong vaccines and specialty medicines pipeline.",
          "LSE","UK","GBp",1512,-0.22,1850,1262,62000,12.1,4.2,32.1,1.12,2.1,5100,
          31400,29300,5400,4900,4.1,3.9,"2025-04-30",-11.8,"BUY",1800,
          "Zantac litigation overhang"),
    Stock("EXPN","Experian PLC","Financial Services",
          "Global data and technology company providing credit, fraud and analytics.",
          "LSE","UK","USD",38.5,0.68,44.1,30.2,35000,33.8,12.1,34.6,0.95,1.7,1900,
          7000,6300,1380,1220,1.5,1.3,"2025-05-14",12.6,"BUY",43.5),
    Stock("MC","LVMH Moët Hennessy","Consumer Discretionary",
          "World's largest luxury goods conglomerate — Louis Vuitton, Dior and 75+ brands.",
          "EURONEXT","Europe","EUR",548,-0.89,830,488,274000,19.2,3.4,18.1,0.58,1.4,14200,
          84700,86200,15200,17200,2.7,2.4,"2025-04-14",-30.1,"HOLD",650,
          "China slowdown impacting luxury demand, profit declined YoY"),
    Stock("SIE","Siemens AG","Industrials",
          "German industrial giant in factory automation, smart infrastructure and digital services.",
          "XETRA","Europe","EUR",186,0.52,220,148,147000,16.8,3.5,21.2,0.61,0.8,8900,
          77800,75900,9200,8500,2.8,2.5,"2025-05-08",2.4,"BUY",220),
    Stock("LGEN","Legal & General Group","Insurance",
          "UK financial services leader in pensions, annuities and investment management.",
          "LSE","UK","GBp",224,0.18,275,186,13800,8.2,1.1,13.4,0.42,0.9,2200,
          9400,8800,1640,1510,9.2,8.8,"2025-06-04",-4.1,"BUY",280),
    Stock("ADS","Adidas AG","Consumer Discretionary",
          "German sportswear giant recovering strongly post-Yeezy dissolution.",
          "XETRA","Europe","EUR",218,1.08,278,174,38800,29.4,5.1,17.2,0.48,1.1,1600,
          23700,21400,1590,268,1.2,0.7,"2025-05-06",18.4,"BUY",265),
    Stock("BARC","Barclays PLC","Banking",
          "UK universal bank with strong investment banking and retail/commercial divisions.",
          "LSE","UK","GBp",286,0.35,324,168,45200,7.4,0.6,9.2,2.8,2.2,8800,
          25400,22600,6400,5200,3.4,2.9,"2025-04-30",48.2,"BUY",340),
]

# ── Display helpers ──────────────────────────────────────────────────────────
def score_colour(n):
    if n >= 70: return GREEN
    if n >= 45: return YELLOW
    return RED

def confidence_badge(c):
    if c == "HIGH":   return clr(" HIGH CONFIDENCE ", BG_GREEN, BOLD)
    if c == "MEDIUM": return clr(" MEDIUM CONFIDENCE ", BG_YELLOW, BOLD)
    return clr(" LOW CONFIDENCE ", BG_RED, BOLD)

def tick(v): return clr("✓", GREEN) if v else clr("✗", RED)

def fmt_price(s: Stock):
    arrow = clr("▲", GREEN) if s.price_chg_pct >= 0 else clr("▼", RED)
    chg   = clr(f"{abs(s.price_chg_pct):.2f}%", GREEN if s.price_chg_pct >= 0 else RED)
    return f"{s.currency} {s.price:,.2f}  {arrow} {chg}"

def separator(char="─", width=72):
    print(clr(char * width, DIM))

def print_header():
    width = 72
    print()
    print(clr("█" * width, BLUE))
    print(clr("█" + " " * (width-2) + "█", BLUE))
    title = "  INVESTMENT ADVISOR  —  DAILY PRE-MARKET REPORT"
    subtitle = "  UK & European Markets  |  High-Medium Risk  |  5-Year Horizon"
    print(clr("█", BLUE) + clr(title.ljust(width-2), BOLD, WHITE) + clr("█", BLUE))
    print(clr("█", BLUE) + clr(subtitle.ljust(width-2), CYAN) + clr("█", BLUE))
    now = datetime.now()
    market_open = now.replace(hour=8, minute=0, second=0)
    alert_time  = now.replace(hour=7, minute=0, second=0)
    dateline = f"  {now.strftime('%A, %-d %B %Y')}  |  Alert: 07:00 GMT  |  LSE opens: 08:00 GMT"
    print(clr("█", BLUE) + clr(dateline.ljust(width-2), DIM, WHITE) + clr("█", BLUE))
    print(clr("█" + " " * (width-2) + "█", BLUE))
    print(clr("█" * width, BLUE))
    print()

def print_card(rank: int, rec: Recommendation):
    s = rec.stock
    sc = rec.score
    col = score_colour(sc)
    width = 72

    separator("═")
    # Rank + ticker + company
    rank_str  = clr(f" #{rank} ", BG_BLUE, BOLD, WHITE)
    tick_str  = clr(f" {s.ticker} ", BOLD, BLUE)
    name_str  = clr(s.company, BOLD)
    score_str = clr(f" {sc}/100 ", col, BOLD)
    print(f"{rank_str} {tick_str} {name_str}  {score_str}")

    # Score bar
    print(f"     Score  {bar(sc)}  {confidence_badge(rec.confidence)}")

    # Sector + exchange + market
    print(f"     {clr(s.sector, CYAN)}  ·  {clr(s.exchange, DIM)}  ·  {clr(s.market, DIM)}")
    print()

    # Price row
    print(f"  {'Current Price':<22} {fmt_price(s)}")
    chg_colour = GREEN if s.perf_1yr >= 0 else RED
    print(f"  {'1-Year Performance':<22} {clr(f'{s.perf_1yr:+.1f}%', chg_colour)}")
    print(f"  {'52-Week Range':<22} {s.currency} {s.low_52:,.0f}  —  {s.currency} {s.high_52:,.0f}")
    print(f"  {'Is price low?':<22} {tick(s.is_price_low)}  {'Is price trending up?' :<22} {tick(s.is_trending_up)}")
    print()

    # Fundamentals grid
    print(f"  {'Market Cap':<22} {s.currency} {s.market_cap:,.0f}M")
    print(f"  {'P/E Ratio':<22} {s.pe:.1f}x   {'Is it cheap?' :<20} {tick(s.is_cheap)}")
    print(f"  {'Price-to-Book':<22} {s.pb:.1f}x")
    print(f"  {'Return on Equity':<22} {s.roe:.1f}%")
    print()

    # Revenue / profit
    rev_arrow  = clr("↑", GREEN) if s.rev_growing    else clr("↓", RED)
    prof_arrow = clr("↑", GREEN) if s.profits_rising else clr("↓", RED)
    print(f"  {'Full-Year Revenue':<22} {s.currency} {s.revenue:,.0f}M  {rev_arrow}  {clr(f'{s.rev_growth_pct:+.1f}%', GREEN if s.rev_growing else RED)}  {'Revenue growing?' :<20} {tick(s.rev_growing)}")
    print(f"  {'Pre-Tax Profit':<22} {s.currency} {s.profit:,.0f}M  {prof_arrow}  {clr(f'{s.profit_growth_pct:+.1f}%', GREEN if s.profits_rising else RED)}  {'Profits rising?' :<20} {tick(s.profits_rising)}")
    print(f"  {'Operating Cash Flow':<22} {s.currency} {s.ocf:,.0f}M")
    print()

    # Dividends + debt
    print(f"  {'Dividend Yield':<22} {s.div_yield:.1f}%   {'Dividends rising?':<20} {tick(s.divs_rising)}")
    print(f"  {'Debt-to-Equity':<22} {s.debt_equity:.2f}   {'Net Debt < 3x Profit?':<20} {tick(s.net_debt_profit < 3.0)}")
    print(f"  {'Net Debt / Profit':<22} {s.net_debt_profit:.1f}x  {'Debt reasonable?':<20} {tick(s.debt_ok)}")
    print()

    # Chart + statement
    print(f"  {'Chart (right > left)?':<22} {tick(s.chart_up)}")
    print(f"  {'Next Statement':<22} {clr(s.next_statement, YELLOW)}")
    print(f"  {'Analyst Consensus':<22} {clr(s.analyst, GREEN if s.analyst=='BUY' else YELLOW)}   Target: {s.currency} {s.target:,.0f}  ({clr(f'{s.upside:+.0f}%', GREEN if s.upside>0 else RED)} upside)")
    print()

    # Negatives
    if s.has_negatives:
        print(f"  {clr('⚠  ' + s.negatives, YELLOW)}")
        print()

    # AI recommendation
    verdict_col = BG_GREEN if rec.good_to_buy else BG_YELLOW
    buy_label   = " ✓  GOOD TIME TO BUY " if rec.good_to_buy else " ⏳ WAIT FOR BETTER ENTRY "
    print(f"  {clr(buy_label, verdict_col, BOLD, WHITE)}")
    print()
    # Wrap AI text
    ai_words = rec.ai_text.split()
    line, lines = [], []
    for w in ai_words:
        if len(" ".join(line + [w])) > 66:
            lines.append(" ".join(line))
            line = [w]
        else:
            line.append(w)
    if line: lines.append(" ".join(line))
    for l in lines:
        print(f"  {clr(l, DIM)}")
    print()

    # Buy reasons
    print(f"  {clr('Buy signals:', GREEN, BOLD)}")
    for r in rec.reasons:
        print(f"    {clr('✓', GREEN)}  {r}")
    if rec.cautions:
        print(f"  {clr('Cautions:', YELLOW, BOLD)}")
        for c in rec.cautions:
            print(f"    {clr('⚠', YELLOW)}  {c}")

def print_notification_preview(top5):
    print()
    separator("─")
    print(clr("  📱  NOTIFICATION PREVIEW  (sent at 07:00 GMT)", BOLD, CYAN))
    separator("─")
    print(clr("  Today's Top 5 Investment Picks", BOLD))
    summary = "  " + "  •  ".join(f"{r.stock.ticker} ({r.score}/100)" for r in top5)
    print(clr(summary, WHITE))
    separator("─")
    print()

def print_summary_table(recs):
    print()
    separator("═")
    print(clr("  RANKED SUMMARY — ALL SCORED STOCKS", BOLD, WHITE))
    separator("─")
    header = f"  {'#':<3}  {'Ticker':<6}  {'Company':<26}  {'Mkt':<6}  {'Score':>5}  {'Conf.':<8}  {'Buy?'}"
    print(clr(header, DIM))
    separator("─")
    for i, rec in enumerate(recs, 1):
        s = rec.stock
        col = score_colour(rec.score)
        conf_short = rec.confidence[:3]
        buy = clr("YES", GREEN, BOLD) if rec.good_to_buy else clr("NO ", RED)
        ticker_padded = clr(s.ticker, col) + " " * max(0, 6 - len(s.ticker))
        print(f"  {i:<3}  {ticker_padded}  {s.company:<26}  {s.market:<6}  "
              f"{clr(str(rec.score).rjust(3), col)}{'':2}  {conf_short:<8}  {buy}")
    separator("═")

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print_header()

    print(clr("  Scoring universe of stocks against your criteria...", DIM))
    all_recs = []
    for i, s in enumerate(STOCKS):
        sys.stdout.write(f"\r  [{i+1}/{len(STOCKS)}] Evaluating {s.ticker}...    ")
        sys.stdout.flush()
        time.sleep(0.12)
        all_recs.append(evaluate(s))
    sys.stdout.write("\r" + " " * 50 + "\r")

    all_recs.sort(key=lambda r: r.score, reverse=True)
    top5 = all_recs[:5]

    print_notification_preview(top5)

    print(clr(f"  TOP {min(5, len(all_recs))} RECOMMENDATIONS  (ranked by score)", BOLD, WHITE))
    print()
    for i, rec in enumerate(top5, 1):
        print_card(i, rec)
        time.sleep(0.05)

    if len(all_recs) > 5:
        print()
        separator("═")
        print(clr("  REMAINING STOCKS (outside top 5)", BOLD, WHITE))
        print_summary_table(all_recs[5:])

    print()
    print(clr("  Simulation complete.", GREEN, BOLD))
    print(clr(f"  Next live alert scheduled: tomorrow at 07:00 GMT", DIM))
    print()

if __name__ == "__main__":
    main()
