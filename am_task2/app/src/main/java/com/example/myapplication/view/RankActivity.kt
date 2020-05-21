package com.example.myapplication.view

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
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

        val testObj = operator
            .list
            .withRawQuery("SELECT * FROM companies ORDER BY score DESC LIMIT 10")
            .executeBlocking()

        testObj.forEach {
            animalNames.add(it.name + " score=" + it.score.toString());
        }

        // set up the RecyclerView
        val recyclerView = findViewById<RecyclerView>(R.id.rvScores)
        recyclerView.layoutManager = LinearLayoutManager(this)
        adapter = MyRecyclerViewAdapter(this, animalNames)
        adapter!!.setClickListener(this)
        recyclerView.adapter = adapter

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