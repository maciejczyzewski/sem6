package com.example.myapplication

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import com.example.myapplication.view.MainActivity

class SplashFragment : Fragment() { //AppCompatActivity() {

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        Log.i("OMG OMG", "WOKRINGINGIGNIGNIGGNi22222222222222222I!");

        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_splash, container, false)
    }

    override fun onAttach(context: Context) {
        super.onAttach(context)
        Log.i("FINAL", "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
    }

    override fun onResume() {
        super.onResume()
        Log.i("FINAL", "!!!!!!!!!!!!!!!!!!BAZUNGA!!!!!!!!!!!!");
        val thread: Thread = object : Thread() {
            override fun run() {

                    try {
                        Thread.sleep(3000L)
                        startActivity(Intent(getActivity(), MainActivity::class.java))
                        (activity as Activity?)!!.overridePendingTransition(0, 0)
                    } catch (e: InterruptedException) {
                        e.printStackTrace()
                    }

            }
        }

        thread.start()

        /*try {
            Thread.sleep(3000L)
            startActivity(Intent(getActivity(), MainActivity::class.java))
            (activity as Activity?)!!.overridePendingTransition(0, 0)
        } catch (e: InterruptedException) {
            e.printStackTrace()
        }*/
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        Log.i("OMG OMG", "WOKRINGINGIGNIGNIGGNI!");


    }
}