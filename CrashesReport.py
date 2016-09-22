#!/usr/bin/env python
import requests
import json
from datetime import datetime, timedelta
import argparse
from twilio.rest import TwilioRestClient
import gspread
from collections import OrderedDict
from oauth2client.service_account import ServiceAccountCredentials

"""
Don't Forget to Install all the following libs
"""

__author__ = 'Dor Raviv'
__copyright__ = 'Cortica 2016'
__version__ = '1.0.6'
__date__ = 'September 2016'
__status__ = 'Development'
__AppName__ = 'Automated ReDiscover Reports'

# Scopes & Paths
SCOPE = ['https://spreadsheets.google.com/feeds']
CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_name('My Project-b859a37d5397.json', SCOPE)
REQUEST_URL_SESSIONS = 'https://api.appsee.com/sessions'
REQUEST_URL_Crashes = 'https://api.appsee.com/crashes/daily'
REQUEST_URL_EVENTS = 'https://api.appsee.com/events'
TWILIO_URI = 'https://api.twilio.com/'

# Credentials- AppSee
API_SECRET = '73f95ae4f566490ba8ba89bef0f6e5ea'
REDISCOVER_API_KEY = 'f0778e55f1ef404a99cc145c849bc69a'
REDISCOVER_TEST_API_KEY = 'c6108dff05424ccfb061bb6549a10d75'

# Credentials- Twilio
FRIENDLYNAME = 'CorticaDev'
SID = 'SKf2f93274a914a96a21ec5ce153283495'
ACCOUNTSID = 'ACd8edd7feb9cb5bddb1e8bdcef0a19014'
SECRET = 'IZK8UdTrPZgdK41BAy5zc6ckQJawaFrK'
AUTH_TOKEN = '7f5b017bfc9916f3b353f0bbf81f3777'
# Credentials- AppsFlyer
APPSFLYER_API = '0a067baa-4639-4f5d-9099-75461a1f3d2f '


# AppSee API Request Sender & Results Parser Based on Dates, Sessions, Users etc'...
# Please Check out https://www.appsee.com/docs/serverapi for further documentation.
# You can Choose whatever you want: Sessions / Usage / Analytics etc. Just Change in the following REQUEST_URL.

# Defining Class For Different Date Formats


class Yesterday:
    def __init__(self):
        # TODO: Remember to change Day=1- Done
        self.Date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.DateForSheet_first = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%y")
        self.DateForSheet_second = (datetime.now() - timedelta(days=1)).strftime("%m/%d/%y")


def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--input", action="store", default='PhoneList.csv',
                        help="path to PhoneNumber input")
    parser.add_argument("-l", "--locations", action="store", default="locations.txt",
                        help="path to location input")
    # TODO: Delete the Output file
    parser.add_argument("-o", "--output", action="store", default='Results.txt',
                        help="path to output")
    args = parser.parse_args()
    return args


def reading_phone_numbers():
    with open(args.input, 'r') as input:
        for i in input:
            uid = str(i).split(',')[0]
            number = (str(i).split(',')[1]).strip('\n')
            dict_for_numbers.setdefault(uid, number)


def reading_locations():
    with open(args.locations, 'r') as input:
        for i in input:
            con = str(i).split('\t')[0]
            temp_location = (str(i).split('\t')[1]).strip('\n')
            dict_for_locations.setdefault(temp_location, con)


def login_to_sheet():
    try:
        print 'Attempting To Connect...'
        gc = gspread.authorize(CREDENTIALS)
        print '...Authenticated!'
        spread_sheet = gc.open("ReDiscover reports")
    except Exception as err:
        print "Unable to Connect to Sheet. Please Check Credentials.. Error " + str(err)
    return spread_sheet


