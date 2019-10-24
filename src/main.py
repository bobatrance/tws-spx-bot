import praw, json, datetime, time, urllib.request, math

secondsBeforeCaptureResults = 60
mapContestSubmissions = {}

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
    alphavantage_api_key=jsonCredentials["apikey"]

# function to handle contest submission parsing
# check to see if it is a duplicate submission
# check to see if message is a number for spx
def checkDuplicateAndAddContestEntry(contestComment):
    if contestComment.author not in mapContestSubmissions:
        try:
            floatContestCommentBody = float(contestComment.body)
            mapContestSubmissions[contestComment.author] = floatContestCommentBody
        except ValueError:
            print("Skipping " + contestComment.author + "'s comment of " + contestComment.body)

def getFloatTodaySpxClose():
    with urllib.request.urlopen("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=SPX&outputsize=compact&apikey="+ alphavantage_api_key) as url:
        data = json.loads(url.read().decode())
    return float(data.get("Time Series (Daily)").get(datetime.date.today().strftime("%Y-%m-%d")).get("4. close"))

def findClosestNumber():
    listClosestAuthors = []
    floatClosestNumber = 9999999.0
    for submissionAuthor in mapContestSubmissions:
        delta = math.fabs(mapContestSubmissions[submissionAuthor]-getFloatTodaySpxClose())
        if delta < floatClosestNumber:
            floatClosestNumber = delta
            listClosestAuthors.clear()
            listClosestAuthors.append(submissionAuthor)
        elif delta == floatClosestNumber:
            listClosestAuthors.append(submissionAuthor)
    return listClosestAuthors

def wiki(subreddit, winner):
    wikipage = subreddit.wiki['SPX Prediction Leaderboards']
    content = wikipage.content_md
    print(content)
    #check user
    #increment user

# main
# setting up daily post parse
subreddit = reddit.subreddit("thewallstreet")
sTodayDate = datetime.date.today().strftime("%B %d")
sDailyDiscussionTarget = "Daily Discussion - (" + sTodayDate + ")"
print("Targeting " + sDailyDiscussionTarget)

for submission in subreddit.hot(limit=15):
    if submission.title == sDailyDiscussionTarget:
        if submission.author == "AutoModerator":
            print("Found today's daily!")
            if subreddit.user_is_subscriber:
                if not subreddit.user_is_banned:
                    print("we're ok to post")
                    commentStartContest = submission.reply("\U0001F4C8 Contest now open! \U0001F4C9")
                    #time.sleep(secondsBeforeCaptureResults) # delay timer for post emulation

                    # do logic capture all comments
                    commentStartContest.refresh()
                    commentContestReplies = commentStartContest.replies
                    for comment in commentContestReplies:
                        # take top level replies and hash to make sure there are no repeat
                        checkDuplicateAndAddContestEntry(comment)

                    # do logic close contest and parse winner
                    commentCloseContest = "~~" + commentStartContest.body + "~~" + "\n\nEdit: Contest now closed!"
                    commentStartContest.edit(commentCloseContest)
                    listWinners = findClosestNumber()
                    for winner in listWinners:
                        print(winner)
                        # perform subreddit wiki functions
                        wiki(subreddit, winner)
                    break
