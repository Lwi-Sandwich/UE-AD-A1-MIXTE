# REST API
from flask import Flask, render_template, request, jsonify, make_response, send_from_directory
import requests
import json
import time
from werkzeug.exceptions import NotFound

#CALLING gRPC requests
import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc


app = Flask(__name__)

PORT = 3004
HOST = '0.0.0.0'

BOOKING_HOST = 'localhost:3002'
MOVIES_HOST = 'http://localhost:3001/graphql'

# Reading and writing to json file
with open('{}/data/users.json'.format("."), "r") as jsf:
	users = json.load(jsf)["users"]

def write(users):
	with open('{}/data/users.json'.format("."), 'w') as f:
		json.dump({'users':users}, f, indent=4)

# Swagger methods
@app.route('/docs', methods=['GET'])
def docs():
	return render_template('swagger_template.html')

@app.route('/specs', methods=['GET'])
def get_spec():
	return send_from_directory('.', 'user_swagger.yaml')

# REST API
@app.route("/", methods=['GET'])
def home():
	return render_template("user.html")

@app.route("/users", methods=['GET'])
def user():
	return make_response(jsonify(users), 200)

@app.route("/users/<userid>", methods=['POST'])
def add_user(userid):
	req = request.get_json()
	for u in users:
		if str(u['id']) == str(userid):
			return make_response(jsonify({'error': 'User ID already exists'}), 409)
	users['last_active'] = time.time()
	users.append(req)
	write(users)
	res = make_response(jsonify({"message":"user added"}),200)
	return res

@app.route('/users/<userid>', methods=['DELETE'])
def delete_user(userid):
	for u in users:
		if str(u['id']) == str(userid):
			users.remove(u)
			write(users)
			return make_response(jsonify(u), 200)
	return make_response(jsonify({'error': 'User not found'}), 400)

@app.route('/users/<userid>', methods=['GET'])
def user_id(userid):
	for u in users:
		if str(u['id']) == str(userid):
			return make_response(jsonify(u), 200)
	return make_response(jsonify({'error': 'User not found'}), 404)

@app.route('/bookings/<userid>', methods=['GET'])
def bookings_user(userid):
	try:
		# GRPC calls
		with grpc.insecure_channel(BOOKING_HOST) as channel:
			stub = booking_pb2_grpc.BookingStub(channel)
			bookings = stub.GetUserBookings(booking_pb2.UserID(id=userid))
			return make_response(jsonify({"userid": bookings.userid, "dates": [{"date": d.date, "movies": [i for i in d.movies]} for d in bookings.dates]}), 200)
	except Exception as e:
		return make_response(jsonify({"Error raised by bookings": str(e)}), 400)

@app.route('/movieinfos/<userid>', methods=['GET'])
def movieinfos_user(userid):
	try:
		# GRPC for bookings
		with grpc.insecure_channel(BOOKING_HOST) as channel:
			stub = booking_pb2_grpc.BookingStub(channel)
			bookings_request = stub.GetUserBookings(booking_pb2.UserID(id=userid))
	except Exception as e:
		return make_response(jsonify({"Error raised by bookings": str(e)}), 400)
	# Movies is in graphql
	movies_request = requests.post(MOVIES_HOST, json={"query": 'query{movies{id, title, rating, director}}'})
	if movies_request.status_code != 200:
		return make_response(jsonify({"Error raised by movies": str(e)}), 400)
	bookings = bookings_request
	movies = movies_request.json()['data']['movies']
	ids_in_bookings = [m for b in bookings.dates for m in b.movies]
	res = {"movies": [m for m in movies if m['id'] in ids_in_bookings]}
	return make_response(jsonify(res), 200)

@app.route("/bookings/<userid>", methods=['POST'])
def add_booking(userid):
	try:
		with grpc.insecure_channel(BOOKING_HOST) as channel:
			stub = booking_pb2_grpc.BookingStub(channel)
			req = request.get_json()
			bookings = stub.AddBooking(booking_pb2.NewBookingInfo(userid=userid, date=req['date'], movieid=req['id']))
			users['last_active'] = time.time()
			write(users)
			return make_response(jsonify({"userid": bookings.userid, "dates": [{"date": d.date, "movies": [i for i in d.movies]} for d in bookings.dates]}), 200)
	except Exception as e:
		return make_response(jsonify({"Error raised by bookings": str(e)}), 400)

if __name__ == "__main__":
	print("Server running in port %s"%(PORT))
	app.run(host=HOST, port=PORT)