package com.example.myapplication.database;

import com.jeppeman.highlite.PrimaryKey;
import com.jeppeman.highlite.SQLiteColumn;
import com.jeppeman.highlite.SQLiteTable;

import java.util.Date;
import java.util.List;

@SQLiteTable(
        database = CompanyDatabase.class,
        tableName = "users", // If left empty, the name of the table defaults to the class name snake cased
        autoCreate = true, // defaults to true, set to false if you do not want the table to be created automatically
        autoAddColumns = true, // defaults to true, set to false if you do not want new columns to be added automatically on upgrades
        autoDeleteColumns = true // defaults to false, set to true if you want deleted fields to be removed from the database automatically on upgrades
)
public class User {

    @SQLiteColumn(primaryKey = @PrimaryKey(autoIncrement = true))
    public long id; // fields annotated with @SQLiteColumn need to be at least package local

    @SQLiteColumn("userName") // Column name becomes companyName here
    public String name;

    // FIXME: tu moglbo by byc haslo

    @SQLiteColumn
    public Date created; // Dates are stored as INTEGER's with the amount of seconds since UNIX epoch
}