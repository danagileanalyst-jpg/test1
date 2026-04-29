package com.investmentapp.ui.main

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.investmentapp.data.model.RecommendedStock
import com.investmentapp.data.repository.StockRepository
import kotlinx.coroutines.launch

class MainViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = StockRepository(application)

    private val _topRecommendations = MutableLiveData<List<RecommendedStock>>()
    val topRecommendations: LiveData<List<RecommendedStock>> = _topRecommendations

    private val _isLoading = MutableLiveData(false)
    val isLoading: LiveData<Boolean> = _isLoading

    private val _errorMessage = MutableLiveData<String?>()
    val errorMessage: LiveData<String?> = _errorMessage

    private val _selectedTab = MutableLiveData(0)  // 0=All, 1=UK, 2=Europe
    val selectedTab: LiveData<Int> = _selectedTab

    val allStocksLive = repository.allStocksLive

    init {
        loadRecommendations()
    }

    fun loadRecommendations() {
        viewModelScope.launch {
            _isLoading.value = true
            _errorMessage.value = null
            try {
                repository.refreshAll()
                val recs = repository.getTopRecommendations(10)
                _topRecommendations.value = filterByTab(recs, _selectedTab.value ?: 0)
            } catch (e: Exception) {
                _errorMessage.value = "Failed to load data: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun selectTab(index: Int) {
        _selectedTab.value = index
        _topRecommendations.value?.let { all ->
            _topRecommendations.value = filterByTab(all, index)
        } ?: loadRecommendations()
    }

    private fun filterByTab(list: List<RecommendedStock>, tab: Int) = when (tab) {
        1 -> list.filter { it.stock.market == "UK" }
        2 -> list.filter { it.stock.market == "Europe" }
        else -> list
    }
}
