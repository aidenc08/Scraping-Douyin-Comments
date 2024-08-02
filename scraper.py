from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import os

# Set up the WebDriver (make sure to specify the path to your chromedriver)



class Comment:
    id_set = set()

    def __init__(self, cid, comment, likes, time):
        self.id = cid
        self.comment = None
        if (self.id in Comment.id_set):
            return None
        else:
            Comment.id_set.add(self.id)
        self.comment = comment
        self.likes = likes
        self.time = time

    def __lt__(self, other):
        return self.likes > other.likes


driver = webdriver.Chrome()


# Navigate to the Douyin video page
ids = [[7134116275030150436]]

labels = ["Bai Bing Before"]
for author in range(len(ids)):
    try:
        label = labels[author]
        os.mkdir(label)
    except:
        print("Directory Already Exists")
    for video in range(len(ids[author])):
        video_url = "https://www.douyin.com/discover?modal_id=" + str(ids[author][video])  # Replace with the actual URL
        driver.get(video_url)
        print("Log In if Necessary and Navigate to Comments.")
        while (input("Press Enter to Start Scrolling. Press q and then enter if bottom of page has been reached: ") != "q"):
            element = driver.find_element(By.TAG_NAME, "html")
            print("Scrolling Started")
            for i in range(60):
                time.sleep(1)
                element.send_keys(Keys.CONTROL + Keys.END)
        all_comments = []
        Comment.id_set = set()
        for request in driver.requests:
            if request.response:
                if ("comment" in str(request.url)):
                    with open("requests.txt", "a") as file:
                        file.write(str(request.url))
                    body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                    try:
                        json_data = json.loads(body)
                        if ('comments' in json_data.keys()):
                            comments = json_data['comments']
                            for comment in comments:
                                text = comment['text']
                                likes = comment['digg_count']
                                create_time = comment['create_time']
                                cid = comment['cid']
                                dt_object = datetime.utcfromtimestamp(create_time)
                                c = Comment(cid, text, likes, dt_object)
                                if (c.comment != None):
                                    all_comments.append(c)
                    except:
                        with open("error.txt", "a") as file:
                            file.write(str(body))
                            file.write("\n\n")
                        pass


        all_comments.sort()
        with open(label + "/" + str(ids[author][video]) + ".csv", 'w') as file:
            file.write("Comment,Time,Likes\n")
            for index in range(0, min(50, len(all_comments))):
                i = all_comments[index]
                comment_stripped = i.comment.replace("\n", " ")
                file.write(comment_stripped + "," + str(i.time) + "," + str(i.likes) + "\n")

        print(str(len(all_comments)) + " Comments Found")
        print("Completed Video " + str(video) + " With ID: " + str(ids[author][video]))

        del driver.requests

        input("Press Enter to Continue to Next Video: ")
    print(label + " Finished.")
