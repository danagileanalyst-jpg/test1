package com.investmentapp.data.api

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {

    private fun buildClient(): OkHttpClient {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
        return OkHttpClient.Builder()
            .addInterceptor(logging)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    fun create(baseUrl: String): FinancialApiService =
        Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(buildClient())
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(FinancialApiService::class.java)
}
