import os
from flask import Flask, render_template, request
import praw
import datetime

app = Flask(__name__)

# 🔹 Reddit API Credentials (Replace with your own)
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD")
)

# 🔹 Route for Home Page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        target_username = request.form["username"]
        removed_count = remove_user_comments(target_username)
        return render_template("index.html", removed_count=removed_count, username=target_username)
    return render_template("index.html", removed_count=None)

# 🔹 Function to Remove Comments
def remove_user_comments(username):
    try:
        target_user = reddit.redditor(username)
        user_comments = target_user.comments.new(limit=30)  # Only remove last 30 comments
        removed = 0
        for comment in user_comments:
            if comment.subreddit.display_name.lower() == "minecraftbuddies":
                comment.mod.remove()
                removed += 1
        return removed
    except Exception as e:
        print(f"Error: {e}")
        return -1  # Return -1 if an error occurs

# 🔹 Function to Ban Users for Account Age Violation
def ban_for_account_age_violation(username):
    try:
        target_user = reddit.redditor(username)
        account_created_date = datetime.datetime.utcfromtimestamp(target_user.created_utc)
        current_date = datetime.datetime.utcnow()
        account_age = (current_date - account_created_date).days

        if account_age < 180:
            days_until_eligible = 180 - account_age
            ban_message = (f"Hello {username},\n\n"
                           "Your account has been temporarily banned from r/MinecraftBuddies due to Rule 1: Accounts must be at least 6 months old to post.\n\n"
                           f"Your ban will last for {days_until_eligible} days. After this period, you will be able to participate in the subreddit again.\n\n"
                           "Thank you for your interest in r/MinecraftBuddies.")

            subreddit = reddit.subreddit("MinecraftBuddies")
            subreddit.banned.add(username, duration=days_until_eligible, note="Rule 1 - Account age violation", ban_message=ban_message)
            
            # Remove all previous comments and posts
            for comment in target_user.comments.new(limit=None):
                if comment.subreddit.display_name.lower() == "minecraftbuddies":
                    comment.mod.remove()
            for submission in target_user.submissions.new(limit=None):
                if submission.subreddit.display_name.lower() == "minecraftbuddies":
                    submission.mod.remove()

            return f"User {username} has been banned for {days_until_eligible} days due to an account age violation."
        else:
            return f"User {username} meets the account age requirement. No action taken."
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing the ban."

# 🔹 Run the Flask App
if __name__ == "__main__":
    app.run(debug=True)
