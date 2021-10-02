import sys
from bs4 import BeautifulSoup
import re
import json
import requests
import ssl
import certifi
import os

# Here's all the magic !
os.environ['SSL_CERT_FILE'] = certifi.where()


#I recommend reading into the source code of the nhentai website to get a better understanding of what my code really does

class Exceptions:
    class NoResults(Exception):
        pass
    class NoNetwork(Exception):
        pass


headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"}
#Optional
def CheckLink(data, **opt):
  '''For MODDERS:
  This part is where you modify your OWN link checker to your own target site to scrape.
  Most of the time there wont be any major edits other than the website you want to check.
  '''
  if opt:
    return("https://nhentai.net/g/%s" % data)
  if re.search("https?://nhentai.net/g/(\d+|/)", data.lower()):
    return(0, data)
  else:
    return(2, "Link is not nHentai")

#Main API
class Api:
  # Use INIT to initialize the needed data, for increased and faster loading times to other functions
  def __init__(self,data):
    '''
    argument 'data' should be a valid gallery/link to a certain doujin. 
    '''
    #NHENTAI SITE FORTUNATELY HAS A DEDICATED JSON EMBEDDED INTO A SCRIPT FILE THAT YOU CAN USE TO GAIN INFORMATION FROM THE SITE. 
    #DIFFERENT SITES MIGHT NOT HAVE A JSON FILE SO YOU WILL HAVE TO DO THE PROCESS MANUALLY
    r = requests.get(data, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")
    try:
      script = (soup.find_all("script")[2].contents[0]).strip().replace("window._gallery = JSON.parse(", "").replace(");","")
    except IndexError:
      #ONLY OCCURS WHEN THERE IS NO RESULTS
      error = {"error_message":"","e":""}
      try:
        error_scrape = soup.find("div",class_="container error")
        status = error_scrape.find("h1").text.strip()
        status_message = error_scrape.find("p").text.strip()
        error["error_message"] = ("%s %s" % (status,status_message))
      except AttributeError as e:
        #Precautionary Catcher. rarely occurs
        error["e"] = e
      raise_message = ("%s %s" % (error["error_message"], error["e"]))
      raise Exceptions.NoResults(raise_message)
    except requests.exceptions.ConnectionError as error:
        raise Exceptions.NoNetwork(error)
    #IF THERE IS NO ERROR THEN PROCEED 
    self.json = json.loads(json.loads(script))
    print(self.json)
    

  def Pages(self):
    Page = len(self.json["images"]["pages"])
    return Page
  
  def Id(self):
    id_ = self.json["id"]
    return id_

  def Tags(self):
    """For MODDERS:
    For better readability for humans or other programs, I recommend you use Json to serialize your data.
    """
    Tag = self.json["tags"]
    return Tag

  def Title(self):
    title = self.json["title"]["english"]
    return title
    
  def Thumbnail(self):
    pass

  def Metadata(self,Page,**request):
    data = self.json["images"]["pages"][Page-1]
    if request['data'] == 'format':
        return format_find(image)
    elif request['data'] == 'res':
        res = {"w": data["w"], "h": data["h"]}
        return res
    return data
      
        
  
  def format_find(self,value):
    data = self.json["images"]["pages"][value-1]
    file = data["t"]
    if file == "j":
      extension = "jpg"
    elif file == "p":
      extension = "png"
    elif file == "g":
      extension = "gif"
    else:
      print("WARNING AT PAGE: %s\nUNIDENTIFIED FORMAT DETECTED REPORT THIS BUG\nautoset: jpg" % value)
      extension = "jpg"
    return extension
  def Direct_link(self,value): 
    """For MODDERS:
    This function is only used to RETURN a valid direct link to the targeted image.
    The variable 'value' is the episode/page of the certain image to return. 
    """
    data = self.json["images"]["pages"][value-1]
    file = data["t"]
    if file == "j":
      extension = "jpg"
    elif file == "p":
      extension = "png"
    elif file == "g":
      extension = "gif"
    else:
      print("WARNING AT PAGE: %s\nUNIDENTIFIED FORMAT DETECTED REPORT THIS BUG\nautoset: jpg" % value)
      extension = "jpg"
    media_id = self.json["media_id"]
    url = "https://i.nhentai.net/galleries/%s/%s.%s" % (media_id, value, extension)
    return url
   
class Iterdata:
  def __init__(self,data):
    self.data = data
    self._index = -1
    self.temptxt = []
  def __iter__(self):
    return self
  def __enter__(self):
    self.txt_line = open(self.data,"r")
    for rawline in self.txt_line:
      for tline in rawline.replace(","," ").split():
        if not tline.isdigit():
          continue
        if len(tline) > 6:
          long_line = re.findall('.{1,6}', tline)
          for fixline in long_line:
            self.temptxt.append(fixline)
        self.temptxt.append(tline)
    return self
  def __next__(self):
    self._index += 1 
    if self._index >= len(self.temptxt):
      raise StopIteration
    return self.temptxt[self._index] 
  def __reversed__(self):
    return self.temptxt[::-1]
  def __exit__(self,tp,v,tb):
    self.txt_line.close()
    
