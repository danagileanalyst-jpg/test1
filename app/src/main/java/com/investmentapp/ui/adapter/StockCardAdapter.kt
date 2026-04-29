package com.investmentapp.ui.adapter

import android.graphics.Color
import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.investmentapp.data.model.ConfidenceLevel
import com.investmentapp.data.model.RecommendedStock
import com.investmentapp.databinding.ItemStockCardBinding
import java.text.NumberFormat
import java.util.Locale

class StockCardAdapter(
    private val onClick: (RecommendedStock) -> Unit
) : ListAdapter<RecommendedStock, StockCardAdapter.ViewHolder>(DiffCallback) {

    companion object DiffCallback : DiffUtil.ItemCallback<RecommendedStock>() {
        override fun areItemsTheSame(a: RecommendedStock, b: RecommendedStock) =
            a.stock.ticker == b.stock.ticker
        override fun areContentsTheSame(a: RecommendedStock, b: RecommendedStock) =
            a == b
    }

    inner class ViewHolder(private val binding: ItemStockCardBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(item: RecommendedStock, rank: Int) {
            val s = item.stock
            with(binding) {
                // Header
                tvRank.text = "#$rank"
                tvTicker.text = s.ticker
                tvCompanyName.text = s.companyName
                tvSector.text = "${s.sector} · ${s.exchange}"
                tvMarket.text = s.market

                // Price
                val fmt = NumberFormat.getNumberInstance(Locale.UK).apply { maximumFractionDigits = 2 }
                tvCurrentPrice.text = "${s.currency} ${fmt.format(s.currentPrice)}"
                val changeColor = if (s.priceChangePct >= 0) Color.parseColor("#00C853") else Color.parseColor("#D50000")
                val arrow = if (s.priceChangePct >= 0) "▲" else "▼"
                tvPriceChange.setTextColor(changeColor)
                tvPriceChange.text = "$arrow ${String.format("%.2f", Math.abs(s.priceChangePct))}%"

                // Score ring
                progressScore.progress = item.score
                tvScore.text = "${item.score}"

                // Confidence badge
                tvConfidence.text = item.confidenceLevel.label
                tvConfidence.setBackgroundColor(item.confidenceLevel.color)

                // Key metrics row
                tvPE.text = "P/E: ${String.format("%.1f", s.peRatio)}x"
                tvROE.text = "ROE: ${String.format("%.1f", s.returnOnEquity)}%"
                tvYield.text = "Yield: ${String.format("%.1f", s.dividendYield)}%"
                tvDebt.text = "D/E: ${String.format("%.1f", s.debtToEquity)}"

                // Buy signal chips
                chipRevGrowing.isChecked = s.isRevenueGrowing
                chipProfitRising.isChecked = s.areProfitsRising
                chipPriceLow.isChecked = s.isPriceLow
                chipDebtOk.isChecked = s.isDebtReasonable
                chipChartUp.isChecked = s.isChartTrendingUp
                chipDivRising.isChecked = s.areDividendsRising

                // AI summary
                tvAiRecommendation.text = item.aiRecommendation

                // Good time to buy indicator
                val buyColor = if (item.isGoodTimeToBuy) Color.parseColor("#00C853") else Color.parseColor("#FF6D00")
                tvBuySignal.setBackgroundColor(buyColor)
                tvBuySignal.text = if (item.isGoodTimeToBuy) "✓ GOOD TIME TO BUY" else "⏳ WAIT FOR BETTER ENTRY"

                // Next statement
                tvNextStatement.text = "Next results: ${s.nextStatementDate}"

                // 52-week range
                tv52Range.text = "52w: ${s.currency} ${fmt.format(s.weekLow52)} – ${fmt.format(s.weekHigh52)}"

                // Negatives
                if (s.hasNegativeIssues) {
                    tvNegatives.visibility = android.view.View.VISIBLE
                    tvNegatives.text = "⚠ ${s.negativeFlags}"
                } else {
                    tvNegatives.visibility = android.view.View.GONE
                }

                root.setOnClickListener { onClick(item) }
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemStockCardBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position), position + 1)
    }
}
