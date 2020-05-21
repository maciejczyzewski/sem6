package com.example.myapplication.view

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.Menu
import android.view.MenuItem
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity
import com.example.myapplication.Core
import com.example.myapplication.R
import kotlinx.android.synthetic.main.activity_main.*

class MainActivity : AppCompatActivity() {
    companion object {
        var globalVar = (0..20).random()
        var globalI = 0
        var globalCR = 666666666
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        //setTheme(R.style.AppTheme)
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        setSupportActionBar(toolbar)

        Log.i("DEBUG", "MAIN SCREEEN!!!!")

        fab.setOnClickListener { view ->
            startActivity(Intent(this@MainActivity, RankActivity::class.java))
            //Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
            //        .setAction("Action", null).show()
        }

        button_logout.setOnClickListener {
            Core.instance?.logout(getApplicationContext());
            Log.i("MAIN", "LOGOUT");
            startActivity(Intent(this@MainActivity, UserActivity::class.java))
        }
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        // Inflate the menu; this adds items to the action bar if it is present.
        menuInflater.inflate(R.menu.menu_main, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        if (item.itemId === R.id.action_ranking) {
            startActivity(Intent(this@MainActivity, RankActivity::class.java))
        }
        if (item.itemId === R.id.action_logout) {
            Core.instance?.logout(getApplicationContext());
            Log.i("MAIN", "LOGOUT");
            startActivity(Intent(this@MainActivity, UserActivity::class.java))
        }
        return when (item.itemId) {
            R.id.action_ranking -> true
            else -> super.onOptionsItemSelected(item)
        }
    }
}
