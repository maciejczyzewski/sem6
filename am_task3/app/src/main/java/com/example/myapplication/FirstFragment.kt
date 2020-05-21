package com.example.myapplication

import android.app.AlertDialog
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.example.myapplication.database.Company
import com.example.myapplication.view.MainActivity.Companion.globalCR
import com.example.myapplication.view.MainActivity.Companion.globalI
import com.example.myapplication.view.MainActivity.Companion.globalVar
import com.example.myapplication.view.UserActivity
import com.jeppeman.highlite.SQLiteOperator
import kotlinx.android.synthetic.main.fragment_first.*
import java.util.*
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

        val username = getContext()?.let { it1 -> Core.instance?.getUsername(it1) };
        textView_username.setText("your username is @" + username);

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

                    /*
                     Jeżeli udało się wygrać
                        za 1 razem - 5pkt,
                        za 2 do 4 - 3pkt,
                        za 5 do 6 - 2pkt,
                        za 7 do 10 - 1pkt,
                     FIXME: Powyżej 10 gra powinna się zrestartować z informacją, że przegrałeś.
                     */

                    var score : Int = 0;

                    if (globalI == 1) {
                        score = 5;
                    } else if (globalI >= 2 && globalI <= 4) {
                        score = 3;
                    } else if (globalI >= 5 && globalI <= 6) {
                        score = 2;
                    } else if (globalI >= 7 && globalI <= 10) {
                        score = 1;
                    }

                    // FIXME: alertDialog ask for 'name'?
                    // https://www.journaldev.com/309/android-alert-dialog-using-kotlin#alert-dialog-with-edit-text
                    AlertDialog.Builder(context)
                        .setTitle("Wygrana!")
                        .setMessage("brawo! zrobiles to tylko w " + globalI.toString() + " --> score=" + score.toString())
                        .setPositiveButton(android.R.string.yes)
                            { dialog, which ->
                                //withEditText(view, score);
                                val thread = Thread(Runnable {
                                    try {
                                        val username = getContext()?.let { it1 -> Core.instance?.getUsername(it1) };
                                        if (username != null) {
                                            Core.instance?.sendScore(username, score)
                                        };
                                    } catch (e: Exception) {
                                        e.printStackTrace()
                                    }
                                })
                                thread.start()
                            }
                        .setIcon(android.R.drawable.ic_dialog_alert)
                        .show()

                    /*viewKonfetti.build()
                        .addColors(Color.YELLOW, Color.GREEN, Color.MAGENTA)
                        .setDirection(0.0, 359.0)
                        .setSpeed(1f, 5f)
                        .setFadeOutEnabled(true)
                        .setTimeToLive(2000L)
                        .addShapes(Shape.Square, Shape.Circle)
                        .addSizes(Size(12))
                        .setPosition(-50f, viewKonfetti.width + 50f, -50f, -50f)
                        .streamFor(300, 5000L)
                    */

                    // globalVar = (0..20).random();
                    // globalI = 0;
                }


                if (globalI > 10) {
                    AlertDialog.Builder(context)
                        .setTitle("Przegrana!!")
                        .setMessage("o nie przegrales!")
                        .setPositiveButton(android.R.string.yes) { dialog, which ->
                            view.findViewById<Button>(R.id.button_new).callOnClick();
                        }
                        .setIcon(android.R.drawable.ic_dialog_alert)
                        .show()

                    // FIXME: add lisner?
                    // view.findViewById<Button>(R.id.button_new).callOnClick();
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

        /*view.findViewById<Button>(R.id.button_logout).setOnClickListener {
            Core.getInstance().logout();
            Log.i("MAIN", "LOGOUT");
            startActivity(Intent(getActivity(), UserActivity::class.java))
        }*/
    }

    fun withEditText(view: View, score: Int) {
        val builder = AlertDialog.Builder(context)
        val inflater = layoutInflater
        builder.setTitle("With EditText")
        val dialogLayout = inflater.inflate(R.layout.alert_dialog_with_edittext, null)
        val editText  = dialogLayout.findViewById<EditText>(R.id.editText)
        builder.setView(dialogLayout)
        builder.setPositiveButton("OK") { dialogInterface, i ->
            // FIXME: add to database
            // ---> editText.text.toString()
            // ---> score
            // ==================== CORE.sendScore
            val operator =
                context?.let { SQLiteOperator.from(it, Company::class.java) }
            val companyObject = Company()
            companyObject.name = editText.text.toString()
            companyObject.score = score
            companyObject.created = Date()
            companyObject.employees = Arrays.asList("John", "Bob")
            if (operator != null) {
                operator.save(companyObject).executeBlocking()
            }

            val thread = Thread(Runnable {
                try {
                    val username = getContext()?.let { it1 -> Core.instance?.getUsername(it1) };
                    if (username != null) {
                        Core.instance?.sendScore(username, score)
                    };
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            })

            thread.start()

            Toast.makeText(context, "EditText is " + editText.text.toString() + "|" + score.toString(), Toast.LENGTH_SHORT).show()
        }
        builder.show()
    }
}