def update_crashes_sheet(date_for_sheet_first, date_for_sheet_second, unique_sessions, sessions, crashes):
    try:
        crashes_sheet = login_to_sheet().worksheet("Crashes")
        # Updating Data on SpreadSheet, First Available Row...
        content = crashes_sheet.get_all_values()
        row_number = len([row for row in content]) + 1
        crashes_sheet.update_cell(row_number, 1, date_for_sheet_first)
        crashes_sheet.update_cell(row_number, 2, date_for_sheet_second)
        crashes_sheet.update_cell(row_number, 3, unique_sessions)
        crashes_sheet.update_cell(row_number, 4, sessions)
        crashes_sheet.update_cell(row_number, 5, crashes)
        print "Finished Updating Sheet: Crashes"
    except Exception as ex:
        print 'There Was An Error Updating SpreadSheet Crashes!\nThe Error Is: ' + str(ex)


def update_Distribution_index_ios(date_for_sheet_first, date_for_sheet_second, yesterday_Users,
                                  yesterday_FirstPeopleReceived,
                                  yesterday_QuickFilterPeople,
                                  yesterday_Event_FaceClick, yesterday_Event_FaceRename,
                                  yesterday_Event_FaceAutoShare):
    try:
        Distribution_index_ios = login_to_sheet().worksheet("Distribution_index_ios")
        content = Distribution_index_ios.get_all_values()
        row_number = len([row for row in content]) + 1
        # Updating Cells In the Selected Sheet
        Distribution_index_ios.update_cell(row_number, 1, date_for_sheet_first)
        Distribution_index_ios.update_cell(row_number, 2, date_for_sheet_second)
        Distribution_index_ios.update_cell(row_number, 3, yesterday_Users)
        Distribution_index_ios.update_cell(row_number, 4, yesterday_FirstPeopleReceived)
        Distribution_index_ios.update_cell(row_number, 5, yesterday_QuickFilterPeople)
        Distribution_index_ios.update_cell(row_number, 6, yesterday_Event_FaceClick)
        Distribution_index_ios.update_cell(row_number, 7, yesterday_Event_FaceRename)
        Distribution_index_ios.update_cell(row_number, 8, yesterday_Event_FaceAutoShare)
        print "Finished Updating Sheet: Distribution_index_ios"
    except Exception as ex:
        print 'There Was An Error Updating SpreadSheet Distribution_index_ios!\nThe Error Is: ' + str(ex)


def update_Distribution_index_ios_Unique(date_for_sheet_first, date_for_sheet_second, yesterday_Users_Unique,
                                         yesterday_FirstPeopleReceivedUnique, yesterday_QuickFilterPeopleUnique,
                                         yesterday_Event_FaceClickUnique, yesterday_Event_FaceRename_Unique,
                                         yesterday_Event_FaceAutoShareUnique, number_of_sms_twilio):
    try:
        Distribution_index_ios_unique = login_to_sheet().worksheet("Distribution_index_ios_unique")
        content = Distribution_index_ios_unique.get_all_values()
        row_number = len([row for row in content]) + 1
        # Updating Cells In the Selected Sheet
        Distribution_index_ios_unique.update_cell(row_number, 1, date_for_sheet_first)
        Distribution_index_ios_unique.update_cell(row_number, 2, date_for_sheet_second)
        Distribution_index_ios_unique.update_cell(row_number, 3, yesterday_Users_Unique)
        Distribution_index_ios_unique.update_cell(row_number, 4, yesterday_FirstPeopleReceivedUnique)
        Distribution_index_ios_unique.update_cell(row_number, 5, yesterday_QuickFilterPeopleUnique)
        Distribution_index_ios_unique.update_cell(row_number, 6, yesterday_Event_FaceClickUnique)
        Distribution_index_ios_unique.update_cell(row_number, 7, yesterday_Event_FaceRename_Unique)
        Distribution_index_ios_unique.update_cell(row_number, 8, yesterday_Event_FaceAutoShareUnique)
        Distribution_index_ios_unique.update_cell(row_number, 9, number_of_sms_twilio)
        print "Finished Updating Sheet: Distribution_index_ios_unique"
    except Exception as ex:
        print 'There Was An Error Updating SpreadSheet Distribution_index_ios_unique!\nThe Error Is: ' + str(ex)


