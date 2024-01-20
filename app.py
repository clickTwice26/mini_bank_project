from flask import Flask, request, render_template, redirect, url_for, flash, make_response,abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from sqlalchemy.testing.pickleable import User
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime, date
from func import *
import requests
import os
import time
import numpy as np
import pandas as pd
from random import randint as rd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chipichipichapachapadubidubudabadaba'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/our_bank'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.app_context().push()
class TodayDashboard:
	def __init__(self, **datas):
		self.total_spent = datas['total_spent']
		self.total_income = datas['total_income']
		self.last_transaction = datas['last_transaction_today']
		self.current_balance = datas['current_balance']

class Transaction(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(200), nullable=False)
	come = db.Column(db.Integer, nullable=False)
	gone = db.Column(db.Integer, nullable=False)
	reason = db.Column(db.String(200), nullable=False)
	left = db.Column(db.Integer, nullable=False)
	date_added = (db.Column(db.String(200), default=currentTime("date"), nullable=False))
	time_added = db.Column(db.String(200), default=currentTime("both"), nullable=False)
	# Create a string

class UserData(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(200), nullable=False, unique=True)
	password = db.Column(db.String(200), nullable=False, unique=True)
	total_balance = db.Column(db.Integer, nullable=True)
	login_token = db.Column(db.String(300), nullable=False, unique=True)
	# Create a string

# Create a Form Class

def token_validator(username, token_to_verify):
	# clog(f"Trying to validate for {username}")
	user_from_db = UserData.query.filter_by(username=username).first()
	# print(f"TOKEN VERIFICATION: {token_to_verify} - {user_from_db.login_token.split('_')[1]}")
	try:
		if token_to_verify == user_from_db.login_token.split("_")[1]:
			# print("TOKEN MATCHED")
			# clog(f"Token matched for {username}")
			return True
		else:
			# clog(f"Token not matched for {username}")
			# print("TOKEN NOT MATCHED")
			return False
	except Exception:
		return False
class AccountManager:
	def __init__(self, username) -> None:
		self.username = username
		self.userdb = UserData.query.filter_by(username=username).first()
		clog(f"Account manager triggered for {username}")
		if str(self.userdb.total_balance) == "None":
			self.userdb.total_balance = 0
		db.session.commit()

	def addmoney(self, amount:int):
		if str(self.userdb.total_balance) == "None":
			self.userdb.total_balance = 0
		self.userdb.total_balance += amount
		db.session.commit()
		clog(f"Money added to {self.userdb.username}, amount: {amount}, current_balance: {self.userdb.total_balance}")
	def cutmoney(self, amount:int):
		if str(self.userdb.total_balance) == "None":
			self.userdb.total_balance = 0
		self.userdb.total_balance -= amount

		db.session.commit()
		clog(f"Money removed from {self.userdb.username}, amount: {amount}, current_balance: {self.userdb.total_balance}")
	def current_balance(self):
		clog(f"attempt to check current balance {self.userdb.total_balance}")
		if str(self.userdb.total_balance) == "None":
			self.userdb.total_balance = 0
		return self.userdb.total_balance




@app.route("/")
def index():
	return render_template("index.html")
@app.route("/create_account", methods=["GET", "POST"])
def create_account():
	status = request.cookies.get("status")
	if request.method == "POST":
		username = request.form['username']
		print(username)
		try:
			if UserData.query.filter_by(username=username).first() is None:
				print("New User")

				new_user = UserData(username=username, password=request.form['password'], login_token=f"{username}_{generate_key()}")
				db.session.add(new_user)
				db.session.commit()

				flash("Account created successfully")
				return render_template("login.html", status=status)
		except Exception as e:
			return render_template("login.html")
		else:
			print("Old User")
			flash("Choose another username")
			return render_template("createaccount.html")
	else:
		status = request.cookies.get("status")
		return render_template("createaccount.html", status=status)

@app.route("/create_transaction", methods=["POST", "GET"])
def view_database():
	status = request.cookies.get("status")
	try:
		token_data = request.cookies.get("token")
		username = token_data.split("_")[0]
		uLogin_token = token_data.split("_")[1]
		# print(uLogin_token)
	except Exception as error:
		flash("Login again")
		return render_template("login.html")
	if token_validator(username, uLogin_token):
		am = AccountManager(username)
		if request.method == "POST":
			form_data = request.form
			form_data = dict(form_data)
			# print(type(form_data))
			if transaction_validator(form_data):
				if form_data['transaction_type'] == "incomming":
					come_amount = form_data['transaction_ammount']
					out_ammount = 0
				else:
					out_ammount = form_data['transaction_ammount']

					come_amount = 0
				come_amount, out_ammount = int(come_amount), int(out_ammount)
				try:
					am.addmoney(come_amount)
					am.cutmoney(out_ammount)
				except Exception as error:
					return "Transaction not successful {}".format(error)
				transaction_data = Transaction(username=username, come=come_amount, gone=out_ammount,reason=form_data['transaction_reason'], left=am.current_balance())
				db.session.add(transaction_data)
				db.session.commit()
				flash("Transaction logged successfully")
				return render_template("create_transaction.html", status=status,tRid=rd(1000, 4000))
			else:
				flash("Invalid Transaction Details")
				return render_template("create_transaction.html", status=status, tRid=rd(1000, 4000))
				# return json.dumps(request.form, indent=4)
		else:
			return render_template("create_transaction.html", status=status, tRid=rd(1000, 4000), balance=UserData.query.filter_by(username='test').first())

	else:
		return "Unauthorized session"

	# database = Transaction.query.all()

