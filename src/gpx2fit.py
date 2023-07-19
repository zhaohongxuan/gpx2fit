
import gpxpy
from geopy.distance import geodesic

from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.event_message import EventMessage
from fit_tool.profile.messages.lap_message import LapMessage
from fit_tool.profile.messages.activity_message import ActivityMessage
from fit_tool.profile.messages.session_message import SessionMessage
from fit_tool.profile.messages.device_info_message import DeviceInfoMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.record_message import RecordMessage
from fit_tool.profile.profile_type import (
    FileType,
    TimerTrigger,
    Event,
    EventType,
    LapTrigger,
    Sport,
    EventType,
    SubSport,
    SessionTrigger,
)

MANUFACTURER = 1  # Garmin
GARMIN_DEVICE_PRODUCT_ID = 3415  # Forerunner 245
GARMIN_SOFTWARE_VERSION = 3.58
# The device serial number must be real Garmin will identify device with it
# here the default number:1234567890 Garmin will recognize it as Forerunner 245
GARMIN_DEVICE_SERIAL_NUMBER = 1234567890

Sport.RUNNING


def gpx2fit(gpx_file_path, sport=Sport.RUNNING, sub_sport=SubSport.GENERIC):
    builder = FitFileBuilder(auto_define=True, min_string_size=50)
    # Read position data from a GPX file
    gpx_file = open(gpx_file_path, "r")
    gpx = gpxpy.parse(gpx_file,"1.1")

    time_create = gpx.time.timestamp() * 1000
    message = FileIdMessage()
    message.local_id = 0
    message.type = FileType.ACTIVITY
    message.manufacturer = MANUFACTURER
    message.product = GARMIN_DEVICE_PRODUCT_ID
    message.time_created = time_create
    message.serial_number = GARMIN_DEVICE_SERIAL_NUMBER
    builder.add(message)

    message = DeviceInfoMessage()
    message.local_id = 1
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
    message.local_id = 2
    message.event = Event.TIMER
    message.event_type = EventType.START
    message.event_group = 0
    message.timer_trigger = TimerTrigger.MANUAL
    message.timestamp = time_create

    builder.add(message)

    distance = 0.0
    timestamp = time_create
    records = []

    prev_coordinate = None
    
    for track in gpx.tracks:
        # an activity at least contain one lap
        # TODO handle lap Message

        total_distance = 0.0
        # todo session Message
        message = SessionMessage()

        for segment in track.segments:
            for index, track_point in enumerate(segment.points):
                current_coordinate = (track_point.latitude, track_point.longitude)
                # calculate distance from previous coordinate and accumulate distance
                if prev_coordinate:
                    delta = geodesic(prev_coordinate, current_coordinate).meters
                else:
                    delta = 0.0
                distance += delta
                total_distance = distance
                message = RecordMessage()
                message.local_id = 3
                message.position_lat = track_point.latitude
                message.position_long = track_point.longitude
                message.distance = distance
                message.altitude = track_point.elevation
                message.timestamp = track_point.time.timestamp() * 1000
                records.append(message)
                prev_coordinate = current_coordinate
        # Lap Message
        message = LapMessage()
        message.timestamp = timestamp
        message.local_id = 4
        message.message_index = 0
        message.lap_trigger = LapTrigger.SESSION_END
        message.event = Event.LAP
        message.event_type = EventType.STOP
        message.sport = sport

        start_point = track.segments[0].points[0]
        end_point = track.segments[0].points[-1]

        message.start_time = start_point.time.timestamp() * 1000
        elapsed_time = end_point.time.timestamp() - start_point.time.timestamp()

        message.total_elapsed_time = elapsed_time
        message.total_timer_time = elapsed_time

        message.start_position_lat = start_point.latitude
        message.start_position_long = start_point.longitude

        message.end_position_lat = end_point.latitude
        message.endPositionLong = end_point.longitude
        message.total_distance = total_distance
        builder.add(message)

        # session Message
        message = SessionMessage()
        message.local_id = 5
        message.timestamp = timestamp

        start_point = track.segments[0].points[0]
        end_point = track.segments[0].points[-1]

        message.start_time = start_point.time.timestamp() * 1000
        elapsed_time = end_point.time.timestamp() - start_point.time.timestamp()

        message.total_elapsed_time = elapsed_time
        message.total_timer_time = elapsed_time

        message.start_position_lat = start_point.latitude
        message.start_position_long = start_point.longitude

        message.sport = sport
        message.sub_sport = sub_sport
        message.first_lap_index = 0
        message.num_laps = 1
        message.trigger = SessionTrigger.ACTIVITY_END
        message.event = Event.SESSION
        message.event_type = EventType.STOP

        message.end_position_lat = end_point.latitude
        message.endPositionLong = end_point.longitude
        message.total_distance = total_distance
        builder.add(message)

        # activity Message
        message = ActivityMessage()
        message.local_id = 6
        message.num_sessions = 1
        message.event = Event.ACTIVITY
        message.event_type = EventType.STOP
        message.timestamp = timestamp

        start_point = track.segments[0].points[0]
        end_point = track.segments[0].points[-1]

        message.start_time = start_point.time.timestamp() * 1000
        elapsed_time = end_point.time.timestamp() - start_point.time.timestamp()

        message.total_timer_time = elapsed_time
        builder.add(message)

    builder.add_all(records)

    message = EventMessage()
    message.local_id = 2
    message.event = Event.TIMER
    message.event_type = EventType.STOP
    message.event_group = 0
    message.timer_trigger = TimerTrigger.MANUAL
    message.timestamp = timestamp
    builder.add(message)

    fit_file = builder.build()

    out_path = "/Users/hank.zhao/Developer/gpx2fit/data/output.fit"
    fit_file.to_file(out_path)
    csv_path = "/Users/hank.zhao/Developer/gpx2fit/data/output.csv"
    fit_file.to_csv(csv_path)


if __name__ == "__main__":
    gpx2fit("/Users/hank.zhao/Developer/gpx2fit/data/origin/Test_Run.gpx")
