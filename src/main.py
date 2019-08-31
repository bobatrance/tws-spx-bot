import praw
import json
import datetime
import time

# loading credentials
with open('../secret/credential.json', 'r') as f:
    jsonCredentials = json.load(f)
    reddit = praw.Reddit(
        client_id=jsonCredentials["clientid"],
        client_secret=jsonCredentials["clientsecret"],
        user_agent=jsonCredentials["useragent"],
        redirect_uri=jsonCredentials["redirecturi"],
        username=jsonCredentials["username"],
        password=jsonCredentials["password"]
    )

# setting up daily post parse
subreddit = reddit.subreddit("thewallstreet")
sTodayDate = datetime.date.today().strftime("%B %d")
sDailyDiscussionTarget = "Daily Discussion - (" + sTodayDate + ")"

for submission in subreddit.hot(limit=15):
    if submission.title == sDailyDiscussionTarget:
        if submission.author == "AutoModerator":
            print("Found today's daily!")
            if subreddit.user_is_subscriber:
                if not subreddit.user_is_banned:
                    print("we're ok to post")
                    commentStartContest = submission.reply("\U0001F4C8 Contest now open! \U0001F4C9")
                    time.sleep(60) #seconds
                    #do logic capture all comments
                    commentStartContest.refresh()
                    commentReplies = commentStartContest.replies
                    #toplevel replies only
                    for replies in commentReplies:
                        print(replies.body)
                    commentCloseContest = "~~" + commentStartContest.body + "~~" + "\n\nEdit: Contest now closed!"
                    commentStartContest.edit(commentCloseContest)
                    break