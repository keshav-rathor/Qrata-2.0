import json
import os
import random
import traceback

from flask import Flask
from flask import request, make_response
from pymongo import MongoClient

MONGODB_URI = "mongodb+srv://kamlesh:techmatters123@aflatoun-quiz-pflgi.mongodb.net/test?retryWrites=true&w=majority"
client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
db = client.hrchatbot
candidates = db.Chatbots_Candidates
job = db.Hiring_PublicJobPosition
db = client.Blacklist
planUS = db.Hr_info






flag = 0
job_detail={}
name={}
candidates_detail={}

# Flask app should start in global layout
app = Flask(__name__)

#function displaying the text on facebook
def make_text_response(message, platform="FACEBOOK"):
    return {
        "text": {
            "text": [
                message
            ]
        },
        "platform": platform
    }




information=["experiance","skills","CTC","Location"]
information_previous=[]
def show(information,information_previous):
    global information_sample
    if len(information) != 0:
        information_sample = random.choice(information)
        information_previous.append(information_sample)
        information.remove(information_sample)
    return information_sample


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    res = process_request(req)
    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def process_request(req):
    global job_detail,candidates_detail
    global flag

    try:
        planUS.insert(req, check_keys=False)
    except:
        pass

    try:
        action = req.get("queryResult").get("action")

        if action == "input.welcome":
            # CLear the previous question list if start over

            return {
                "source": "webhook"
            }

#Asking for name from user and updating the candidates details
        elif action == "name":
            result = req.get("queryResult")
            parameter = result.get("parameters")
            print(parameter)
            candidates_detail.update(parameter)
            #candidates.insert(candidates_detail)

# Asking for email from user and updating the candidates details
        elif action == "email":
            result = req.get("queryResult")
            parameter = result.get("parameters").get("email")
            email = {"email": parameter}
            print(email)
            candidates_detail.update(email)
            # candidates.insert(candidates_detail)



#Taking the details of user in community and update the database
        elif action == "Community":
            result = req.get("queryResult")
            parameter = result.get("parameters")
            candidates_detail.update(parameter)
            print(candidates_detail)
            print(len(candidates_detail))
        #candidates.insert(candidates_detail)
            if len(candidates_detail) >= 5:

                candidates.insert(candidates_detail)
                candidates_detail = {}
                return {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        make_text_response(
                            "Excellent! i'll keep you updated."

                        )
                    ] + [
                        make_text_response("Meanwhile you can have a look on these things"),
                        {
                            "quickReplies": {
                                "title": "These are your options",
                                "quickReplies": [
                                    "About us",
                                    "Highpo!",
                                    "Jobs",
                                    "Help us to improve"
                                ]
                            },
                            "platform": "FACEBOOK"
                        }

                    ]
                }

# #Accept the Resume URL from user and update candidates detail
#         elif action == "resume":
#             result = req.get("originalDetectIntentRequest").get("payload").get("data").get("message").get("attachments")[0].get("payload")
#             # resume_url = result.get("url")
#             candidates_detail.update(result)
#

#Searching the jobs
        elif action == "search_jobs":
            result = req.get("queryResult")
            parameter = result.get("parameters")
            job_detail.update(parameter)
            # print("Job details", job_detail)
            # print("Name", name)

            # print("Got all job details")
            #candidates.insert(job_detail)
            filter_query = {"statusVisible": "enum.Hiring_JobPositionStatusVisible.Public"}
            filter_query.update(parameter)

            show_jobs = job.find(filter_query).limit(5)
            print("show jobs",show_jobs)

            if show_jobs.count()!=0:
                job_detail = {}
                return {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        {
                            "card": {
                                "title": i["jobTitle"],
                                "subtitle": i["companyName"] + " | " + i["locality"] + " | " + i["region"],
                                "imageUri": "https://akm-img-a-in.tosshub.com/sites/btmt/images/stories/jobs660_090518050232_103118054303_022119084317.jpg",
                                "buttons": [
                                    {
                                        "text": "View Job Detail",
                                        "postback": i["jobDetailsUrl"]
                                    }
                                ]
                            },

                            "platform": "FACEBOOK"
                        } for i in show_jobs
                    ] + [
                        make_text_response("You can apply for the job or you can view something else."),
                        {
                            "quickReplies": {
                                "title": "These are your options",
                                "quickReplies": [
                                    "About us",
                                    "Jobs"
                                ]
                            },
                            "platform": "FACEBOOK"
                        }

                    ]


                }

            else:
                return {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        make_text_response(
                            " We are really sorry but we don't have any job opening for your profile for now ."
                            "We have your contact details and will contact you if there is any opening in future ."
                            "Thanks for visiting our site")
                    ]+[
                        {
                            "quickReplies": {
                                "title": "These are your options",
                                "quickReplies": [
                                    "About us",
                                    "Jobs"
                                ]
                            },
                            "platform": "FACEBOOK"
                        }

                    ]
                }
