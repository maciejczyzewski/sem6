package com.example.myapplication

//import androidx.navigation.fragment.NavHostFragment
import android.app.AlertDialog
import android.content.Context
import android.content.Intent
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
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.NavHostFragment.findNavController
import com.example.myapplication.view.MainActivity
import java.lang.Compiler.command





class LoginFragment : Fragment() { //AppCompatActivity() {

    private val TAG = "LoginFragment"

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        Log.i(TAG, "WOKRINGINGIGNIGNIGGNi22222222222222222I!");

        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_login, container, false)
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
                AlertDialog.Builder(getContext())
                    .setTitle("Blad!")
                    .setMessage("USER NOT EXISTS")
                    .setPositiveButton(android.R.string.yes, null)
                    .setIcon(android.R.drawable.ic_dialog_alert)
                    .show()
            }
        }

        view.findViewById<Button>(R.id.button_submit).setOnClickListener {
            Log.i(TAG, "SUBMIT");
            // GET FROM TEXT VIEW
            val editText  = view.findViewById<EditText>(R.id.editText2)
            Log.i(TAG, editText.text.toString());
            val thread = Thread(Runnable {
                try {
                    val status =
                        getContext()?.let { it1 -> Core.instance?.login(it1, editText.text.toString()) };
                    if (status!!) {
                        Log.i(TAG, "-------------> OKAY");
                        startActivity(Intent(getActivity(), MainActivity::class.java))
                    } else {
                        // FIXME: toast
                        Log.i(TAG, "-------------> USER NOT EXISTS!");

                        /*AlertDialog.Builder(getContext())
                            .setTitle("Blad!")
                            .setMessage("USER NOT EXISTS")
                            .setPositiveButton(android.R.string.yes, null)
                            .setIcon(android.R.drawable.ic_dialog_alert)
                            .show()*/

                        val message = mHandler.obtainMessage(1, null)
                        message.sendToTarget()
                        //Toast.makeText(context, "USER NOT EXISTS", Toast.LENGTH_SHORT).show()
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            })

            thread.start()
        }

        view.findViewById<Button>(R.id.button_other).setOnClickListener {
            Log.i(TAG, "REGISTER");
            findNavController(this).navigate(R.id.action_LoginFragment_to_registerFragment)
        }
    }
}