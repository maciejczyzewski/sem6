package com.example.myapplication.database;

import android.util.Log;
import android.database.sqlite.SQLiteDatabase;
import com.jeppeman.highlite.*;

@SQLiteDatabaseDescriptor(
        dbName = "companyDatabase",
        dbVersion = 4 // Increment this to trigger an upgrade
)
public class CompanyDatabase {

    // Optional: define a method like this if you want to manually handle onOpen.
    // Note: PRAGMA foreign_keys = ON is set automatically if any foreign
    // keys are found for any table in the database.
    @OnOpen
    public static void onOpen(SQLiteDatabase db) {
        Log.i("DB", "onOpen");
    }

    // Optional: define a method like this if you want to manually handle onCreate;
    // i.e. if you opt out from automatic table creation on some table.
    @OnCreate
    public static void onCreate(SQLiteDatabase db) {
        Log.i("DB", "onCreate");
    }

    // Optional: define a method like this if you want to manually handle onUpgrade;
    // i.e. if you opt out from automatic upgrades on some table
    @OnUpgrade
    public static void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        Log.i("DB", "onUpgrade");
    }

}