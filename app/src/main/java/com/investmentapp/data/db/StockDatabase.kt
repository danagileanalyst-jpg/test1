package com.investmentapp.data.db

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.investmentapp.data.model.StockData

@Database(entities = [StockData::class], version = 1, exportSchema = false)
abstract class StockDatabase : RoomDatabase() {

    abstract fun stockDao(): StockDao

    companion object {
        @Volatile private var INSTANCE: StockDatabase? = null

        fun getInstance(context: Context): StockDatabase =
            INSTANCE ?: synchronized(this) {
                Room.databaseBuilder(context.applicationContext, StockDatabase::class.java, "investment_db")
                    .fallbackToDestructiveMigration()
                    .build()
                    .also { INSTANCE = it }
            }
    }
}
