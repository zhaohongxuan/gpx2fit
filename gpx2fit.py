import datetime

import gpxpy
import math
from geopy.distance import geodesic

from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.event_message import EventMessage
from fit_tool.profile.messages.lap_message import LapMessage
from fit_tool.profile.messages.device_info_message import DeviceInfoMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.record_message import RecordMessage
from fit_tool.profile.profile_type import FileType, Manufacturer, Event, EventType

MANUFACTURER = 1  # Garmin
GARMIN_DEVICE_PRODUCT_ID = 3415  # Forerunner 245
GARMIN_SOFTWARE_VERSION = 3.58
# The device serial number must be real Garmin will identify device with it
# here the default number:1234567890 Garmin will recognize it as Forerunner 245
GARMIN_DEVICE_SERIAL_NUMBER = 1234567890


def gpx2fit(gpx_file_path):

    builder = FitFileBuilder(auto_define=True, min_string_size=50)
    # Read position data from a GPX file
    gpx_file = open(gpx_file_path, 'r')
    gpx = gpxpy.parse(gpx_file)

    time_create  = gpx.time.timestamp()*1000
    message = FileIdMessage()
    message.type = FileType.ACTIVITY
    message.manufacturer = MANUFACTURER
    message.product = GARMIN_DEVICE_PRODUCT_ID
    message.time_created = time_create
    message.serial_number = GARMIN_DEVICE_SERIAL_NUMBER
    builder.add(message)
    
    message = DeviceInfoMessage()
    # the serial number must be real, otherwise Garmin will not identify it
    message.serial_number = GARMIN_DEVICE_SERIAL_NUMBER
    message.manufacturer = MANUFACTURER
    message.garmin_product = GARMIN_DEVICE_PRODUCT_ID
    message.software_version = GARMIN_SOFTWARE_VERSION
    message.device_index = 0
    message.source_type = 5
    message.product = GARMIN_DEVICE_PRODUCT_ID
    builder.add(message)

    # start event
    message = EventMessage()
    message.event = Event.TIMER
    message.event_type = EventType.START
    message.timestamp = time_create
    builder.add(message)

    distance = 0.0
    timestamp = time_create
    records = []

    prev_coordinate = None
    for track in gpx.tracks:
        # TODO handle lap Message 
        # message  = LapMessage()
        for segment in track.segments:
            for index, track_point in enumerate(segment.points):
                current_coordinate = (track_point.latitude, track_point.longitude)
                # calculate distance from previous coordinate and accumulate distance
                if prev_coordinate:
                    delta = geodesic(prev_coordinate, current_coordinate).meters
                else:
                    delta = 0.0
                distance += delta

                message = RecordMessage()
                message.position_lat = track_point.latitude
                message.position_long = track_point.longitude
                message.distance = distance
                message.grade = track_point.elevation
                message.timestamp = track_point.time.timestamp()*1000
                records.append(message)
                prev_coordinate = current_coordinate
            
    builder.add_all(records)

    message = EventMessage()
    message.event = Event.TIMER
    message.event_type = EventType.STOP
    message.timestamp = timestamp
    builder.add(message)

    fit_file = builder.build()

    out_path = '/Users/hank.zhao/Developer/gpx2fit/data/test.fit'
    fit_file.to_file(out_path)
    csv_path = '/Users/hank.zhao/Developer/gpx2fit/data/test.csv'
    fit_file.to_csv(csv_path)

if __name__ == "__main__":
    gpx2fit("/Users/hank.zhao/Developer/gpx2fit/data/test.gpx")
