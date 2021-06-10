import configparser
from time import sleep
import shutil
import os
import csv
import sqlite3
import urllib.request
import zipfile
import progressbar
import json
def show_progress(block_num, block_size, total_size):
    global pbar
    if pbar is None:
        pbar = progressbar.ProgressBar(maxval=total_size)
        pbar.start()

    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None
def massCopy(directory,destination):
    print("Copying "+directory+" to "+destination)
    files = os.listdir(directory)
    for file in files:
        fileName = os.path.join(directory,file)
        #print("copying "+fileName)
        if os.path.isfile(fileName):
            shutil.copy(fileName,destination)

def insertIntoDB(filenameCSV,location,query,dataArr):
    dataCSV = csv.reader(open(filenameCSV,encoding='UTF-8'),delimiter=",")
    if(filenameCSV=="realPlayers.csv"):
        next(dataCSV)
    con = sqlite3.connect(location)
    cursor = con.cursor()
    for row in dataCSV:
        data = list()
        for i in dataArr:
            data.append(row[i])
        cursor.execute(query,data)
    con.commit()
    con.close()

pbar = None
#Get Config

if(os.path.isfile("config.cfg") != True):
    print("ConfigFile Not Found, Downloading it")
    urllib.request.urlretrieve("https://tmdataeditor.000webhostapp.com/config.cfg","config.cfg")
    print("Edit File config.cfg with correct values and retry")
    sleep(5)
    exit()
   
cfg = configparser.RawConfigParser()
cfg.read(r"config.cfg")
#Make Backup of the DB and Save
print("Making backups")
try:
    shutil.copyfile(cfg["yourGameSettings"]["gameFolderLocation"]+"\Configs\DefaultConfig.db",cfg["yourGameSettings"]["gameFolderLocation"]+"\Configs\DefaultConfigBackup.db")
except:
    print(cfg["yourGameSettings"]["gameFolderLocation"]+"\Configs\DefaultConfig.db was not found, make sure gameFolderLocation is correct")
    print("Script stops in 10seconds")
    sleep(10)
    exit()

print("Done")
#Download
if(cfg["scriptSettings"].getboolean("downloadFiles")): 
    for link in cfg["downloadURL"]:
        print("Downloading "+link)
        if(link =="realplayerscsv"):
            filename = "realPlayers.csv"
        elif(link == "realtournamentscsv"):
            filename = "realTournaments.csv"
        else:
            filename =cfg["downloadURL"][link].split("/")[-1]
            
        if(cfg["downloadURL"][link].endswith("zip")):
            urllib.request.urlretrieve(cfg["downloadURL"][link],filename,show_progress)
            print("Extracting zip")
            with zipfile.ZipFile(filename,"r") as myZip:
                myZip.extractall("Content/")
            os.remove(filename)
        else:
            urllib.request.urlretrieve(cfg["downloadURL"][link],filename)

for item in cfg["scriptSettings"]:
    if(item.startswith("change")):
        if(cfg["scriptSettings"].getboolean(item)):
            filename= item.replace("change","")

            if(os.path.isdir("Content/"+filename)):
                print("Copying "+filename+" to game folder")
                massCopy("Content/"+filename,cfg["yourGameSettings"]["gameFolderLocation"]+"/Content/"+filename)
                print("Done")
            print("real"+filename+".csv")
            if(os.path.isfile("real"+filename+".csv")):
                print("Inserting "+filename.capitalize()+" into DB")
                query = cfg["queries"][filename]
                data = json.loads(cfg.get("queries",filename+"Data"))
                insertIntoDB("real"+filename+".csv",cfg["yourGameSettings"]["gameFolderLocation"]+"\Configs\DefaultConfig.db",query,data)
print("Saved into Database")
print("All Done")
print("Exit in 30...")
sleep(30)