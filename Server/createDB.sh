#!/bin/sh

cd data
sqlite3 sqliteDB.db < db.sql
