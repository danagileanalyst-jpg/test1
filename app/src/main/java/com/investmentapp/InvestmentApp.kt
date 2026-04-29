package com.investmentapp

import android.app.Application
import com.investmentapp.worker.DailyRecommendationWorker

class InvestmentApp : Application() {
    override fun onCreate() {
        super.onCreate()
        DailyRecommendationWorker.schedulePeriodic(this)
    }
}
