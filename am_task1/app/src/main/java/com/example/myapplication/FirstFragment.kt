package com.example.myapplication

import android.app.AlertDialog
import android.content.DialogInterface
import android.content.SharedPreferences
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.example.myapplication.MainActivity.Companion.globalCR
import com.example.myapplication.MainActivity.Companion.globalI
import com.example.myapplication.MainActivity.Companion.globalVar
import kotlin.math.min


/**
 * A simple [Fragment] subclass as the default destination in the navigation.
 */
class FirstFragment : Fragment() {

    override fun onCreateView(
            inflater: LayoutInflater, container: ViewGroup?,
            savedInstanceState: Bundle?
    ): View? {


        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_first, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // old -----
        //view.findViewById<Button>(R.id.button_first).setOnClickListener {
        //    println("hello!");
        //    findNavController().navigate(R.id.action_FirstFragment_to_SecondFragment)
        //}
        // ---------

        val textView: TextView = view.findViewById(R.id.textview_first) as TextView
        val textView_i: TextView = view.findViewById(R.id.textView_i) as TextView;
        val textView_cr: TextView = view.findViewById(R.id.textView_cr) as TextView;
        val numView: EditText = view.findViewById(R.id.editText) as EditText;

        if (globalCR < 666666666) {
            textView_cr.setText("aktualny rekord: " + globalCR.toString());
        } else {
            textView_cr.setText("aktualny rekord: jeszcze nie grales!");
        }

        /*if (context != null) {
        val mPrefs: SharedPreferences = context!!.getSharedPreferences("label", 0)
        val mString = mPrefs.getString("tag", "default_value_if_variable_not_found")

        val mEditor = mPrefs.edit()
        mEditor.putString("tag", "zapisane!").commit()
        }*/

        view.findViewById<Button>(R.id.button_submit).setOnClickListener {
            var x: Int? = null;
            println("@1")
            println("|"+numView.text.toString()+"|")
            if (!numView.text.toString().isNullOrEmpty()) {
                x = numView.text.toString().toIntOrNull();

                if (x != null) {
                if (x < 0 || x > 20) {
                    AlertDialog.Builder(context)
                        .setTitle("Zly zakres!")
                        .setMessage("zakres jest od 0-20 a ty wybrales -> " + x.toString())
                        .setPositiveButton(android.R.string.yes, null)
                        .setIcon(android.R.drawable.ic_dialog_alert)
                        .show()

                    x = -1;
                }
                }

            }

            if (x == null) {
                x = -1

                AlertDialog.Builder(context)
                    .setTitle("Nic nie wpisales!")
                    .setMessage("musisz wpisac cos ;-)")
                    .setPositiveButton(android.R.string.yes, null)
                    .setIcon(android.R.drawable.ic_dialog_alert)
                    .show()
            };

            println("@2")
            if (x != -1) {
                println("@3")
                println(x)
                globalI++;
                textView_i.setText("ilosc ruchow: " + globalI.toString());

                if (x < globalVar) {
                    textView.setText("<" + " dales mniej [twoje " + x.toString() + "]");
                } else if(x > globalVar) {
                    textView.setText(">" + " dales wiecej [twoje " + x.toString() + "]");
                } else {
                    textView.setText("== " + x.toString());
                    globalCR = min(globalCR, globalI);

                    textView_cr.setText("aktualny rekord: " + globalCR.toString());

                    AlertDialog.Builder(context)
                        .setTitle("Wygrana!")
                        .setMessage("brawo! zrobiles to tylko w " + globalI.toString())
                        .setPositiveButton(android.R.string.yes, null)
                        .setIcon(android.R.drawable.ic_dialog_alert)
                        .show()

                    globalVar = (0..20).random();
                    globalI = 0;
                }
            }
        }


        view.findViewById<Button>(R.id.button_new).setOnClickListener {
            println("restart");

            globalI = 0;
            globalVar = (0..20).random();

            textView.setText("nowa gra, zaczynaj!");
            textView_i.setText("ilosc ruchow: " + globalI.toString());

            AlertDialog.Builder(context)
                .setTitle("Nowa Gra")
                .setMessage("tajna liczba to " + globalVar.toString())
                .setPositiveButton(android.R.string.yes, null)
                .setIcon(android.R.drawable.ic_dialog_alert)
                .show()
            //findNavController().navigate(R.id.action_FirstFragment_to_SecondFragment)
        }
    }
}
