package com.investmentapp.ui.main

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.tabs.TabLayout
import com.investmentapp.databinding.ActivityMainBinding
import com.investmentapp.ui.adapter.StockCardAdapter
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: MainViewModel by viewModels()
    private lateinit var adapter: StockCardAdapter

    private val notifLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { /* permission result handled silently */ }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        requestNotificationPermission()
        setupRecyclerView()
        setupTabs()
        setupSwipeRefresh()
        observeViewModel()
        updateDateHeader()
    }

    private fun setupRecyclerView() {
        adapter = StockCardAdapter { stock ->
            com.investmentapp.ui.detail.StockDetailActivity.start(this, stock)
        }
        binding.rvRecommendations.apply {
            layoutManager = LinearLayoutManager(this@MainActivity)
            adapter = this@MainActivity.adapter
            setHasFixedSize(false)
        }
    }

    private fun setupTabs() {
        binding.tabLayout.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab) = viewModel.selectTab(tab.position)
            override fun onTabUnselected(tab: TabLayout.Tab) = Unit
            override fun onTabReselected(tab: TabLayout.Tab) = Unit
        })
    }

    private fun setupSwipeRefresh() {
        binding.swipeRefresh.setOnRefreshListener {
            viewModel.loadRecommendations()
        }
    }

    private fun observeViewModel() {
        viewModel.isLoading.observe(this) { loading ->
            binding.swipeRefresh.isRefreshing = loading
            binding.shimmerLayout.apply {
                if (loading) { visibility = View.VISIBLE; startShimmer() }
                else { stopShimmer(); visibility = View.GONE }
            }
        }

        viewModel.topRecommendations.observe(this) { recs ->
            adapter.submitList(recs)
            binding.tvCount.text = "${recs.size} recommendations"
            binding.rvRecommendations.visibility = if (recs.isEmpty()) View.GONE else View.VISIBLE
            binding.tvEmpty.visibility = if (recs.isEmpty()) View.VISIBLE else View.GONE
        }

        viewModel.errorMessage.observe(this) { msg ->
            msg?.let { Toast.makeText(this, it, Toast.LENGTH_LONG).show() }
        }
    }

    private fun updateDateHeader() {
        val sdf = SimpleDateFormat("EEEE, d MMMM yyyy", Locale.UK)
        binding.tvDate.text = sdf.format(Date())
        binding.tvMarketAlert.text = "Alert set for 07:00 GMT — 1 hr before LSE opens"
    }

    private fun requestNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED
            ) {
                notifLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
        }
    }
}
