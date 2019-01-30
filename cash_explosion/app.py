from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.serializer import loads, dumps
import pymysql
pymysql.install_as_MySQLdb()

import pandas as pd
import sqlite3
import os

from flask import Flask, jsonify, render_template, request, redirect, Response

#from config import db1database, db1host, db1pass, db1user, db2database, db2host, db2pass, db2user
from . import config as co

Base = declarative_base()
Base2 = declarative_base()

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    date = Column(String(255))
    name = Column(String(255))
    residence = Column(String(255))
    state = Column(String(2))
    ticket_bought = Column(String(255))
    first_pick = Column(Integer)
    first_amount = Column(Integer)
    second_pick = Column(Integer)
    second_amount = Column(Integer)
    third_pick = Column(Integer)
    third_amount = Column(Integer)
    doubles = Column(Integer)
    bonus = Column(Integer)
    bonus_amount = Column(Integer)

class Vendor(Base):
    __tablename__ = "vendor"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    address = Column(String(255))
    price_level = Column(Integer)
    rating = Column(Float)
    user_rating_total = Column(Integer)
    placetype = Column(String(255))
    latitude = Column(String(255))
    longitude = Column(String(255))
    player_id = Column(Integer)

engine = create_engine(f"mysql://{co.db1user}:{co.db1pass}@{co.db1host}:3306/{co.db1database}")
conn = engine.connect()
engine2 = create_engine(f"mysql://{co.db2user}:{co.db2pass}@{co.db2host}:3306/{co.db2database}")
conn2 = engine2.connect()
Base.metadata.create_all(engine2)

Base.metadata.create_all(engine)

# Use this to clear out the db
#Base.metadata.drop_all(engine)

from sqlalchemy.orm import Session
session = Session(bind=engine)
session2 = Session(bind=engine)
session3 = Session(bind=engine2)
session4 = Session(bind=engine)

app = Flask(__name__)

navbar = [{"name":"Add Data","link":"adddata"},
            {"name":"View Data","link":"view_data"},
            {"name":"Chart Data","link":"chart_data"},
            {"name":"Time Data","link":"time_data"},
            {"name":"Map - Winners","link":"map"},
            {"name":"Map - Hometown","link":"map2"},
            {"name":"Retailers","link":"vendors"},
            {"name":"Numbers","link":"numbers"}]

@app.route("/")
def index():
    return render_template("index.html", navbar=navbar)

@app.route("/adddata")
def add_data_page():
    return render_template("adddata.html", navbar=navbar)

@app.route("/view_data")
def view_data():
    return render_template("view_data.html", navbar=navbar)

@app.route("/chart_data")
def chart_data():
    return render_template("chart_data.html", navbar=navbar)

@app.route("/time_data")
def time_data():
    return render_template("time_data.html", navbar=navbar)

@app.route("/numbers")
def numbers():
    return render_template("numbers.html", navbar=navbar)

@app.route("/number/<number>")
def number(number):
    n = int(number)
    single_number_statistics = {}
    single_number_statistics["number"] = n
    df = pd.read_sql_query("SELECT * from players", conn)

    get_number_data = df.loc[(df['first_pick'] == n) | (df['second_pick'] == n) | (df['third_pick'] == n)]
    single_number_statistics["occurances"] = int(get_number_data.count()[0])

    #average won
    a = (int(df.loc[(df['first_pick'] == n)].sum()["first_amount"]) + int(df.loc[(df['second_pick'] == n)].sum()["second_amount"]) + int(df.loc[(df['third_pick'] == n)].sum()["third_amount"])) / int(get_number_data.count()[0])
    single_number_statistics["average"] = format(int(round(a,0)), ",")

    single_number_statistics["earliest_pick"] = get_number_data["date"].unique()[0]
    single_number_statistics["latest_pick"] = get_number_data["date"].unique()[len(get_number_data["date"].unique()) - 1]

    occurances_per_week = []
    for x in range(1,get_number_data["date"].value_counts().max() + 1):
        occurances_per_week.append(round(sum(get_number_data["date"].value_counts() >= x) / len(df["date"].unique()) * 100,1))
    single_number_statistics["percent_occurance"] = occurances_per_week
    return render_template("number.html", number=single_number_statistics, navbar=navbar)

@app.route("/map")
def map():
    return render_template("map.html", navbar=navbar)

@app.route("/map2")
def map2():
    return render_template("map2.html", navbar=navbar)

@app.route("/vendors")
def vendors():
    return render_template("vendors.html", navbar=navbar)

@app.route("/api/vendors")
def get_vendors():
    vendors = []
    for u in session3.query(Vendor).all():
        row = u.__dict__
        row.pop('_sa_instance_state', None)
        vendors.append(row)
    
    return jsonify(vendors)

@app.route("/api/insertdata", methods=["POST"])
def insert_data():
    playerData = request.get_json(force=True)
    playerData["name"] = playerData["name"].title()
    playerData["residence"] = playerData["residence"].title()
    playerData["ticket_bought"] = playerData["ticket_bought"].title()
    if playerData['bonus'] == '0':
        playerData["bonus_amount"] = ""

    #player = Player(date=playerData['date'], 
    #                name=playerData['name'],
    #                residence=playerData['residence'],
    #                state=playerData['state'],
    #                ticket_bought=playerData["ticket_bought"],
    #                first_pick=playerData["first_pick"],
    #                first_amount=playerData["first_amount"],
    #                second_pick=playerData["second_pick"],
    #                second_amount=playerData["second_amount"],
    #                third_pick=playerData["third_pick"],
    #                third_amount=playerData["third_amount"],
    #                doubles=playerData["doubles"],
    #                bonus=playerData["bonus"],
    #                bonus_amount=playerData["bonus_amount"])
    #session.add(player)
    #session.commit()

    return render_template("index.html")

