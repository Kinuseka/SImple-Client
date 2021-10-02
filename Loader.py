from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.clock import mainthread
from kivy.uix.boxlayout import BoxLayout
from kivy.cache import Cache

 
import httpx
import asyncio
import Lib
import io
import time
def setLabel(to, txt):
    to.text = txt
    
def Search(self, link):
        self.sutton.disabled = True
        print(link)
        try:
            self.result = Lib.Api(link)
            title = self.result.Title()
        except TypeError as e:
            title = e
        except ValueError as e:
            title = e
        except AttributeError as e:
            title = e
        except Lib.Exceptions.NoResults as e:
            title = e
        except Lib.Exceptions.NoNetwork as e:
            title = e
        if not isinstance(title, Exception):
            self.status.text = title
            self.searched = self.result
            setLabel(self.status2, F"Selected: {self.searched.Title()}")
        else:
            self.searched = False
            if title == 404:
                setLabel(self.status, "No results")
            else:
                setLabel(self.status, "There was an error\n{}".format(title))
                setLabel(self.status2, "Selected: NONE")
            print(title)
        self.Update_button()
        self.sutton.disabled = False
   
def init_cache(identifier, limit):
    Cache.register(identifier,limit=limit,timeout=1200)

def save_cache(identifier, page, object_):
    Cache.append(identifier,page, object_)
 
def load_cache(identifier, page):
    instance = Cache.get(identifier, page)
    return instance

async def threadhandler(self, pages):
    sem = asyncio.Semaphore(4)
    task = []
    async with httpx.AsyncClient() as client:
        for num in range(pages):
            num = num + 1  
            link = self.searched.Direct_link(num)       
            #Loader.threadload(Loader.loadimage,self,link,num)
            task.append(asyncio.ensure_future(threadload(sem,self,link,num,client)))
        await asyncio.gather(*task)

    
    
async def threadload(sem,*args):
    async with sem: 
        return await loadimage(*args)


async def loadimage(self,link,page,client):
    print(link)
    box = BoxLayout(size_hint=(1,None),size=self.size,orientation="vertical")
    addbox(box,self.hill)
    identifier = self.searched.Id()
    format_ = self.searched.format_find(page)
    cacheimg = load_cache(identifier, page)
    res = self.searched.Metadata(page,data='res')
    
    if cacheimg:
        print('CACHE FOUND DFOFOFO')
    else:
        init_cache(self.searched.Id(),self.searched.Id())
    bimage = await _downloadimage(link,client)   
    save_cache(identifier, page, bimage)
    
    #Image Process 
    #imgs = io.StringIO(bimage)
    bytes = io.BytesIO(bimage)
    bytes.seek(0)
    filename = f"{identifier}_{id}.{format_}"
    txt = CoreImage(bytes,ext=format_)
    renderimage(txt,box)
    
@mainthread    
def addbox(what,layout):
      layout.add_widget(what)
      #what.add_widget(Image(source='images/n.jpg'))
@mainthread
def renderimage(txt,layout):
    img = Image(texture=txt.texture)
    layout.add_widget(img)
    
    
    
async def _downloadimage(link,client):
    for trys in range(5):
        try:
            async with client.stream('GET', link) as response:
                buffer = b''
                async for chunk in response.aiter_bytes(1024):
                    buffer = buffer + chunk
                return buffer      
        except httpx.HTTPError as e:
            print(f'retrying page:{trys}')
            await asyncio.sleep(2)
     
    
        
    
    
    