def parse_users(result_total):
    js = json.loads(result_total)
    ids_container = []
    for session in js['Sessions']:
        try:
            id = session['UserId']
            location = session['Location']['Description']
            # Since AppSee uses UTC Time format in their JSON & it has +3 hours to Local Time, Adding This prevents
            # Drifting users from different days.
            startTime = session['StartTime']
            appseeTimeFormat = datetime.strptime(startTime, "%Y-%m-%dT%H:%M:%S") + timedelta(hours=3)
            myTimeFormat = "%Y-%m-%d"
            newTime = appseeTimeFormat.strftime(myTimeFormat)
            # Making sure The Users Aren't from Cortica's Contact List/ Locations
            if id not in dict_for_numbers and location not in dict_for_locations:
                if newTime == Yesterday().Date:
                    ids_container.append(id)
        except Exception as ee:
            print str(ee)
    print ids_container
    return len(ids_container), len(set(ids_container))


def parse_crashes(result_crashes):
    js = json.loads(result_crashes)
    external_users_crashes_counter = 0
    for crashed in js['Sessions']:
        try:
            id = crashed['UserId']
            location = crashed['Location']['Description']
            if id not in dict_for_numbers and location not in dict_for_locations:
                external_users_crashes_counter += 1
        except Exception as eee:
            print str(eee)
    return external_users_crashes_counter


# Special Event- Occurs only on New Installations of the app
def get_first_people_received_list():
    page = 1
    ids_container = []
    total_list = OrderedDict()
    # Iterate through all of the sessions from 11/9/2016 where we had first implemented First People Event.
    # Appending all of the userId's into a single list of users
    while True:
        url_template = '?apikey=' + REDISCOVER_API_KEY + \
                       '&apisecret=' + API_SECRET + '&platform=iOS&appversion=2.4.1&fromdate=2016-09-11' + \
                       '&todate=' + Yesterday().Date
        url_for_parsing = REQUEST_URL_SESSIONS + url_template + '&page=%d' % page
        request_json = requests.get(url_for_parsing).text
        js = json.loads(request_json)
        if len(js['Sessions']) == 0:
            break
        else:
            try:
                sessions = js['Sessions']
                for session in sessions:
                    try:
                        id = session['UserId']
                        location = session['Location']['Description']
                        if id not in dict_for_numbers and location not in dict_for_locations:
                            # Some Sessions from the past Doesn't have Events.
                            try:
                                events = session['Events']
                                # Event: First People Received
                                for event in events:
                                    if event['Name'] == 'First People Received':
                                        ids_container.append(id)
                                        break
                            except Exception as err:
                                pass
                    except Exception as err:
                        print "An Error occurred while parsing First People Received! Check: " + str(err)
            except Exception as err:
                print "No Sessions... Check " + str(err)
                pass
            page += 1
        total_list = ids_container
    return total_list


def parse_event_first_people_received(result_total, unique_user_id_list):
    js = json.loads(result_total)
    id_list = []
    sessions = js['Sessions']
    for session in sessions:
        userId = session['UserId']
        try:
            events = session['Events']
            for event in events:
                if event['Name'] == 'First People Received':
                    id_list.append(userId)
                    break
        except Exception as err:
            print "Had An Issue retrieving the final \"First People Received\" Event! Check Out: " + str(err)
    print len(id_list)
    return len(id_list), len(set(id_list))


def parse_event_face_click(result_events):
    js = json.loads(result_events)
    sessions = js['Sessions']
    ids_container = []
    for session in sessions:
        try:
            id = session['UserId']
            location = session['Location']['Description']
            if id not in dict_for_numbers and location not in dict_for_locations:
                events = session['Events']
                # Event: First People Received
                for event in events:
                    event_name = 'face click'
                    if event['Name'] == event_name:
                        ids_container.append(id)
                        break
        except Exception as err:
            print "An Error occurred! Event FaceClick: " + str(err)
    return len(ids_container), len(set(ids_container))


def parse_event_quick_filter_people(result_events):
    js = json.loads(result_events)
    sessions = js['Sessions']
    idsContainer = []
    for session in sessions:
        try:
            id = session['UserId']
            location = session['Location']['Description']
            if id not in dict_for_numbers and location not in dict_for_locations:
                events = session['Events']
                # Event: First People Received
                for event in events:
                    if event['Name'] == 'quickfilter selected':
                        if event['Properties']['quickfilter'] == 'People':
                            idsContainer.append(id)
                            break
        except Exception as err:
            print "An Error occurred! Quick Filter: People: " + str(err)
    return len(idsContainer), len((set(idsContainer)))


