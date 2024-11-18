from flask import Flask, session, render_template, redirect, url_for, make_response, request
from flask_session import Session
import x

def _________GET_________(): pass

##############################
@app.get("/") 
def view_index():
    name = "Test"
    return render_template("view_index.html", name=name)
