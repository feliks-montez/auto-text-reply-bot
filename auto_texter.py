from googlevoice import Voice
from googlevoice import util
from googlevoice.util import *
import googlevoice.settings as settings
from time import sleep

# configure some Voice settings
settings.DEBUG=True

class MessageListener():
  def __init__(self, refresh_interval=30):
    """
      * refresh_interval is in seconds
    """
    self.voice = Voice()
    self.voice.login()

    sms = self.voice.sms()
    html = self.voice.sms.html_data
    
    self.conversations = self.getConversations(self.voice) or self.conversations # this in case it fails because of an image or something
    self.last_message_count = self.voice.sms.data['totalSize']
    
    while True:
      self.loop()
      sleep(refresh_interval)
    
  def get_unread_count(self, folder):
    unread_count = 0;
    i = 0
    while True:
      try:
        if not folder.messages[i].isRead:
          print(read_message(self.voice, i))
          unread_count += 1
        i += 1
      except IndexError:
        break
    return unread_count
    
  def getConversations(self, voice):
    try:
      sms = voice.sms()
    except googlevoice.util.ParsingError:
      return None
    conversations = {}
  
    i = 0
    while True:
      try:
        contact_name = voice.sms.html_data.find(id=sms.messages[i].id)
        message_data = sms.messages[i]
        try:
          contact_name = contact_name.find('span', class_='gc-message-name').find('a').text
        except:
          contact_name = contact_name.find('span', class_='gc-message-name').select('span[title]')[0].attrs['title']
        raw_messages = voice.sms.html_data.find(id=sms.messages[i].id).select('.gc-message-sms-row')
        
        try:
          from_number = voice.sms.html_data.find(id=sms.messages[i].id).find('span', class_='gc-message-type').text
        except AttributeError:
          from_number = voice.sms.html_data.find(id=sms.messages[i].id).find('span', class_='gc-message-name').text
        from_number = re.search(r'([\(\)\s\-\d]+\d)', from_number).group(0)
        
        messages = []
        for message in raw_messages:
          from_ = message.find('span', class_='gc-message-sms-from').text.strip()[:-1]
          text = message.find('span', class_='gc-message-sms-text').text
          time = message.find('span', class_='gc-message-sms-time').text.strip()
          
          txt = Text(from_=from_, from_number=from_number, text=text, time=time, isRead=message_data.isRead)
          messages.append(txt)
        if contact_name in conversations.keys():
          conversations[contact_name] += messages
        else:
          conversations[contact_name] = messages
        i += 1
        
      except IndexError:
        break
    return conversations
    
  def loop(self):
    sms = self.voice.sms()
    
    updated_conversations = self.getConversations(self.voice)
    new_message = False
    new_messages = []
    if len(updated_conversations.keys()) > len(self.conversations.keys()):
      new_message = True
      #print("new conversation")
    elif len(updated_conversations.keys()) == len(self.conversations.keys()):
      #print("same # of conversations")
      for contact in self.conversations.keys():
        last_messages = self.conversations[contact]
        updated_messages = updated_conversations[contact]
        if len(updated_messages) > len(last_messages):
          new_message = True
          #print("new message")
        
          for i in range(0, len(updated_messages)):
            #print(len(last_messages),len(updated_messages),i)
            try:
              if last_messages[i].text == updated_messages[i].text:
                continue
              elif last_messages[i-1].text == updated_messages[i].text:
                continue
              elif last_messages[i+1].text == updated_messages[i].text:
                continue
              else: # this updated_message must be a new one--it doesn't appear to be in the last_messages
                new_messages.append(updated_messages[i])
            except IndexError:
              if last_messages[i-2].text == updated_messages[i].text:
                continue
              elif last_messages[i-1].text == updated_messages[i].text:
                continue
              elif last_messages[0].text == updated_messages[i].text:
                continue
              else: # this updated_message must be a new one--it doesn't appear to be in the last_messages
                new_messages.append(updated_messages[i])
          
      self.conversations = updated_conversations
    
    for msg in new_messages:
      if msg.from_ != 'Me':
        # TODO: only send the auto-response if the last message was more than 30 minutes ago
        print("New message! => %s" % msg.toString())
        dumb_contacts = ['Aimee Hudson', 'Andrew Post']
        test_contacts = ['Drew Meier', '17246673655']
        if msg.from_ in dumb_contacts:
          self.voice.send_sms(msg.from_number, "You're dumb")
        if msg.from_ in test_contacts or msg.from_number in test_contacts:
          self.voice.send_sms(msg.from_number, "Auto-reply from megatron. Let me know if you get this (it doesn't show up on my chat).")
    
