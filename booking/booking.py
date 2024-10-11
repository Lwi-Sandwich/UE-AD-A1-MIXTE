import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import json

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
        # TODO check showtime
        for b in self.db:
            if b['userid'] == request.userid:
                for d in b['dates']:
                    if d['date'] == request.date:
                        if request.movieid not in d['movies']:
                            d['movies'].append(request.movieid)
                        write(self.db)
                        return booking_pb2.UserBooking(userid=b['userid'], dates=[booking_pb2.Date(date=i['date'], movies=i["movies"]) for i in b['dates']])
                    b['dates'].append({'date': request.date, 'movies': [request.movieid]})
                    write(self.db)
                    return booking_pb2.UserBooking(userid=b['userid'], dates=[booking_pb2.Date(date=i['date'], movies=i["movies"]) for i in b['dates']])
        b = {'userid': request.userid, "dates": [{'date': request.date, 'movies': [request.movieid]}]}
        self.db.append(b)
        write(self.db)
        print("aaa")
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
