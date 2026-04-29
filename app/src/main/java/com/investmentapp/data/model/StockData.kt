package com.investmentapp.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "stocks")
data class StockData(
    @PrimaryKey val ticker: String,
    val companyName: String,
    val sector: String,
    val description: String,
    val exchange: String,                   // LSE, EURONEXT, XETRA, etc.
    val market: String,                     // UK, Europe
    val currentPrice: Double,
    val currency: String,
    val priceChangePct: Double,             // daily % change
    val weekHigh52: Double,
    val weekLow52: Double,
    val marketCap: Double,                  // in millions
    val peRatio: Double,
    val priceToBook: Double,
    val returnOnEquity: Double,             // percentage
    val debtToEquity: Double,
    val netDebtToProfit: Double,            // net debt / EBITDA
    val operatingCashFlow: Double,          // in millions
    val fullYearRevenue: Double,            // in millions
    val fullYearRevenuePrevious: Double,
    val fullYearPreTaxProfit: Double,       // in millions
    val fullYearPreTaxProfitPrevious: Double,
    val dividendYield: Double,              // percentage
    val dividendPrevious: Double,
    val nextStatementDate: String,          // ISO date string
    val fullYearPerformancePct: Double,     // 1-year price performance %
    val analystConsensus: String,           // BUY / HOLD / SELL
    val analystTargetPrice: Double,
    val negativeFlags: String,              // comma-separated negative news flags
    val lastUpdated: Long = System.currentTimeMillis()
) {
    val isPriceLow: Boolean
        get() = weekHigh52 > 0 && currentPrice <= weekLow52 + (weekHigh52 - weekLow52) * 0.35

    val isPriceTrendingUp: Boolean
        get() = priceChangePct > 0 && fullYearPerformancePct > 0

    val isCheap: Boolean
        get() = peRatio in 1.0..18.0

    val isRevenueGrowing: Boolean
        get() = fullYearRevenuePrevious > 0 && fullYearRevenue > fullYearRevenuePrevious

    val areProfitsRising: Boolean
        get() = fullYearPreTaxProfitPrevious > 0 && fullYearPreTaxProfit > fullYearPreTaxProfitPrevious

    val areDividendsRising: Boolean
        get() = dividendPrevious > 0 && dividendYield > 0

    val isDebtReasonable: Boolean
        get() = netDebtToProfit < 3.0 && debtToEquity < 1.5

    val isChartTrendingUp: Boolean
        get() = fullYearPerformancePct > 0

    val hasNegativeIssues: Boolean
        get() = negativeFlags.isNotBlank()

    val revenueGrowthPct: Double
        get() = if (fullYearRevenuePrevious > 0)
            ((fullYearRevenue - fullYearRevenuePrevious) / fullYearRevenuePrevious) * 100.0
        else 0.0

    val profitGrowthPct: Double
        get() = if (fullYearPreTaxProfitPrevious > 0)
            ((fullYearPreTaxProfit - fullYearPreTaxProfitPrevious) / fullYearPreTaxProfitPrevious) * 100.0
        else 0.0

    val priceVs52WeekHighPct: Double
        get() = if (weekHigh52 > 0)
            ((currentPrice - weekHigh52) / weekHigh52) * 100.0
        else 0.0

    val upside: Double
        get() = if (currentPrice > 0 && analystTargetPrice > 0)
            ((analystTargetPrice - currentPrice) / currentPrice) * 100.0
        else 0.0
}

data class RecommendedStock(
    val stock: StockData,
    val score: Int,
    val aiRecommendation: String,
    val isGoodTimeToBuy: Boolean,
    val buyReasons: List<String>,
    val cautionPoints: List<String>,
    val confidenceLevel: ConfidenceLevel
)

enum class ConfidenceLevel(val label: String, val color: Int) {
    HIGH("High Confidence", 0xFF00C853.toInt()),
    MEDIUM("Medium Confidence", 0xFFFF6D00.toInt()),
    LOW("Low Confidence", 0xFFD50000.toInt())
}

data class MarketSummary(
    val date: String,
    val ukOpen: String = "08:00 GMT",
    val europeOpen: String = "08:00 CET",
    val nextAlertTime: String,
    val topRecommendations: List<RecommendedStock>
)
