package com.investmentapp.ui.detail

import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.chip.Chip
import com.investmentapp.R
import com.investmentapp.data.model.RecommendedStock
import com.investmentapp.data.model.StockData
import com.investmentapp.databinding.ActivityStockDetailBinding
import com.investmentapp.engine.RecommendationEngine
import java.text.NumberFormat
import java.util.Locale
import kotlin.math.abs

class StockDetailActivity : AppCompatActivity() {

    private lateinit var binding: ActivityStockDetailBinding

    companion object {
        private const val EXTRA_TICKER = "extra_ticker"

        fun start(context: Context, rec: RecommendedStock) {
            val intent = Intent(context, StockDetailActivity::class.java).apply {
                putExtra(EXTRA_TICKER, rec.stock.ticker)
                // In production: pass via shared ViewModel or parcelable
            }
            context.startActivity(intent)
        }

        // Called from adapter — we store the last-viewed rec in a companion cache
        private val recCache = mutableMapOf<String, RecommendedStock>()
        fun cache(rec: RecommendedStock) { recCache[rec.stock.ticker] = rec }
        fun getCached(ticker: String) = recCache[ticker]
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityStockDetailBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        val ticker = intent.getStringExtra(EXTRA_TICKER) ?: return
        val rec = getCached(ticker) ?: return

        populateDetail(rec)
    }

    private fun populateDetail(rec: RecommendedStock) {
        val s = rec.stock
        val fmt = NumberFormat.getNumberInstance(Locale.UK).apply { maximumFractionDigits = 2 }

        with(binding) {
            // Header
            supportActionBar?.title = s.companyName
            tvTicker.text = s.ticker
            tvExchange.text = "${s.exchange} · ${s.market}"
            tvSector.text = s.sector
            tvDescription.text = s.description

            // Price block
            tvPrice.text = "${s.currency} ${fmt.format(s.currentPrice)}"
            val changeColor = if (s.priceChangePct >= 0) Color.parseColor("#00C853") else Color.parseColor("#D50000")
            tvDailyChange.setTextColor(changeColor)
            tvDailyChange.text = "${if (s.priceChangePct >= 0) "▲" else "▼"} ${String.format("%.2f", abs(s.priceChangePct))}%"

            // Score
            progressScore.progress = rec.score
            tvScoreValue.text = "${rec.score}/100"
            tvConfidence.text = rec.confidenceLevel.label
            tvConfidence.setBackgroundColor(rec.confidenceLevel.color)

            // AI Recommendation
            tvAiText.text = rec.aiRecommendation
            val buyColor = if (rec.isGoodTimeToBuy) Color.parseColor("#00C853") else Color.parseColor("#FF6D00")
            tvBuySignal.setBackgroundColor(buyColor)
            tvBuySignal.text = if (rec.isGoodTimeToBuy) "✓ GOOD TIME TO BUY" else "⏳ WAIT"

            // Fundamentals grid
            tvCurrentPriceVal.text = "${s.currency} ${fmt.format(s.currentPrice)}"
            tvLow52Val.text = "${s.currency} ${fmt.format(s.weekLow52)}"
            tvHigh52Val.text = "${s.currency} ${fmt.format(s.weekHigh52)}"
            tvPriceLowVal.text = if (s.isPriceLow) "Yes ✓" else "No"
            tvPriceTrendVal.text = if (s.isPriceTrendingUp) "Upward ↑" else "Flat/Down ↓"
            tvMarketCapVal.text = "£${fmt.format(s.marketCap)}M"
            tvPEVal.text = "${String.format("%.1f", s.peRatio)}x"
            tvPBVal.text = "${String.format("%.1f", s.priceToBook)}x"
            tvROEVal.text = "${String.format("%.1f", s.returnOnEquity)}%"
            tvDebtEquityVal.text = "${String.format("%.2f", s.debtToEquity)}"
            tvNetDebtVal.text = "${String.format("%.1f", s.netDebtToProfit)}x profit"
            tvDebtReasonableVal.text = if (s.isDebtReasonable) "Yes ✓" else "No ✗"
            tvOCFVal.text = "${fmt.format(s.operatingCashFlow)}M"

            tvRevenueVal.text = "${fmt.format(s.fullYearRevenue)}M"
            tvRevGrowthVal.text = "${String.format("%.1f", s.revenueGrowthPct)}%"
            tvRevGrowingVal.text = if (s.isRevenueGrowing) "Yes ✓" else "No ✗"
            tvProfitVal.text = "${fmt.format(s.fullYearPreTaxProfit)}M"
            tvProfitGrowthVal.text = "${String.format("%.1f", s.profitGrowthPct)}%"
            tvProfitsRisingVal.text = if (s.areProfitsRising) "Yes ✓" else "No ✗"

            tvDivYieldVal.text = "${String.format("%.1f", s.dividendYield)}%"
            tvDivRisingVal.text = if (s.areDividendsRising) "Yes ✓" else "No ✗"

            tvNextStatementVal.text = s.nextStatementDate
            tv1YrPerfVal.text = "${String.format("%.1f", s.fullYearPerformancePct)}%"
            tvChartUpVal.text = if (s.isChartTrendingUp) "Yes ↗" else "No ↘"
            tvOutlookVal.text = s.analystConsensus
            tvTargetVal.text = "${s.currency} ${fmt.format(s.analystTargetPrice)} (${String.format("%.0f", s.upside)}% upside)"
            tvCheapVal.text = if (s.isCheap) "Yes ✓" else "No ✗"

            tvNegativesVal.text = if (s.hasNegativeIssues) s.negativeFlags else "None identified"

            // Buy reasons chips
            rec.buyReasons.forEach { reason ->
                val chip = Chip(this@StockDetailActivity).apply {
                    text = reason
                    isCheckable = false
                    setChipBackgroundColorResource(R.color.chip_positive_bg)
                    setTextColor(Color.WHITE)
                }
                chipGroupReasons.addView(chip)
            }

            rec.cautionPoints.forEach { caution ->
                val chip = Chip(this@StockDetailActivity).apply {
                    text = caution
                    isCheckable = false
                    setChipBackgroundColorResource(R.color.chip_caution_bg)
                    setTextColor(Color.WHITE)
                }
                chipGroupCautions.addView(chip)
            }
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressedDispatcher.onBackPressed()
        return true
    }
}
