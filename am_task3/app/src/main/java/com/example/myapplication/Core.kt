package com.example.myapplication

import android.content.Context
import android.util.Log
import com.example.myapplication.database.User
import com.google.gson.Gson
import com.jeppeman.highlite.SQLiteOperator
import com.jeppeman.highlite.SQLiteQuery
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.IOException
import java.util.*

internal class APIResponse {
    var status = false
    var __debug: String? = null
}

internal class APIResponseRow {
    var name: String? = null
    var score: Int? = null
}

internal class APIResponseWithList {
    lateinit var list: ArrayList<APIResponseRow>
    var status = false
    var __debug: String? = null
}

class Core private constructor() {
    var client = OkHttpClient()
    var SERVER = "http://192.168.0.8:8000"

    fun test() {
        Log.i(TAG, "TEST CALLED!!!!!!!!!!!!!!!!!!")
    }

    @Throws(IOException::class)
    fun run(url: String?): String {
        val request = Request.Builder()
            .url(url!!)
            .build()
        client.newCall(request).execute().use { response -> return response.body!!.string() }
    }

    fun login(context: Context, username: String): Boolean {
        Log.i(TAG, "login from $username")
        //Log.i(TAG, get("http://httpbin.org/ip").jsonObject.getString("origin"));
        val url = SERVER + "/login/$username"

        // status --> true?
        // insert localy session | write to function get_user()
        try {
            val json_str = run(url)
            Log.i(TAG, json_str)
            val g = Gson()
            val res = g.fromJson(json_str, APIResponse::class.java)
            return if (res.status == true) {
                Log.i(TAG, "TRUE")
                val operator = SQLiteOperator.from(context, User::class.java)
                val companyObject = User()
                companyObject.name = username
                companyObject.created = Date()
                if (operator != null) {
                    Log.i(TAG, "ADDED TO LOCAL DATABASE")
                    operator.save(companyObject).executeBlocking()
                }
                true
            } else {
                Log.i(TAG, "False")
                false
            }
        } catch (e: IOException) {
            e.printStackTrace()
        }
        return false
    }

    fun register(username: String): Boolean {
        val url = SERVER + "/register/$username"
        try {
            val json_str = run(url)
            Log.i(TAG, json_str)
            val g = Gson()
            val res = g.fromJson(json_str, APIResponse::class.java)
            return res.status
        } catch (e: IOException) {
            e.printStackTrace()
        }
        Log.i(TAG, "register from $username")
        return true
    }

    fun sendScore(username: String, score: Int): Boolean {
        Log.i(TAG, "SENDING SCORE $username / $score")
        val url = SERVER + "/score/$username/$score"
        try {
            val json_str = run(url)
            Log.i(TAG, json_str)
            val g = Gson()
            val res = g.fromJson(json_str, APIResponse::class.java)
            return res.status
        } catch (e: IOException) {
            e.printStackTrace()
        }
        return false
    }

    fun getScores(): List<String> {
        val animalNames = ArrayList<String>()
        /*animalNames.add("Horse")
        animalNames.add("Cow")
        animalNames.add("Camel")
        animalNames.add("Sheep")
        animalNames.add("Goat")*/
        Log.i(TAG, "SENDING RANK")
        val url = SERVER + "/rank"
        try {
            val json_str = run(url)
            Log.i(TAG, json_str)
            val g = Gson()
            val res = g.fromJson(json_str, APIResponseWithList::class.java)
            res.list.forEach {
                animalNames.add(it.name + " score=" + it.score.toString());
            }
        } catch (e: IOException) {
            e.printStackTrace()
        }

        return animalNames
    }

    // DROP LOCALDATABASE
    fun logout(context: Context) {
        Log.i(TAG, "LOGOUT")
        val operator = SQLiteOperator.from(context, User::class.java)
        operator
            .delete()
            .withQuery(
                SQLiteQuery
                    .builder()
                    .build()
            ).executeBlocking();
    } // FIXME: getScores

    fun getUsername(context: Context): String {
        Log.i(TAG, "GET USERNAME")
        val operator = SQLiteOperator.from(context, User::class.java)
        val testObj = operator
            .list
            .withRawQuery("SELECT * FROM users")
            .executeBlocking()

        if (testObj.size == 0) {
            return "-"
        } else {
            return testObj[0].name;
        }
    }

    // FIXME: sendScore
    companion object {
        // Create the instance
        private const val TAG = "Core"

        // Return the instance
        var instance: Core? = null
            get() {
                if (field == null) {
                    synchronized(
                        Core::class.java
                    ) { if (field == null) field = Core() }
                }
                // Return the instance
                return field
            }
            private set
    }

    init {
        // FIXME: check if logged in?
        // okay / good idea!

        Log.i(TAG, "TESSSST FIRST TIME :-------)")
        // Constructor hidden because this is a singleton
    }
}