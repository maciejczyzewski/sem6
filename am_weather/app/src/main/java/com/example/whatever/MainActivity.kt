package com.example.whatever

import android.annotation.SuppressLint
import android.content.Context
import android.location.Location
import android.location.LocationListener
//import com.google.android.gms.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.Observer
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.bumptech.glide.Glide
import com.github.kittinunf.fuel.Fuel
import com.github.kittinunf.fuel.gson.responseObject
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationServices
import com.google.android.material.snackbar.Snackbar
import com.google.gson.annotations.SerializedName
import kotlinx.android.synthetic.main.activity_main.*
import kotlin.math.roundToInt


class MainActivity : AppCompatActivity() {
    private var latitude: Double? = null
    private var longitude: Double? = null

    private val TAG = "MainActivity"

    private val viewModel by lazy {
        ViewModelProvider(this).get(WeatherViewModel::class.java)
    }

    private lateinit var fusedLocationClient: FusedLocationProviderClient

    @SuppressLint("MissingPermission")
    private fun getLocation() {
        Log.i(TAG, "Location!")
        fusedLocationClient.lastLocation
            .addOnSuccessListener { location: Location? ->
                latitude = location?.latitude
                longitude = location?.longitude
                Log.i(TAG, latitude.toString() + "/" + longitude.toString())
            }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        setSupportActionBar(findViewById(R.id.my_toolbar))

        ////////////
        /// FIXME
        fusedLocationClient = LocationServices.getFusedLocationProviderClient(this)
        this.getLocation()
        ////////////

        viewModel.isProgress.observe(this, Observer {
            showProgress(it)
        })
        viewModel.response.observe(this, Observer {
            showResult(it)
        })
        viewModel.error.observe(this, Observer {
            if (it == null)
                return@Observer
            showError(it)
            viewModel.error.value = null
        })

        val btn: Button = findViewById(R.id.refresh)
        btn.setOnClickListener(View.OnClickListener {
            viewModel.loadResponse()
            Toast.makeText(this@MainActivity, "Refresh action!", Toast.LENGTH_SHORT)
                .show()
        })
    }

    fun Double.formatTemp() = "%d°".format(this.roundToInt())
    fun Double.formathPa() = "%d hPa".format(this.roundToInt())
    fun Double.formatWind() = "%d km/h".format((this * 2.6).roundToInt())

    private fun showResult(model: ResponseModel) {
        containerView.visibility = View.VISIBLE
        val weather = model.forecasts.first()
        Log.i(TAG, model.title)
        val iconUrl = "https://www.metaweather.com/static/img/weather/png/${weather.code}.png"
        Glide.with(this)
                .load(iconUrl)
                .into(iconWeather)
        textLocation.text = model.title
        textTempMax.text = weather.maxTemp.formatTemp()
        textTempMin.text = weather.minTemp.formatTemp()
        textAirPressure.text = weather.airPressure.formathPa()
        textWindSpeed.text = weather.windSpeed.formatWind()
        iconWind.rotation = weather.windDirection.toFloat()
    }

    private fun showError(error: Throwable) {
        containerView.visibility = View.GONE
        Snackbar.make(
                mainView,
                "Error: ${error.message}",
                Snackbar.LENGTH_SHORT
        ).show()
    }

    private fun showProgress(show: Boolean) {
        progressView.visibility = if (show)
            View.VISIBLE
        else
            View.GONE
    }
}

class ResponseModel(
        @SerializedName("title")
        val title: String,
        @SerializedName("consolidated_weather")
        val forecasts: List<Weather>
)

class Weather(
        @SerializedName("weather_state_abbr")
        val code: String,
        @SerializedName("min_temp")
        val minTemp: Double,
        @SerializedName("max_temp")
        val maxTemp: Double,
        @SerializedName("wind_speed")
        val windSpeed: Double,
        @SerializedName("wind_direction")
        val windDirection: Double,
        @SerializedName("air_pressure")
        val airPressure: Double
)


class WeatherViewModel : ViewModel() {
    private val TAG = "WeatherViewModel"

    val isProgress = MutableLiveData(false)
    val response = MutableLiveData<ResponseModel>()
    val error = MutableLiveData<Throwable>()

    init {
        loadResponse()
    }

    fun loadResponse(location_code: Int = 523920) {
        val url = "https://www.metaweather.com/api/location/${location_code}/"
        isProgress.value = true
        Fuel.get(url)
            .responseObject<ResponseModel> { _, _, result ->
                isProgress.value = false
                result.fold({
                    response.value = it
                }, {
                    error.value = it.exception
                })
            }
    }
}