def parse_event_face_rename(result_events):
    js = json.loads(result_events)
    sessions = js['Sessions']
    idsContainer = []
    for session in sessions:
        try:
            id = session['UserId']
            location = session['Location']['Description']
            if id not in dict_for_numbers and location not in dict_for_locations:
                events = session['Events']
                # Event: First People Received
                for event in events:
                    event_name = 'face rename'
                    if event['Name'] == event_name:
                        idsContainer.append(id)
                        break
        except Exception as err:
            print "An Error occurred! Event: Face Rename: " + str(err)
    return len(idsContainer), len(set(idsContainer))


def parse_event_auto_share(result_events):
    js = json.loads(result_events)
    sessions = js['Sessions']
    idsContainer = []
    for session in sessions:
        try:
            id = session['UserId']
            location = session['Location']['Description']
            if id not in dict_for_numbers and location not in dict_for_locations:
                events = session['Events']
                # Event: First People Received
                for event in events:
                    if event['Name'] == 'face autoshare':
                        idsContainer.append(id)
                        break
        except Exception as err:
            print "An Error occurred! Event: Face Auto share: " + str(err)
    return len(idsContainer), len(set(idsContainer))


def number_of_messages_twilio():
    # TODO: Finish Pagination using NextPageUri- Currently only returns First Page
    try:
        client = TwilioRestClient(ACCOUNTSID, AUTH_TOKEN)
        messages = client.messages.list()
        clients_container = []
        for message in messages:
            to = message.to
            sms_sent_time = message.date_sent.strftime("%Y-%m-%d")
            if to not in dict_for_numbers and str(sms_sent_time) == Yesterday().Date:
                if message.status == 'delivered':
                    clients_container.append(to)
    except Exception as err:
        print "Error Getting Messages from Twilio.com. Please Check out: " + str(err)
    return len(clients_container)


