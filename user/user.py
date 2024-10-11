# REST API
from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

#CALLING gRPC requests
import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import movie_pb2
import movie_pb2_grpc

# CALLING GraphQL requests
# todo to complete

app = Flask(__name__)

PORT = 3004
HOST = '0.0.0.0'

BOOKING_HOST = 'http://localhost:3002/bookings/'
MOVIES_HOST = 'http://localhost:3001/graphql'

with open('{}/data/users.json'.format("."), "r") as jsf:
	users = json.load(jsf)["users"]

@app.route("/", methods=['GET'])
def home():
	return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users", methods=['GET'])
def user():
	return make_response(jsonify(users), 200)

@app.route("/users/<userid>", methods=['POST'])
def add_user(userid):
    req = request.get_json()
    for u in users:
        if str(u['id']) == str(userid):
            return make_response(jsonify({'error': 'User ID already exists'}), 409)
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
            return make_response(jsonify({'message': 'Deleted successfully'}), 200)
    return make_response(jsonify({'error': 'User not found'}), 400)

def write(users):
    with open('{}/data/users.json'.format("."), 'w') as f:
        json.dump({'users':users}, f, indent=4)
@app.route('/users/<userid>', methods=['GET'])
def user_id(userid):
	for u in users:
		if str(u['id']) == str(userid):
			return make_response(jsonify(u), 200)
	return make_response(jsonify({'error': 'bad input parameter'}), 400)

@app.route('/bookings/<userid>', methods=['GET'])
def bookings_user(userid):
	try:
        with grpc.insecure_channel(BOOKING_HOST) as channel:
            stub = booking_pb2_grpc.BookingStub(channel)
            bookings = stub.GetUserBookings(showtime_pb2.GetUserBookings(UserID=userid))
    except Exception as e:
        print(e)
        return booking_pb2.UserBooking(userid="", dates="")

@app.route('/movieinfos/<userid>', methods=['GET'])
def movieinfos_user(userid):
	try:
        with grpc.insecure_channel(BOOKING_HOST) as channel:
            stub = booking_pb2_grpc.BookingStub(channel)
            bookings_request = stub.GetUserBookings(booking_pb2.GetUserBookings(UserID=userid))
    except Exception as e:
        print(e)
        return make_response(jsonify({'error': 'bad input parameter'}), 400)
	#bookings_request = requests.get(BOOKING_HOST + str(userid))
	movies_request = requests.post(MOVIES_HOST, json={"query": 'query{movies{id, title, rating, director}}'})
	if movies_request.status_code != 200:
		return make_response(jsonify({'error': 'bad input parameter'}), 400)
	bookings = bookings_request
	movies = movies_request.json()
	ids_in_bookings = [m for b in bookings.dates for m in b.movies]
	res = {"movies": [m for m in movies if m['id'] in ids_in_bookings]}
	return make_response(jsonify(res), 200)

@app.route("/bookings/<userid>", methods=['POST'])
def add_booking(userid):
	try:
        with grpc.insecure_channel(BOOKING_HOST) as channel:
            stub = booking_pb2_grpc.BookingStub(channel)
            bookings_request = stub.AddBooking(booking_pb2.AddBooking(userid=userid, date=request.date, movie=request.movie))
    except Exception as e:
        print(e)
        return make_response(jsonify({'error': 'bad input parameter'}), 400)
	

if __name__ == "__main__":
	print("Server running in port %s"%(PORT))
	app.run(host=HOST, port=PORT)