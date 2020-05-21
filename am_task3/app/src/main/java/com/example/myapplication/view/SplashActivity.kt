package com.example.myapplication.view

import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import com.example.myapplication.R

class SplashActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        // startActivity(new Intent(SplashActivity.this, SplashActivity.class));
        Log.i("DEBUG", "WELCOME SCREEN")

        //startActivity(new Intent(SplashActivity.this, MainActivity.class));

        // close splash activity

        //finish();
    }
}