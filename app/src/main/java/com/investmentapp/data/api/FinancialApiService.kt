package com.investmentapp.data.api

import com.investmentapp.data.model.StockData
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

// Retrofit interface — swap base URL and endpoints for your preferred provider
// (Alpha Vantage, Finnhub, Polygon.io, Yahoo Finance unofficial, etc.)
interface FinancialApiService {

    @GET("query")
    suspend fun getStockOverview(
        @Query("function") function: String = "OVERVIEW",
        @Query("symbol") symbol: String,
        @Query("apikey") apiKey: String
    ): Response<Map<String, Any>>

    @GET("query")
    suspend fun getGlobalQuote(
        @Query("function") function: String = "GLOBAL_QUOTE",
        @Query("symbol") symbol: String,
        @Query("apikey") apiKey: String
    ): Response<Map<String, Any>>

    @GET("query")
    suspend fun getIncomeStatement(
        @Query("function") function: String = "INCOME_STATEMENT",
        @Query("symbol") symbol: String,
        @Query("apikey") apiKey: String
    ): Response<Map<String, Any>>
}

data class ApiConfig(
    val baseUrl: String = "https://www.alphavantage.co/",
    val apiKey: String = BuildConfigHelper.ALPHA_VANTAGE_KEY
)

object BuildConfigHelper {
    // Set your API key in local.properties: ALPHA_VANTAGE_KEY=your_key_here
    const val ALPHA_VANTAGE_KEY = "demo"
}
