import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import showtime_pb2
import showtime_pb2_grpc
import json

SHOWTIME = "localhost:3003"

class BookingServicer(booking_pb2_grpc.BookingServicer):

    def __init__(self):
        with open('{}/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["bookings"]

    def GetAllBookings(self, request, context):
        for b in self.db:
            yield booking_pb2.UserBooking(userid=b['userid'], dates=[booking_pb2.Date(date=i['date'], movies=i["movies"]) for i in b['dates']])

    def GetUserBookings(self, request, context):
        for b in self.db:
            if b['userid'] == request.id:
                return booking_pb2.UserBooking(userid=b['userid'], dates=[booking_pb2.Date(date=i['date'], movies=i["movies"]) for i in b['dates']])
        return booking_pb2.UserBooking(userid='', dates=[])

    def AddBooking(self, request, context):
        # Check showtime
        try:
            with grpc.insecure_channel(SHOWTIME) as channel:
                stub = showtime_pb2_grpc.ShowtimeStub(channel)
                time = stub.GetShowtimeByDate(showtime_pb2.ShowtimeDate(date=request.date))
                # Return empty booking if failed
                if request.movieid not in time.movies:
                    return booking_pb2.UserBooking(userid='', dates=[])
        except Exception:
            return booking_pb2.UserBooking(userid='', dates=[])
        # Goal is to find user to see if creating one is needed
        for b in self.db:
            if b['userid'] == request.userid:
                # See if we need to create a date in db
                for d in b['dates']:
                    if d['date'] == request.date:
                        if request.movieid not in d['movies']:
                            d['movies'].append(request.movieid)
                        write(self.db)
                        return booking_pb2.UserBooking(userid=b['userid'], dates=[booking_pb2.Date(date=i['date'], movies=i["movies"]) for i in b['dates']])
                    b['dates'].append({'date': request.date, 'movies': [request.movieid]})
                    write(self.db)
                    return booking_pb2.UserBooking(userid=b['userid'], dates=[booking_pb2.Date(date=i['date'], movies=i["movies"]) for i in b['dates']])
        # Does not exist, create user
        b = {'userid': request.userid, "dates": [{'date': request.date, 'movies': [request.movieid]}]}
        self.db.append(b)
        write(self.db)
        return booking_pb2.UserBooking(userid=b['userid'], dates=[booking_pb2.Date(date=i['date'], movies=i["movies"]) for i in b['dates']])

def write(bookings):
	with open('{}/data/bookings.json'.format("."), 'w') as f:
		json.dump({'bookings':bookings}, f, indent=4)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3002')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
