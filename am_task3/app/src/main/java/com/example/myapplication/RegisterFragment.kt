package com.example.myapplication

import android.app.AlertDialog
import android.content.Context
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.Message
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.NavHostFragment.findNavController
import com.example.myapplication.view.UserActivity

// https://stackoverflow.com/questions/59196327/navigate-between-different-graphs-with-navigation-components

class RegisterFragment : Fragment() { //AppCompatActivity() {

    private val TAG = "RegisterFragment"

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        Log.i(TAG, "WOKRINGINGIGNIGNIGGNi22222222222222222I!");

        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_register, container, false)
    }

    override fun onAttach(context: Context) {
        super.onAttach(context)
        Log.i(TAG, "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
    }

    override fun onResume() {
        super.onResume()
        Log.i(TAG, "!!!!!!!!!!!!!!!!!!BAZUNGA!!!!!!!!!!!!");
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val mHandler = object : Handler(Looper.getMainLooper()) {
            override fun handleMessage(message: Message?) {
                // This is where you do your work in the UI thread.
                // Your worker tells you in the message what to do.
                if (message != null) {
                    if (message.what == 1) {
                    AlertDialog.Builder(getContext())
                        .setTitle("blad!")
                        .setMessage("USERNAME TAKEN")
                        .setPositiveButton(android.R.string.yes, null)
                        .setIcon(android.R.drawable.ic_dialog_alert)
                        .show()
                    }
                    if (message.what == 2) {
                        Toast.makeText(context, "USER REGISTRED", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }

        Log.i(TAG, "WOKRINGINGIGNIGNIGGNI!");

        view.findViewById<Button>(R.id.button_submit).setOnClickListener {
            Log.i(TAG, "SUBMIT");
            val editText  = view.findViewById<EditText>(R.id.editText2)
            Log.i(TAG, editText.text.toString());
            val thread = Thread(Runnable {
                try {
                    val status = Core.instance?.register(editText.text.toString());
                    if (status!!) {
                        // move to page
                        Log.i(TAG, "-------------> OKAY");
                        /*AlertDialog.Builder(getContext())
                            .setTitle("hurra!")
                            .setMessage("user zarejestrowany")
                            .setPositiveButton(android.R.string.yes, null)
                            .setIcon(android.R.drawable.ic_dialog_alert)
                            .show()*/
                        // Toast.makeText(context, "USER REGISTRED", Toast.LENGTH_SHORT).show()
                        val message = mHandler.obtainMessage(2, null)
                        message.sendToTarget()
                    } else {
                        // FIXME: toast
                        Log.i(TAG, "-------------> ALREADY TAKEN");
                        /*AlertDialog.Builder(getContext())
                            .setTitle("blad!")
                            .setMessage("USERNAME TAKEN")
                            .setPositiveButton(android.R.string.yes, null)
                            .setIcon(android.R.drawable.ic_dialog_alert)
                            .show()*/
                        // Toast.makeText(context, "USER TAKEN", Toast.LENGTH_SHORT).show()
                        val message = mHandler.obtainMessage(1, null)
                        message.sendToTarget()
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            })

            thread.start()
        }

        view.findViewById<Button>(R.id.button_other).setOnClickListener {
            Log.i(TAG, "LOGIN");
            findNavController(this).navigate(R.id.action_registerFragment_to_LoginFragment)
        }
    }
}