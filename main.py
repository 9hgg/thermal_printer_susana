from escpos.printer import File, Dummy
from PIL import Image
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from google.cloud import firestore, storage
from datetime import datetime


from PIL import Image
import requests
from io import BytesIO

import unicodedata


def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

# Fetch the service account key JSON file contents
default_app = firebase_admin.initialize_app()
storage_client = storage.Client()
firebase_bucket_name = 'susana-love.appspot.com'
firebase_bucket_client = storage_client.bucket(firebase_bucket_name)
db = firestore.Client()


p = File("/dev/usb/lp1")


def printMessage(message):
    d = Dummy()
    
    print(message)
    message_id = str(message.get("id",""))
    if len(message_id)>0:
        message_url = "https://susana.love/gallery/"+message_id
    else: 
        return


    title = strip_accents(message.get("title",""))
    if len(title) > 0:
        d.set(align="CENTER",text_type="B",height=2,width=2)
        d.text(title+"\n\n")
        d.set(align="LEFT",text_type="NORMAL",height=1,width=1)

    
    body = strip_accents(message.get("body",""))
    if len(body) > 0:
        d.text(body+"\n\n")



    image_path = message.get("imagePath","")
    print("Image path:",image_path)
    if len(image_path) > 0:
        d.set(align="CENTER")
        # get image download url
        blob = firebase_bucket_client.get_blob(image_path[1:])
        blob.make_public()
        url = blob.public_url
        # download image
        response = requests.get(url)
        # convert to PNG
        im = Image.open(BytesIO(response.content))
        im.thumbnail([580,580])
        thumbnail_local_path = "images/"+message_id+".png"
        print(thumbnail_local_path)
        im.save(thumbnail_local_path)
        d.image(thumbnail_local_path) 
        d.set(align="LEFT")


    author = strip_accents(message.get("author",""))
    if len(author) > 0:
        d.set(align="RIGHT",text_type="U")
        d.text("\nBy")
        d.set(text_type="NORMAL")
        d.text(" "+author+"\n")
        d.set(align="LEFT")

    post_date = message.get("postDate","")
    if post_date > 0:
        d.set(align="RIGHT",font="b")
        datestr = datetime.utcfromtimestamp(post_date/1000).strftime('%d-%m-%Y - %H:%M')
        d.text("              "+datestr+"\n")
        d.set(align="LEFT",font="a")


    d.set(align="RIGHT")
    d.qr(message_url, size=4)
    d.set(align="LEFT")
    d.cut()
    p._raw(d.output)


# As an admin, the app has access to read and write all data, regradless of Security Rules
ref = db.collection('messages')
snapshots = ref.get() 
for snapshot in snapshots:
    message = snapshot.to_dict()
    printMessage(message)
    print(message["id"],message["title"], message.get("printDate",-1))
    # break
exit()





im = Image.open(r'image.jpg')
im.thumbnail([580,580])
im.save(r'image.png')
p.image("image.png") 

# d.image("image.jpg")

# good size!
# p.qr("You can readme from your smartphone", size=8)


d.cut()

# send code to printer
# p._raw(d.output)

# print(d.output)


# p.text("Hello World\n"
# p.qr("You can readme from your smartphone")
# p.cut()
# # p.image("fb.png") # works
# p.image("fb.png") # works
