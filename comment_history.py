
## Modmail User Comment History Bot.  Updated version of u/user_history_bot


import praw
import traceback
import time
import sys
import config


sub_name = 'YOUR_SUBREDDIT'


try:
    reddit = praw.Reddit(   user_agent = 'User Comment History Bot v.1.0 by u/buckrowdy & u/ghostofbearbryant.',
                            username = config.username,
                            password = config.password,
                            client_id = config.client_id,
                            client_secret = config.client_secret)

except Exception as e:
    print(f"\t### ERROR - Could not login.\n\t{e}")
#print(f"Logged in as: {reddit.user.me()}\n\n")
#return reddit


# Check to see if the user account is an active and valid account.
def does_user_exist(user):
    try:
        for comment in user.comments.new(limit=1):
            pass
        return True
    except praw.exceptions.PRAWException:
        return False

# Scrape the user's account and compile a table with their comment history. 
def get_comment_history(user):
   print('working...')
   subreddits = [str(comment.subreddit.display_name) for comment in user.comments.new(limit=None)]
   str_message = "Data for the last {} comments for /u/{}\n\n{:20}|{:20}|{:20}\n".format(len(subreddits),str(user),
            "Subreddit","Comments","Percentage")
   str_message += (("-"*20 + "|")*2 + "-"*20)+"\n"
   subreddit_count = dict((subreddit, subreddits.count(subreddit)) for subreddit in subreddits)
   start = 0
   for subreddit in sorted(subreddit_count, key=lambda k:subreddit_count[k],reverse=True):
      count = subreddit_count[subreddit]
      percentage = "{0:.2f}%".format(float(100*count)/len(subreddits))
      str_message += "/r/{:20}|{:20}|{:20}\n".format(subreddit, count , percentage)
      start += 1
      if start == 60:
         break
   str_message += "\n\n To use this bot, reply to a modmail message with 'user_history', then highlight."
   return str_message 


# Take the comment history table and send it as a modmail message.
def generate_response(username):

    user = reddit.redditor(f'{username}')
    if does_user_exist(user):
        return get_comment_history(user) 
    else:
        return f'/u/{username} is an invalid user!'


# Take the generated response and send it as a private mod note.
def respond(msg_to_respond, response):  
    try:
        msg_to_respond.reply(body=response, internal=True) 
    except Exception as e:
      print(e)
      print("\t\n### ERROR - Couldn't reply to modmail.")
      traceback.print_exc()


# Bot run that checks modmail for the trigger phrase.
def run_bot():
    try:
        print('Working...')
        unread_conversations = reddit.subreddit(sub_name).modmail.conversations(state="highlighted")
        #unread_conversations = reddit.subreddit(sub_name).modmail.conversations(state="all")
        for conversation in unread_conversations: 
            if (len(conversation.authors) >= 1 and len(conversation.messages) >= 1 and "user_history" in conversation.messages[-1].body_markdown): 
                print(f'Match Found: {conversation.id}')
                username = conversation.user
                print(f'Username: {username}')
                conversation_id = conversation.id
                print(conversation_id)
                conversation.archive()
                response = generate_response(username)
                respond(conversation, response)
                print('Message Sent Successfully')
                #conversation.read()
                conversation.unhighlight()
                print('Conversation unhighlighted')
    except Exception as e:
      print("\t\n### ERROR - Modmail couldn't be checked.")
      traceback.print_exc()             
                    

 if __name__ == "__main__":
     try:
         reddit = reddit_login()

     except Exception as e:
         print("\t\n### ERROR - Could not connect to reddit.")
         sys.exit(1)

     # Loop the bot
     while True:

         try:
             run_bot()
             print('Sleeping...')
             time.sleep(60)  
        
         except Exception as e:
             print(f"\t### ERROR - Something went wrong.\n\t{e}")
             sys.exit(1)
         
    



    
              


