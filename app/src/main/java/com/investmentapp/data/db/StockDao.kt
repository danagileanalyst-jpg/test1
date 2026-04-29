package com.investmentapp.data.db

import androidx.lifecycle.LiveData
import androidx.room.*
import com.investmentapp.data.model.StockData

@Dao
interface StockDao {

    @Query("SELECT * FROM stocks ORDER BY lastUpdated DESC")
    fun getAllStocks(): LiveData<List<StockData>>

    @Query("SELECT * FROM stocks WHERE ticker = :ticker LIMIT 1")
    suspend fun getStock(ticker: String): StockData?

    @Query("SELECT * FROM stocks WHERE market = :market ORDER BY lastUpdated DESC")
    suspend fun getStocksByMarket(market: String): List<StockData>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertStocks(stocks: List<StockData>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertStock(stock: StockData)

    @Delete
    suspend fun deleteStock(stock: StockData)

    @Query("DELETE FROM stocks")
    suspend fun clearAll()

    @Query("SELECT * FROM stocks ORDER BY lastUpdated DESC LIMIT :limit")
    suspend fun getRecentStocks(limit: Int = 20): List<StockData>
}
