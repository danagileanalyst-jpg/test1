package com.investmentapp.data.repository

import android.content.Context
import com.investmentapp.data.api.RetrofitClient
import com.investmentapp.data.db.StockDatabase
import com.investmentapp.data.model.StockData
import com.investmentapp.engine.RecommendationEngine
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class StockRepository(private val context: Context) {

    private val dao = StockDatabase.getInstance(context).stockDao()
    private val api = RetrofitClient.create("https://www.alphavantage.co/")
    private val engine = RecommendationEngine()

    // European + UK watchlist — extend as needed
    private val watchlist = listOf(
        // UK (LSE)
        "AZN.LON", "HSBA.LON", "BP.LON", "GSK.LON", "ULVR.LON",
        "RIO.LON", "BA.LON", "VOD.LON", "LLOY.LON", "BARC.LON",
        "BT-A.LON", "SHEL.LON", "DGE.LON", "EXPN.LON", "LGEN.LON",
        // Europe (EURONEXT / XETRA)
        "ASML.AMS", "SAP.ETR", "SIE.ETR", "ADS.ETR", "BMW.ETR",
        "DTE.ETR", "ALV.ETR", "BNP.PAR", "MC.PAR", "OR.PAR",
        "SAN.MAD", "INGA.AMS", "PHIA.AMS", "RNO.PAR", "VOW3.ETR"
    )

    val allStocksLive = dao.getAllStocks()

    suspend fun refreshAll(): Result<List<StockData>> = withContext(Dispatchers.IO) {
        return@withContext try {
            val stocks = getSampleEuropeanStocks()   // swap for real API calls
            dao.insertStocks(stocks)
            Result.success(stocks)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getTopRecommendations(limit: Int = 5) = withContext(Dispatchers.IO) {
        val stocks = dao.getRecentStocks(50).ifEmpty { getSampleEuropeanStocks() }
        engine.rankStocks(stocks).take(limit)
    }

    // ---------------------------------------------------------------------------
    // Sample data — populated with realistic-looking but illustrative numbers.
    // Replace with live API fetch in production.
    // ---------------------------------------------------------------------------
    private fun getSampleEuropeanStocks(): List<StockData> = listOf(
        StockData(
            ticker = "AZN", companyName = "AstraZeneca PLC", sector = "Healthcare",
            description = "Global biopharmaceutical company focused on oncology, CVRM, and rare diseases.",
            exchange = "LSE", market = "UK", currency = "GBp",
            currentPrice = 10850.0, priceChangePct = 0.72,
            weekHigh52 = 12850.0, weekLow52 = 9420.0,
            marketCap = 168000.0, peRatio = 31.2, priceToBook = 5.8,
            returnOnEquity = 18.4, debtToEquity = 0.82, netDebtToProfit = 1.9,
            operatingCashFlow = 8200.0,
            fullYearRevenue = 45800.0, fullYearRevenuePrevious = 42700.0,
            fullYearPreTaxProfit = 6100.0, fullYearPreTaxProfitPrevious = 5200.0,
            dividendYield = 2.1, dividendPrevious = 1.9,
            nextStatementDate = "2025-05-08", fullYearPerformancePct = 8.3,
            analystConsensus = "BUY", analystTargetPrice = 12400.0,
            negativeFlags = ""
        ),
        StockData(
            ticker = "ASML", companyName = "ASML Holding NV", sector = "Technology",
            description = "World's sole supplier of EUV lithography machines for semiconductor manufacturing.",
            exchange = "EURONEXT", market = "Europe", currency = "EUR",
            currentPrice = 685.40, priceChangePct = 1.14,
            weekHigh52 = 1010.0, weekLow52 = 603.0,
            marketCap = 269000.0, peRatio = 28.6, priceToBook = 19.2,
            returnOnEquity = 51.7, debtToEquity = 0.31, netDebtToProfit = 0.4,
            operatingCashFlow = 7800.0,
            fullYearRevenue = 27900.0, fullYearRevenuePrevious = 21600.0,
            fullYearPreTaxProfit = 8100.0, fullYearPreTaxProfitPrevious = 6200.0,
            dividendYield = 1.2, dividendPrevious = 0.9,
            nextStatementDate = "2025-04-16", fullYearPerformancePct = -22.4,
            analystConsensus = "BUY", analystTargetPrice = 880.0,
            negativeFlags = ""
        ),
        StockData(
            ticker = "SAP", companyName = "SAP SE", sector = "Technology",
            description = "Europe's largest software company, leading enterprise ERP cloud transition.",
            exchange = "XETRA", market = "Europe", currency = "EUR",
            currentPrice = 218.50, priceChangePct = 0.45,
            weekHigh52 = 258.0, weekLow52 = 158.0,
            marketCap = 252000.0, peRatio = 41.0, priceToBook = 6.9,
            returnOnEquity = 16.3, debtToEquity = 0.45, netDebtToProfit = 1.2,
            operatingCashFlow = 5600.0,
            fullYearRevenue = 34500.0, fullYearRevenuePrevious = 30900.0,
            fullYearPreTaxProfit = 5300.0, fullYearPreTaxProfitPrevious = 3600.0,
            dividendYield = 1.0, dividendPrevious = 0.8,
            nextStatementDate = "2025-04-22", fullYearPerformancePct = 16.2,
            analystConsensus = "BUY", analystTargetPrice = 250.0,
            negativeFlags = ""
        ),
        StockData(
            ticker = "GSK", companyName = "GSK PLC", sector = "Healthcare",
            description = "UK pharma giant with strong vaccines and specialty medicines pipeline.",
            exchange = "LSE", market = "UK", currency = "GBp",
            currentPrice = 1512.0, priceChangePct = -0.22,
            weekHigh52 = 1850.0, weekLow52 = 1262.0,
            marketCap = 62000.0, peRatio = 12.1, priceToBook = 4.2,
            returnOnEquity = 32.1, debtToEquity = 1.12, netDebtToProfit = 2.1,
            operatingCashFlow = 5100.0,
            fullYearRevenue = 31400.0, fullYearRevenuePrevious = 29300.0,
            fullYearPreTaxProfit = 5400.0, fullYearPreTaxProfitPrevious = 4900.0,
            dividendYield = 4.1, dividendPrevious = 3.9,
            nextStatementDate = "2025-04-30", fullYearPerformancePct = -11.8,
            analystConsensus = "BUY", analystTargetPrice = 1800.0,
            negativeFlags = "Zantac litigation overhang"
        ),
        StockData(
            ticker = "EXPN", companyName = "Experian PLC", sector = "Financial Services",
            description = "Global data and technology company providing credit, fraud, and analytics services.",
            exchange = "LSE", market = "UK", currency = "USD",
            currentPrice = 38.50, priceChangePct = 0.68,
            weekHigh52 = 44.10, weekLow52 = 30.20,
            marketCap = 35000.0, peRatio = 33.8, priceToBook = 12.1,
            returnOnEquity = 34.6, debtToEquity = 0.95, netDebtToProfit = 1.7,
            operatingCashFlow = 1900.0,
            fullYearRevenue = 7000.0, fullYearRevenuePrevious = 6300.0,
            fullYearPreTaxProfit = 1380.0, fullYearPreTaxProfitPrevious = 1220.0,
            dividendYield = 1.5, dividendPrevious = 1.3,
            nextStatementDate = "2025-05-14", fullYearPerformancePct = 12.6,
            analystConsensus = "BUY", analystTargetPrice = 43.50,
            negativeFlags = ""
        ),
        StockData(
            ticker = "MC", companyName = "LVMH Moët Hennessy", sector = "Consumer Discretionary",
            description = "World's largest luxury goods conglomerate owning Louis Vuitton, Dior, and 75+ brands.",
            exchange = "EURONEXT", market = "Europe", currency = "EUR",
            currentPrice = 548.00, priceChangePct = -0.89,
            weekHigh52 = 830.0, weekLow52 = 488.0,
            marketCap = 274000.0, peRatio = 19.2, priceToBook = 3.4,
            returnOnEquity = 18.1, debtToEquity = 0.58, netDebtToProfit = 1.4,
            operatingCashFlow = 14200.0,
            fullYearRevenue = 84700.0, fullYearRevenuePrevious = 86200.0,
            fullYearPreTaxProfit = 15200.0, fullYearPreTaxProfitPrevious = 17200.0,
            dividendYield = 2.7, dividendPrevious = 2.4,
            nextStatementDate = "2025-04-14", fullYearPerformancePct = -30.1,
            analystConsensus = "HOLD", analystTargetPrice = 650.0,
            negativeFlags = "China slowdown impacting luxury demand, profit declined YoY"
        ),
        StockData(
            ticker = "SIE", companyName = "Siemens AG", sector = "Industrials",
            description = "German industrial giant in factory automation, smart infrastructure, and digital services.",
            exchange = "XETRA", market = "Europe", currency = "EUR",
            currentPrice = 186.00, priceChangePct = 0.52,
            weekHigh52 = 220.0, weekLow52 = 148.0,
            marketCap = 147000.0, peRatio = 16.8, priceToBook = 3.5,
            returnOnEquity = 21.2, debtToEquity = 0.61, netDebtToProfit = 0.8,
            operatingCashFlow = 8900.0,
            fullYearRevenue = 77800.0, fullYearRevenuePrevious = 75900.0,
            fullYearPreTaxProfit = 9200.0, fullYearPreTaxProfitPrevious = 8500.0,
            dividendYield = 2.8, dividendPrevious = 2.5,
            nextStatementDate = "2025-05-08", fullYearPerformancePct = 2.4,
            analystConsensus = "BUY", analystTargetPrice = 220.0,
            negativeFlags = ""
        ),
        StockData(
            ticker = "LGEN", companyName = "Legal & General Group", sector = "Insurance",
            description = "UK financial services leader in pensions, annuities, and investment management.",
            exchange = "LSE", market = "UK", currency = "GBp",
            currentPrice = 224.0, priceChangePct = 0.18,
            weekHigh52 = 275.0, weekLow52 = 186.0,
            marketCap = 13800.0, peRatio = 8.2, priceToBook = 1.1,
            returnOnEquity = 13.4, debtToEquity = 0.42, netDebtToProfit = 0.9,
            operatingCashFlow = 2200.0,
            fullYearRevenue = 9400.0, fullYearRevenuePrevious = 8800.0,
            fullYearPreTaxProfit = 1640.0, fullYearPreTaxProfitPrevious = 1510.0,
            dividendYield = 9.2, dividendPrevious = 8.8,
            nextStatementDate = "2025-06-04", fullYearPerformancePct = -4.1,
            analystConsensus = "BUY", analystTargetPrice = 280.0,
            negativeFlags = ""
        ),
        StockData(
            ticker = "ADS", companyName = "Adidas AG", sector = "Consumer Discretionary",
            description = "German sportswear giant recovering strongly after Ye/Yeezy partnership dissolution.",
            exchange = "XETRA", market = "Europe", currency = "EUR",
            currentPrice = 218.00, priceChangePct = 1.08,
            weekHigh52 = 278.0, weekLow52 = 174.0,
            marketCap = 38800.0, peRatio = 29.4, priceToBook = 5.1,
            returnOnEquity = 17.2, debtToEquity = 0.48, netDebtToProfit = 1.1,
            operatingCashFlow = 1600.0,
            fullYearRevenue = 23700.0, fullYearRevenuePrevious = 21400.0,
            fullYearPreTaxProfit = 1590.0, fullYearPreTaxProfitPrevious = 268.0,
            dividendYield = 1.2, dividendPrevious = 0.7,
            nextStatementDate = "2025-05-06", fullYearPerformancePct = 18.4,
            analystConsensus = "BUY", analystTargetPrice = 265.0,
            negativeFlags = ""
        ),
        StockData(
            ticker = "BARC", companyName = "Barclays PLC", sector = "Banking",
            description = "UK universal bank with strong investment banking and retail/commercial divisions.",
            exchange = "LSE", market = "UK", currency = "GBp",
            currentPrice = 286.0, priceChangePct = 0.35,
            weekHigh52 = 324.0, weekLow52 = 168.0,
            marketCap = 45200.0, peRatio = 7.4, priceToBook = 0.6,
            returnOnEquity = 9.2, debtToEquity = 2.8, netDebtToProfit = 2.2,
            operatingCashFlow = 8800.0,
            fullYearRevenue = 25400.0, fullYearRevenuePrevious = 22600.0,
            fullYearPreTaxProfit = 6400.0, fullYearPreTaxProfitPrevious = 5200.0,
            dividendYield = 3.4, dividendPrevious = 2.9,
            nextStatementDate = "2025-04-30", fullYearPerformancePct = 48.2,
            analystConsensus = "BUY", analystTargetPrice = 340.0,
            negativeFlags = ""
        )
    )
}