@app.route("/api/get_data")
def get_data():
    players = []
    for u in session2.query(Player).all():
        row = u.__dict__
        row.pop('_sa_instance_state', None)
        players.append(row)
    
    print(len(players))
    return jsonify(players)

@app.route("/api/get_chart_data")
def get_chart_data():
    numbers = []
    for x in range(20):
        numbers.append({"frequency":0,"total":0,"average":0})
    for u in session4.query(Player).all():
        numbers[u.first_pick - 1]["frequency"] = numbers[u.first_pick - 1]["frequency"] + 1
        numbers[u.first_pick - 1]["total"] = numbers[u.first_pick - 1]["total"] + u.first_amount
        numbers[u.second_pick - 1]["frequency"] = numbers[u.second_pick - 1]["frequency"] + 1
        numbers[u.second_pick - 1]["total"] = numbers[u.second_pick - 1]["total"] + u.second_amount
        numbers[u.third_pick - 1]["frequency"] = numbers[u.third_pick - 1]["frequency"] + 1
        numbers[u.third_pick - 1]["total"] = numbers[u.third_pick - 1]["total"] + u.third_amount
    for number in numbers:
        try:
            number["average"] = number["total"] / number["frequency"]
        except(ZeroDivisionError):
            print('cant')
    return jsonify(numbers)

@app.route("/api/time_data")
def get_time_data():
    df = pd.read_sql_query("SELECT * FROM players", conn)
    df["game total"] = df["first_amount"] + df["second_amount"] + df["third_amount"]
    min_val = df.groupby(['date']).min()
    max_val = df.groupby(['date']).max()
    avg = df.groupby(['date']).mean()
    date_describe = pd.DataFrame({"min":min_val["game total"],"max":max_val["game total"],"avg":avg["game total"]})
    index_reseted = date_describe.reset_index()
    return jsonify(index_reseted.to_json(orient="records"))

@app.route("/api/describe")
def describe():
    overall_stats = {}

    df = pd.read_sql_query("SELECT * FROM players", conn)

    #Players that lived and bought ticket in same city
    same_city = 2
    for index, row in df.iterrows():
        if (row["residence"] == row["ticket_bought"]):
            same_city += 1
    overall_stats["sameCityPercentage"] = same_city / int(df.count()[0]) * 100

    overall_stats["numberOfGames"] = int(df.count()[0])
    latest_date = df.sort_values(by="date", ascending=False).reset_index()
    overall_stats["latestDate"] = latest_date.loc[0]["date"]

    df["game total"] = df["first_amount"] + df["second_amount"] + df["third_amount"]
    sort_gametotal = df.sort_values(by=["date", "game total"])
    sort_gametotal = sort_gametotal.reset_index()
    first_place = sort_gametotal.iloc[7::8,:]
    second_place = sort_gametotal.iloc[6::8,:]
    sort_gametotal["bonus_amount"].loc[sort_gametotal["bonus_amount"] == 0] = 0
    grand_total = sort_gametotal["game total"].sum() + sort_gametotal["bonus_amount"].sum() + first_place["game total"].sum() + second_place["game total"].sum()
    overall_stats["cashWon"] = int(grand_total) + 2486500 + 449800
    overall_stats["doublesFound"] = int(sort_gametotal["doubles"].sum())
    overall_stats["bonusesFound"] = int(sort_gametotal["bonus"].sum())

    sort_gametotal["grand total"] = sort_gametotal["game total"] + sort_gametotal["bonus_amount"]

    find_highest_total_overall = sort_gametotal.sort_values(by="grand total", ascending=False).reset_index().loc[0]
    overall_stats["highestTotalOverall"] = {"name":find_highest_total_overall["name"],
                                            "residence": find_highest_total_overall["residence"],
                                            "date":find_highest_total_overall["date"],
                                            "grandTotal":int(find_highest_total_overall["grand total"]) }

    find_highest_game_total = sort_gametotal.sort_values(by="game total", ascending=False).reset_index().loc[0]
    overall_stats["highestGameTotal"] = {"name":find_highest_game_total["name"],
                                            "residence": find_highest_game_total["residence"],
                                            "date":find_highest_game_total["date"],
                                            "grandTotal":int(find_highest_game_total["game total"]) }

    find_lowest_game_total = sort_gametotal.sort_values(by="grand total", ascending=True).reset_index().loc[0]
    overall_stats["lowestGameTotal"] = {"name":find_lowest_game_total["name"],
                                            "residence": find_lowest_game_total["residence"],
                                            "date":find_lowest_game_total["date"],
                                            "grandTotal":int(find_lowest_game_total["game total"])}
                                                                                   
    a = sort_gametotal["residence"].value_counts()
    overall_stats["residenceLeader"] = {"city":a.keys()[0], "amount":int(a[0])}
    b = sort_gametotal["ticket_bought"].value_counts()
    overall_stats["ticketBoughtLeader"] = {"city":b.keys()[0], "amount":int(b[0])}

    #state representation
    staterep = sort_gametotal["state"]
    OHPercentage = (staterep.value_counts()[0]) / (df.count()[0]) * 100
    overall_stats["stateRepresentation"] = {"numberOfStates":len(staterep.unique()),"OHPercentage":OHPercentage}
    return jsonify(overall_stats)

if __name__ == "__main__":
    app.run()