if __name__ == "__main__":
    args = setup()
    dict_for_numbers = {}
    dict_for_locations = {}
    yesterdayResults = OrderedDict()
    try:
        # Fetching Data to Exclude
        reading_phone_numbers()
        reading_locations()
        # You can choose which Platform (Android/iOS), App version, UserID
        url_Template = '?apikey=' + REDISCOVER_API_KEY + \
                       '&apisecret=' + API_SECRET + '&platform=iOS&appversion=2.4.1&fromdate=' + Yesterday().Date + \
                       '&todate=' + Yesterday().Date
        # Initiating Counter For this Run!
        currentPage = 1
        yesterday_Sessions = 0
        yesterday_Users_Unique = 0
        yesterday_Crashes = 0
        yesterday_FirstPeopleReceived = 0
        yesterday_FirstPeopleReceivedUnique = 0
        yesterday_QuickFilterPeople = 0
        yesterday_QuickFilterPeopleUnique = 0
        yesterday_Event_FaceClick = 0
        yesterday_Event_FaceClickUnique = 0
        yesterday_Event_FaceRename = 0
        yesterday_Event_FaceRename_Unique = 0
        yesterday_Event_FaceAutoShare = 0
        yesterday_Event_FaceAutoShareUnique = 0
        while True:
            request_url_Sessions = REQUEST_URL_SESSIONS + url_Template + '&page=%d' % currentPage
            request_url_Crashes = REQUEST_URL_SESSIONS + url_Template + '&crashed=true'
            request_url_Events = REQUEST_URL_SESSIONS + url_Template \
                                 + '&eventname=quickfilter%20selected&property=quickfilter' + '&page=%d' % currentPage

            # Getting Results from AppSee Api...

            result_Total = requests.get(request_url_Sessions).text
            result_Crashes = requests.get(request_url_Crashes).text
            result_Events = requests.get(request_url_Events).text
            pagination = json.loads(result_Total)

            # If No More Sessions, Don't run all of the Functions! Quit ASAP!
            if len(pagination['Sessions']) == 0:
                break
            else:

                # Parsing How Many Users, Unique Users & Crashes
                current_users, current_unique_users = parse_users(result_Total)
                yesterday_Sessions += current_users
                yesterday_Users_Unique += current_unique_users
                # Parsing Crashes
                yesterday_Crashes = parse_crashes(result_Crashes)
                # Parsing Event: First People Received
                currentFirstPeopleReceived, currentUniqueFirstPeopleReceived = parse_event_first_people_received(
                        result_Total, get_first_people_received_list())
                yesterday_FirstPeopleReceived += currentFirstPeopleReceived
                yesterday_FirstPeopleReceivedUnique += currentUniqueFirstPeopleReceived
                # Parsing Event: QuickFilter People
                currentQuickFilterPeople, currentQuickFilterPeopleUnique = parse_event_quick_filter_people(
                        result_Events)
                yesterday_QuickFilterPeople += currentQuickFilterPeople
                yesterday_QuickFilterPeopleUnique += currentQuickFilterPeopleUnique
                # Parsing Event: Face Click
                currentEventFaceClick, currentEventFaceclickUnique = parse_event_face_click(result_Events)
                yesterday_Event_FaceClick += currentEventFaceClick
                yesterday_Event_FaceClickUnique += currentEventFaceclickUnique
                # Parsing Event: Face Rename
                currentEventFaceRename, currentEventFaceRenameUnique = parse_event_face_rename(result_Events)
                yesterday_Event_FaceRename += currentEventFaceRename
                yesterday_Event_FaceRename_Unique += currentEventFaceRenameUnique
                # Parsing EventL Face AutoShare
                current_Event_FaceAutoshare, current_Event_FaceAutoshareUnique = parse_event_auto_share(result_Events)
                yesterday_Event_FaceAutoShare += current_Event_FaceAutoshare
                yesterday_Event_FaceAutoShareUnique += current_Event_FaceAutoshareUnique

            currentPage += 1
        # Updating SpreadSheet According to Results
        # update_crashes_sheet(Yesterday().DateForSheet_first, Yesterday().DateForSheet_second, yesterday_Users_Unique,
        #                      yesterday_Sessions, yesterday_Crashes)
        # update_Distribution_index_ios(Yesterday().DateForSheet_first, Yesterday().DateForSheet_second,
        #                               yesterday_Sessions, yesterday_FirstPeopleReceived,
        #                               yesterday_QuickFilterPeople, yesterday_Event_FaceClick,
        #                               yesterday_Event_FaceRename,
        #                               yesterday_Event_FaceAutoShare)
        # update_Distribution_index_ios_Unique(Yesterday().DateForSheet_first, Yesterday().DateForSheet_second,
        #                                      yesterday_Users_Unique,
        #                                      yesterday_FirstPeopleReceivedUnique, yesterday_QuickFilterPeopleUnique,
        #                                      yesterday_Event_FaceClickUnique, yesterday_Event_FaceRename_Unique,
        #                                      yesterday_Event_FaceAutoShareUnique, number_of_messages_twilio())

        # TODO: Delete Debugging Prints Prior To Upload
        print str(Yesterday().DateForSheet_first) + " First Date Format"
        print str(Yesterday().DateForSheet_second) + " Second Date Format"
        print str(yesterday_Sessions) + " Total External Sessions"
        print str(yesterday_Users_Unique) + " Total External Users- Unique!"
        print str(yesterday_Crashes) + " Total Users Crashes"
        print str(yesterday_FirstPeopleReceived) + " First People Received"
        print str(yesterday_QuickFilterPeople) + " QuickFilter People"
        print str(yesterday_Event_FaceClick) + " Event: Face Click"
        print str(yesterday_Event_FaceRename) + " Event: FaceRename"
        print str(yesterday_Event_FaceAutoShare) + " Event: FaceAutoShare"
        print str(number_of_messages_twilio()) + " Number of Messages- Twilio.com"
        print 'Done!'
    except Exception as e:
        print "An Issue rose in the Main Function.. Something is Wrong. It might be " + str(e)
