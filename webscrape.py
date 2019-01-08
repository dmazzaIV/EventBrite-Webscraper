from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import mysql.connector

#region
#global variables
event_tag_classes = {'event_name' : {"class": "card-text--truncated__three"},
                     'event_month' : {"class": "date-thumbnail__month"},
                     'event_day' : {"class": "date-thumbnail__day"},
                     'event_location' : {"class": "card-text--truncated__one"},
                     'event_time' : {"class": "eds-media-card-content__sub-content"},
                     'event_desc' : {"class": "eds-media-card-content__action-link"}
                     }

event_info_dict = {}
#endregion

def main():

    mydb = mysql.connector.connect(host='127.0.0.1', user='root', password='IbgrwAttn,mwa.11SQL', database='planner')
    mydb.autocommit = True

    url ='https://www.eventbrite.com/d/ca--san-jose/events/'

    scrape_event_list(url,mydb)

    mydb.close()

def scrape_event_list(url,database):

	#opens a conenction and downlaods the html code
	uClient = uReq(url)
	page_html = uClient.read()
	uClient.close()

	page_soup = soup(page_html, "html.parser")

	containers = page_soup.findAll("div", {"class": "eds-media-card-content__content"})

	event_id_counter = 1

	for container in containers:

		event_info_dict['event_name'] = pull_text_from_tag(container, 'div', event_tag_classes['event_name'])

		#pull event month and day and concatenate them
		event_month = pull_text_from_tag(container, 'p', event_tag_classes['event_month'])
		event_day = pull_text_from_tag(container, 'p', event_tag_classes['event_day'])
		if event_month != None and event_day != None:
		    event_info_dict["event_date"] = str(event_month + " " + event_day)

		event_info_dict["event_location"] = pull_text_from_tag(container, 'div', event_tag_classes['event_location'])

        #time has to be handled differently because of the way it is formatted on the site
		time_container = container.findAll("div",event_tag_classes['event_time'])
		if len(time_container) != 0:
		    event_time = time_container[0].div.text.split(',')
		    if len(event_time) >= 2:
		        event_time = event_time[2]
		        event_info_dict["event_time"] = event_time[0:8]

		event_info_dict['event_desc'] = scrape_event_desc(container) 

		event_info_dict["event_id"] = event_id_counter
		event_id_counter += 1

		populate_event_db(database)
		event_info_dict.clear


def scrape_event_desc(container):
	event_desc_link_container = container.findAll("a", event_tag_classes['event_desc'])
	for a in event_desc_link_container:
		event_desc_link = a['href']

	return event_desc_link


def pull_text_from_tag(container,html_tag,html_class):
	text_container = container.findAll(html_tag, html_class)
	if len(text_container) != 0:
	    return text_container[0].text
	else:
		return 


def populate_event_db(database):
	mycursor = database.cursor()
	sqlFormula = "INSERT INTO events (eventid,ename,location,eventdate,starttime,edesc) VALUES (%s,%s,%s,%s,%s,%s)"
	event_info = (event_info_dict["event_id"],event_info_dict["event_name"],event_info_dict["event_location"],
		event_info_dict["event_date"],event_info_dict["event_time"],event_info_dict['event_desc'])

	mycursor.execute(sqlFormula,event_info)

main()