@app.route("/myaccount")
def myaccount():
	status = request.cookies.get("status")
	try:
		token_data = request.cookies.get("token")
		username = token_data.split("_")[0]
		uLogin_token = token_data.split("_")[1]
		print(uLogin_token)
	except Exception as error:
		flash("Login again")
		return render_template("login.html")
	if token_validator(username, uLogin_token):

		am = AccountManager(username)
		return render_template("account.html",status=status, balance=am.current_balance())

	else:
		flash("Unauthorized session")
		return render_template("login.html")

@app.route("/transactions")
def transaction_manager():

	try:
		token_data = request.cookies.get("token")
		username = token_data.split("_")[0]
		uLogin_token = token_data.split("_")[1]
		status = request.cookies.get("status")
		print(uLogin_token)
	except Exception as error:
		flash("Login again")
		return render_template("login.html")
	if token_validator(username, uLogin_token):
		database = Transaction.query.filter_by(username=username)
		# am = AccountManager()
		return render_template("transaction.html",status=status, database=database)


	else:
		return "Unauthorized session"

@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		user_data_to_login = UserData.query.filter_by(username=request.form['username']).first()
		if user_data_to_login is not None:
			if user_data_to_login.password == request.form['password']:

				user_data_to_login.login_token = f"{user_data_to_login.username}_{generate_key()}"
				resp = make_response(redirect("/myaccount"))
				db.session.commit()
				resp.set_cookie("token", user_data_to_login.login_token)
				resp.set_cookie("status", "logged_in")
				return resp
			else:
				flash("Incorrent credentials")
				return render_template("login.html")
		else:
			return "User Not Found"
	return render_template("login.html")

@app.route("/logout", methods=["GET"])
def logout():
	if request.method == "GET":
		try:
			username_to_logout = request.cookies.get("token").split("_")[0]

		except Exception as error:
			print(error)
			resp = make_response(redirect("/login"))
			resp.set_cookie("status", "logged_out")
			return resp
		user_data_to_logout = UserData.query.filter_by(username=username_to_logout).first()
		if user_data_to_logout is not None:
			user_data_to_logout.login_token = generate_key()
			db.session.commit()
			resp = make_response(redirect("/login"))
			resp.set_cookie("status", "logged_out")
			return resp
		else:
			return "User Not Found"
@app.route("/dashboard")
def dashboard():
	try:
		status = request.cookies.get("status")
		token_data = request.cookies.get("token")
		username = token_data.split("_")[0]
		uLogin_token = token_data.split("_")[1]
		print(uLogin_token)
	except Exception as error:
		flash("Login again")
		return render_template("login.html")
	if token_validator(username, uLogin_token):
		today_user_data = Transaction.query.filter_by(username=username, date_added=currentTime("date")).all()
		user_dashboard = DashCalc(today_user_data)

		total_spent_today = user_dashboard.calculate_total_spent()
		total_income_today = user_dashboard.calculate_total_income()
		last_transaction_today = Transaction.query.filter_by(username=username, date_added=currentTime("date")).all()
		# print(len(last_transaction_today))
		try:
			last_transaction_today = last_transaction_today[len(last_transaction_today)-1]
			if last_transaction_today.gone == 0:
				print(last_transaction_today.gone)
				last_transaction_today = str(last_transaction_today.come) + " ( Incoming )"
			else:
				last_transaction_today = str(last_transaction_today.gone) + " ( Outgoing )"

		except IndexError:
			last_transaction_today = 0
		am = AccountManager(username)
		current_balance_today = am.current_balance()
		today_storage = TodayDashboard(total_spent=total_spent_today, total_income=total_income_today, current_balance=current_balance_today, last_transaction_today=last_transaction_today)
		return render_template("dashboard.html", today_storage=today_storage, status=status)
	else:
		flash("Unauthorized")
		return redirect("/")
@app.route("/testing")
def testing():
	username="admin"
	today_user_data = Transaction.query.filter_by(username=username, date_added=currentTime("date")).all()
	return render_template("testing.html", today_user_data=today_user_data)
@app.errorhandler(404)
def page_not_found(error):
	try:
		status = request.cookies.get("status")
	except Exception:
		status = None
	return render_template("404.html", status=status), 404
if __name__ == "__main__":
	app.run(debug=True, port=9992, host="0.0.0.0")