#
        elif action == "IT":
            print("IT")
            result = req.get("queryResult")
            parameter = result.get("parameters")
            job_detail.update(parameter)
            # print("Job details", job_detail)
            # print("Name", name)

            print("Got all job details")
            print(job_detail)
            #candidates.insert(job_detail)
            show_jobs = job.find({"jobTitle": job_detail["jobTitle"],
                                  "statusVisible": "enum.Hiring_JobPositionStatusVisible.Public"}).limit(3)
            print(show_jobs)

            if show_jobs:
                print("IT - Show_jobs")
                job_detail = {}
                return {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        {
                            "card": {
                                "title": i["jobTitle"],
                                "subtitle": i["companyName"] + " | " + i["locality"] + " | " + i["region"],
                                "imageUri": "https://akm-img-a-in.tosshub.com/sites/btmt/images/stories/jobs660_090518050232_103118054303_022119084317.jpg",
                                "buttons": [
                                    {
                                        "text": "View Job Detail",
                                        "postback": i["jobDetailsUrl"]
                                    }
                                ]
                            },
                            "platform": "FACEBOOK"
                        } for i in show_jobs]
                }

            else:
                return {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        make_text_response(
                            " We are really sorry but we don't have any job opening for your profile for now ."
                            "We have your contact details and will contact you if there is any opening in future ."
                            "Thanks for visiting our site")
                    ]
                }


        elif action == "Jobs":
            print("jobs")
            result = req.get("queryResult")
            parameter=result.get("parameters")
            job_detail.update(parameter)
            # print("Job details", job_detail)
            # print("Name", name)
            if len(job_detail)>=6:
               # print("Got all job details")
               candidates.insert(job_detail)
               show_jobs = job.find({ "locality": job_detail["locality"],
                                        "statusVisible" : "enum.Hiring_JobPositionStatusVisible.Public"}).limit(3)
               if show_jobs:
                   job_detail={}
                   return {
                       "source": "webhook",
                       "fulfillmentMessages":   [
                            {
                                   "card": {
                                       "title": i["jobTitle"],
                                       "subtitle": i["companyName"] + " | " + i["locality"] + " | " + i["region"],
                                       "imageUri": "https://akm-img-a-in.tosshub.com/sites/btmt/images/stories/jobs660_090518050232_103118054303_022119084317.jpg",
                                       "buttons": [
                                           {
                                               "text": "View Job Detail",
                                               "postback": i["jobDetailsUrl"]
                                           }
                                       ]
                                   },
                                   "platform": "FACEBOOK"
                               } for i in show_jobs ]
                   }

               else:
                   return {
                       "source": "webhook",
                       "fulfillmentMessages": [
                           make_text_response(" We are really sorry but we don't have any job opening for your profile for now ."
                                              "We have your contact details and will contact you if there is any opening in future ."
                                              "Thanks for visiting our site")
                       ]
                   }

#Default fallback if flag==2 means 2 known input so show the message
        elif action == "input.unknown":
            flag += 1
            if flag >= 2:
                flag = 0
                return {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        {
                            "text": {
                                "text": [
                                    "It's look like I unable to understand what you are saying but  "
                                    "I can help you these following things:\n1. About Qrata 📝\n2. Jobs 👨🏼‍🏫\n3. "
                                    "Be You",
                                ]
                            }
                        },
                        {
                            "text": {
                                "text": [
                                    "I am not fully aware of what you are asking .",
                                ]
                            },
                            "platform": "FACEBOOK"
                        },
                        {
                            "quickReplies": {
                                "title": "But I can help you these following things",
                                "quickReplies": [
                                    "About Qrata",
                                    "Jobs",
                                    "Be You",

                                ]
                            },
                            "platform": "FACEBOOK"
                        }
                    ]
             }






#if some error occure then display this message
    except Exception as e:
        print("Error:", e)
        traceback.print_exc()
        return {
            "fulfillmentText": "Oops... 😮 I am not able to help you at the moment, please try again..",
            "source": "webhook"
        }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port {}".format(port))
    app.run(debug=True, port=port, host='0.0.0.0')