package com.investmentapp.worker

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import androidx.core.app.NotificationCompat
import androidx.work.*
import com.investmentapp.R
import com.investmentapp.data.repository.StockRepository
import com.investmentapp.ui.main.MainActivity
import java.util.concurrent.TimeUnit
import java.util.Calendar

class DailyRecommendationWorker(
    private val context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    companion object {
        const val WORK_NAME = "daily_investment_recommendations"
        const val CHANNEL_ID = "investment_recommendations"
        const val NOTIFICATION_ID = 1001

        fun schedule(context: Context) {
            val delay = minutesUntilMarketAlertTime()
            val request = OneTimeWorkRequestBuilder<DailyRecommendationWorker>()
                .setInitialDelay(delay, TimeUnit.MINUTES)
                .setConstraints(
                    Constraints.Builder()
                        .setRequiredNetworkType(NetworkType.CONNECTED)
                        .build()
                )
                .build()

            WorkManager.getInstance(context).enqueueUniqueWork(
                WORK_NAME,
                ExistingWorkPolicy.REPLACE,
                request
            )
        }

        fun schedulePeriodic(context: Context) {
            // Daily repeat — fires every 24h, each run reschedules itself for
            // the correct time (1 hour before UK/EU market open = 07:00 GMT)
            val request = PeriodicWorkRequestBuilder<DailyRecommendationWorker>(
                24, TimeUnit.HOURS
            )
                .setInitialDelay(minutesUntilMarketAlertTime(), TimeUnit.MINUTES)
                .setConstraints(
                    Constraints.Builder()
                        .setRequiredNetworkType(NetworkType.CONNECTED)
                        .build()
                )
                .build()

            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                WORK_NAME,
                ExistingPeriodicWorkPolicy.UPDATE,
                request
            )
        }

        private fun minutesUntilMarketAlertTime(): Long {
            val now = Calendar.getInstance()
            val target = Calendar.getInstance().apply {
                set(Calendar.HOUR_OF_DAY, 7)   // 07:00 — 1 hour before LSE opens
                set(Calendar.MINUTE, 0)
                set(Calendar.SECOND, 0)
                if (before(now)) add(Calendar.DAY_OF_YEAR, 1)
            }
            val diffMs = target.timeInMillis - now.timeInMillis
            return (diffMs / 60_000).coerceAtLeast(1)
        }
    }

    override suspend fun doWork(): Result {
        return try {
            createNotificationChannel()
            val repo = StockRepository(context)
            repo.refreshAll()
            val top5 = repo.getTopRecommendations(5)

            if (top5.isNotEmpty()) {
                val summary = top5.joinToString(" • ") { "${it.stock.ticker} (${it.score}/100)" }
                sendNotification(
                    title = "Today's Top 5 Investment Picks",
                    body = summary
                )
            }
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }

    private fun sendNotification(title: String, body: String) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(body)
            .setStyle(NotificationCompat.BigTextStyle().bigText(body))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()

        val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        manager.notify(NOTIFICATION_ID, notification)
    }

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID,
            "Investment Recommendations",
            NotificationManager.IMPORTANCE_HIGH
        ).apply {
            description = "Daily pre-market stock recommendations"
        }
        val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        manager.createNotificationChannel(channel)
    }
}
