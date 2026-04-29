package com.investmentapp.engine

import com.investmentapp.data.model.ConfidenceLevel
import com.investmentapp.data.model.RecommendedStock
import com.investmentapp.data.model.StockData

/**
 * Scores each stock against the user's investment criteria:
 *   - High-medium risk
 *   - 5-year horizon
 *   - Target >20-25% growth
 *   - UK + European markets
 *
 * Maximum raw score = 100 points
 */
class RecommendationEngine {

    fun rankStocks(stocks: List<StockData>): List<RecommendedStock> =
        stocks
            .map { evaluate(it) }
            .filter { it.score >= 30 }           // floor — don't surface junk
            .sortedByDescending { it.score }

    private fun evaluate(stock: StockData): RecommendedStock {
        val reasons = mutableListOf<String>()
        val cautions = mutableListOf<String>()
        var score = 0

        // ── Valuation (20 pts) ────────────────────────────────────────────────
        if (stock.isCheap) {
            score += 12
            reasons += "Attractive P/E ratio (${String.format("%.1f", stock.peRatio)}x)"
        }
        if (stock.priceToBook in 0.5..4.0) {
            score += 8
            reasons += "Reasonable price-to-book (${String.format("%.1f", stock.priceToBook)}x)"
        }

        // ── Growth (25 pts) ───────────────────────────────────────────────────
        if (stock.isRevenueGrowing) {
            val pts = when {
                stock.revenueGrowthPct >= 25 -> 15
                stock.revenueGrowthPct >= 15 -> 10
                else -> 5
            }
            score += pts
            reasons += "Revenue growing ${String.format("%.1f", stock.revenueGrowthPct)}% YoY"
        } else {
            cautions += "Revenue not growing"
        }

        if (stock.areProfitsRising) {
            val pts = when {
                stock.profitGrowthPct >= 25 -> 10
                stock.profitGrowthPct >= 10 -> 6
                else -> 3
            }
            score += pts
            reasons += "Pre-tax profit up ${String.format("%.1f", stock.profitGrowthPct)}%"
        } else {
            cautions += "Profits not rising"
        }

        // ── Price action (15 pts) ─────────────────────────────────────────────
        if (stock.isPriceLow) {
            score += 8
            reasons += "Price near 52-week low — potential value entry"
        }
        if (stock.isPriceTrendingUp) {
            score += 7
            reasons += "Short-term price trend is positive"
        } else if (!stock.isPriceLow) {
            cautions += "Price not trending up"
        }

        // ── Chart trend (10 pts) ──────────────────────────────────────────────
        if (stock.isChartTrendingUp) {
            score += 10
            reasons += "1-year chart trend positive (+${String.format("%.1f", stock.fullYearPerformancePct)}%)"
        } else {
            cautions += "Annual chart trend is negative"
        }

        // ── Dividends (10 pts) ────────────────────────────────────────────────
        if (stock.areDividendsRising) {
            val pts = if (stock.dividendYield >= 4.0) 10 else 6
            score += pts
            reasons += "Dividends rising; current yield ${String.format("%.1f", stock.dividendYield)}%"
        }

        // ── Balance sheet (10 pts) ────────────────────────────────────────────
        if (stock.isDebtReasonable) {
            score += 10
            reasons += "Healthy debt: net debt/profit ${String.format("%.1f", stock.netDebtToProfit)}x"
        } else {
            cautions += "Elevated debt levels (D/E ${String.format("%.1f", stock.debtToEquity)})"
        }

        // ── Quality (10 pts) ──────────────────────────────────────────────────
        if (stock.returnOnEquity >= 15) {
            score += 6
            reasons += "Strong ROE: ${String.format("%.1f", stock.returnOnEquity)}%"
        }
        if (stock.operatingCashFlow > 0) {
            score += 4
            reasons += "Positive operating cash flow"
        }

        // ── Analyst / Outlook (bonus, up to 10 pts) ───────────────────────────
        if (stock.analystConsensus == "BUY") {
            score += 6
            reasons += "Analyst consensus: BUY (target ${stock.currency} ${stock.analystTargetPrice})"
        }
        if (stock.upside >= 20) {
            score += 4
            reasons += "Analyst upside ${String.format("%.0f", stock.upside)}% to target"
        }

        // ── Negative penalty ─────────────────────────────────────────────────
        if (stock.hasNegativeIssues) {
            score -= 10
            stock.negativeFlags.split(",").forEach { cautions += it.trim() }
        }

        score = score.coerceIn(0, 100)

        val confidence = when {
            score >= 70 -> ConfidenceLevel.HIGH
            score >= 45 -> ConfidenceLevel.MEDIUM
            else -> ConfidenceLevel.LOW
        }

        val isGoodBuy = score >= 55 && !stock.hasNegativeIssues
        val aiText = buildAiRecommendation(stock, score, isGoodBuy, reasons, cautions)

        return RecommendedStock(
            stock = stock,
            score = score,
            aiRecommendation = aiText,
            isGoodTimeToBuy = isGoodBuy,
            buyReasons = reasons,
            cautionPoints = cautions,
            confidenceLevel = confidence
        )
    }

    private fun buildAiRecommendation(
        stock: StockData,
        score: Int,
        isGoodBuy: Boolean,
        reasons: List<String>,
        cautions: List<String>
    ): String {
        val verdict = when {
            isGoodBuy && score >= 70 -> "STRONG BUY"
            isGoodBuy -> "BUY"
            score >= 40 -> "WATCH"
            else -> "AVOID"
        }

        val horizon = "Over a 5-year horizon with a high-medium risk appetite"
        val growthNote = if (stock.revenueGrowthPct >= 20)
            "${stock.companyName} demonstrates the >20% growth threshold you seek."
        else
            "${stock.companyName} shows measured growth that may compound well over 5 years."

        val debtNote = if (stock.isDebtReasonable)
            "Balance sheet is clean, supporting resilience through market cycles."
        else
            "Elevated debt requires monitoring — watch refinancing risk."

        return "[$verdict] $horizon, $growthNote $debtNote " +
                "Score: $score/100. " +
                (if (isGoodBuy) "Now looks like a good entry point." else "Wait for better conditions.")
    }
}