#    new_count = int(self.voice.sms.data['totalSize'])
#    print(new_count)
#    if new_count > self.last_message_count:
#      self.last_message_count = new_count
#      print("got message")
      

class Text():
  def __init__(self, to='', from_='', from_number='', text='', time='', isRead=True):
    self.to = to
    self.from_ = from_
    self.text = text
    self.time = time
    self.isRead = isRead
    self.from_number = re.sub(r'[\(\)\s\-]', '', from_number)
    
  def toString(self):
    return("%s (%s) at %s: %s" % (self.from_, self.from_number, self.time, self.text))

#voice = Voice()
#voice.login()

#sms = voice.sms()
#html = voice.sms.html_data

#conversations = {}



#def read_message(voice, i):
#  sms = voice.sms()
#  html = voice.sms.html_data
#  contact_name = voice.sms.html_data.find(id=sms.messages[i].id)
#  try:
#    contact_name = contact_name.find('span', class_='gc-message-name').find('a').text
#  except:
#    contact_name = contact_name.find('span', class_='gc-message-name').select('span[title]')[0].attrs['title']
#  raw_messages = voice.sms.html_data.find(id=sms.messages[i].id).select('.gc-message-sms-row')
#  
#  message = raw_messages[-1]
#  from_ = message.find('span', class_='gc-message-sms-from').text.strip()[:-1]
#  text = message.find('span', class_='gc-message-sms-text').text
#  time = message.find('span', class_='gc-message-sms-time').text.strip()
#  
#  txt = Text(from_=from_, text=text, time=time)
#  return txt.toString()

###-------------------------------

##phoneNumber = input('Number to send message to: ')
##text = raw_input('Message text: ')

##voice.send_sms(phoneNumber, text)

#for contact in conversations.keys():
#  msgs = conversations[contact]
#  print(contact)
#  print("\n------------------------\n")
#  for msg in msgs:
#    print(msg.toString()) 

youre_dumb = MessageListener(5)

#from googlevoice import Voice
#import sys
#import BeautifulSoup


#def extractsms(htmlsms) :
#    """
#    extractsms  --  extract SMS messages from BeautifulSoup tree of Google Voice SMS HTML.

#    Output is a list of dictionaries, one per message.
#    """
#    msgitems = []										 accum message items here
#    	Extract all conversations by searching for a DIV with an ID at top level.
#    tree = BeautifulSoup.BeautifulSoup(htmlsms)			 parse HTML into tree
#    conversations = tree.findAll("div",attrs={"id" : True},recursive=False)
#    for conversation in conversations :
#        	For each conversation, extract each row, which is one SMS message.
#        rows = conversation.findAll(attrs={"class" : "gc-message-sms-row"})
#        for row in rows :								 for all rows
#            	For each row, which is one message, extract all the fields.
#            msgitem = {"id" : conversation["id"]}		 tag this message with conversation ID
#            spans = row.findAll("span",attrs={"class" : True}, recursive=False)
#            for span in spans :							 for all spans in row
#                cl = span["class"].replace('gc-message-sms-', '')
#                msgitem[cl] = (" ".join(span.findAll(text=True))).strip()	 put text in dict
#            msgitems.append(msgitem)					 add msg dictionary to list
#    return msgitems
#    
#voice = Voice()
#voice.login()

#voice.sms()
#for msg in extractsms(voice.sms.html):
#    print str(msg)

