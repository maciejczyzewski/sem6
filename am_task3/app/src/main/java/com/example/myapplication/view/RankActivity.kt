package com.example.myapplication.view

import android.app.AlertDialog
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.Message
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.myapplication.Core
import com.example.myapplication.MyRecyclerViewAdapter
import com.example.myapplication.MyRecyclerViewAdapter.ItemClickListener
import com.example.myapplication.R
import com.example.myapplication.database.Company
import com.jeppeman.highlite.SQLiteOperator
import java.util.*

//import java.sql.Date;

// FIXME: use https://github.com/requery/requery/blob/master/requery-android/example-kotlin/src/main/kotlin/io/requery/android/example/app/CreatePeople.kt
// FIXME: use https://github.com/jeppeman/HighLite

class RankActivity : AppCompatActivity(), ItemClickListener {
    var adapter: MyRecyclerViewAdapter? = null
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.ranking_layout)

        // TODO: remove this trash
        // val database: SQLiteDatabase = DatabaseManager.getInstance().openDatabase()
/*
        val operator =
            SQLiteOperator.from(this, Company::class.java)
        /*val companyObject = Company()
        companyObject.name = "My awesome company"
        companyObject.created = Date()
        companyObject.employees = Arrays.asList("John", "Bob")
        operator.save(companyObject).executeBlocking()
*/

        // data to populate the RecyclerView with
        val animalNames = ArrayList<String>()
        /*animalNames.add("Horse")
        animalNames.add("Cow")
        animalNames.add("Camel")
        animalNames.add("Sheep")
        animalNames.add("Goat")*/

        // FIXME: scores from CORE
        val testObj = operator
            .list
            .withRawQuery("SELECT * FROM companies ORDER BY score DESC LIMIT 10")
            .executeBlocking()

        testObj.forEach {
            animalNames.add(it.name + " score=" + it.score.toString());
        }
*/
        /////////////////////////////////////////

        var context_copy = this

        val mHandler = object : Handler(Looper.getMainLooper()) {
            override fun handleMessage(message: Message?) {
                // This is where you do your work in the UI thread.
                // Your worker tells you in the message what to do.
                if (message != null) {
                    if (message.what == 1) {
                        val recyclerView = findViewById<RecyclerView>(R.id.rvScores)
                        recyclerView.layoutManager = LinearLayoutManager(context_copy)
                        adapter = MyRecyclerViewAdapter(context_copy, message.obj as List<String>)
                        adapter!!.setClickListener(context_copy)
                        recyclerView.adapter = adapter
                    }

                }
            }
        }

        val thread = Thread(Runnable {
            try {
                val animalNames = Core.instance?.getScores()
                val message = mHandler.obtainMessage(1, animalNames)
                message.sendToTarget()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        })

        Toast.makeText(this, "Loading", Toast.LENGTH_SHORT).show()

        thread.start()

        /////////////////////////////////////////////

        // set up the RecyclerView
        /*val recyclerView = findViewById<RecyclerView>(R.id.rvScores)
        recyclerView.layoutManager = LinearLayoutManager(this)
        adapter = MyRecyclerViewAdapter(this, animalNames)
        adapter!!.setClickListener(this)
        recyclerView.adapter = adapter
*/
        this.findViewById<Button>(R.id.button_back).setOnClickListener {
            startActivity(Intent(this@RankActivity, MainActivity::class.java))
        }
    }

    override fun onItemClick(view: View?, position: Int) {
        Toast.makeText(
            this,
            "You clicked " + adapter!!.getItem(position) + " on row number " + position,
            Toast.LENGTH_SHORT
        ).show()
    }
}