import os
import time
import re
from slack import WebClient
import datetime
import requests
from math import ceil
import random


GROUP_SIZE = 5
LOWER_GROUP_SIZE = 4
CHANNEL_NAME = 'donut-time' #channel name for donut-time to occur in
BOT_ID = 'U011Q8JT69J' #get bot id
TOKEN_TEXT_PATH = 'slackkeys.txt'

MSG = "Hi, welcome to this weeks donut time. \n\n Hope you enjoy catching up with each other!"


#get tokens
tokens = {}
with open(TOKEN_TEXT_PATH) as f:
    text = f.readlines()
    for line in text:
        a,b = line.split(':') #get key, value
        b = b[:-1] #get rid of new line
        tokens[a]=b
        
# get all channels the donut-bot is in
url = 'https://slack.com/api/users.conversations?token='+tokens['OAuthAccessToken']+'&types=private_channel%2Cpublic_channel&pretty=1'
val = requests.get(url).json()
# get the channel id of CHANNEL_NAME
for channel in val['channels']:
    if channel['name'] == CHANNEL_NAME:
        CHANNEL_ID = channel['id']
        
# gets all members in the CHANNEL_NAME channel
b = 'https://slack.com/api/conversations.members?token='+tokens['OAuthAccessToken']+'&channel='+CHANNEL_ID+'&pretty=1'
val = requests.get(b).json()
val['members'].remove(BOT_ID) #remove the bot from the list of members
member_ids = val['members']
NUM_MEMBERS = len(member_ids)

#get group sizes
NUM_GROUPS = ceil(NUM_MEMBERS / GROUP_SIZE)
print(NUM_GROUPS)
groups_that_are_off = GROUP_SIZE - (NUM_MEMBERS % GROUP_SIZE)
print(groups_that_are_off)
group_sizes = [GROUP_SIZE-1]*groups_that_are_off + [GROUP_SIZE]*(NUM_GROUPS-groups_that_are_off)
print(group_sizes)
print(NUM_GROUPS)
assert sum(group_sizes) == NUM_MEMBERS
assert not any([x<LOWER_GROUP_SIZE for x in group_sizes])

#create new direct message with users, donut-bot prints out given msg
def create_and_introduce_group(users:list,msg:str):
    #create group
    string_users = ','.join(users)
    create_group_url = 'https://slack.com/api/conversations.open?token='+tokens['OAuthAccessToken']+'&users='+string_users+'&pretty=1'
    create_group_response = requests.get(create_group_url).json()
    if create_group_response['ok']!=True:
        print("WARNING: SOMETHING BROKE")
    channel_id = create_group_response['channel']['id']
    #send message
    requests.get('https://slack.com/api/chat.postMessage?token='+tokens['OAuthAccessToken']+'&channel='+channel_id+'&text='+msg+'&pretty=1')
    
    
#creating groups
random_indices = np.random.choice(list(range(NUM_MEMBERS)),size=NUM_MEMBERS,replace=False)
assert len(np.unique(random_indices)) == NUM_MEMBERS
offset = 0
for size in group_sizes:
    get_indices = random_indices[offset:offset+size]
    get_members = list(np.array(member_ids)[get_indices])
    create_and_introduce_group(get_members,MSG)
    offset +=size
    
    

