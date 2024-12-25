# logging in so that we can read padlocked works
username = input("Username: ")
pwd = input("Password: ")
username = username.replace(' ','')
pwd = pwd.replace(' ','')

from urllib.request import urlopen
from bs4 import BeautifulSoup
import mechanize
import re
import numpy as np
from collections import Counter
import io
import time
import string
import csv

def openLink(link, user, pwd):
  isOpen = False
  while not isOpen:
    try:
      br = mechanize.Browser()
      br.set_handle_robots(False) # ignore robot.txt
      br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
      br.open("https://archiveofourown.org/users/login")

      # log in to your account
      br.select_form(id = "new_user_session_small")
      br["user[login]"] = user
      br["user[password]"] = pwd
      br.submit()

      # open the page of your tag
      response = br.open(link)
      isOpen = True
    except:
      print("Too many request, waiting for a bit and retry it...")
      time.sleep(120)

  myfile = response.get_data()

  br.close()
  time.sleep(2)

  return myfile


### DATA COLLECTION - scrapping your readings -----------------------
wrapped_year = '2024'  # Please type the year in between the apostrophes '' (DO NOT DELETE THE APOSTROPHES! DO NOT PUT SPACES!)

tag_link = input("Link to the tag's page: ")

myfile = openLink(tag_link, username, pwd)

soup = BeautifulSoup(myfile, 'html.parser')

# find total number of pages
nav = soup.find("ol", attrs={"role":"navigation"})
pages = nav.findAll("a")
last_page = int(pages[-2].text)

### A work is broken down into 3 main components
# fics: name, author, fandom, 4 squares in front, completion status, datetime
titles = []
authors = []
fandoms = []
ratings = []

# extras: all the tag block
warnings = []
ships = []
characters = []
tags = []

# stats: language, words, chapters, comments, kudos, hits
words = []

# looping through pages
isDone = False
# open first page
p = 1
while not isDone or p <= last_page:
  print("opening page ", p)

  fics = soup.findAll('div', attrs={'class':"header module"})
  extras = soup.findAll('ul', attrs={'class':"tags commas"})
  stats = soup.findAll('dl', attrs={'class':"stats"})

  for fic in range(len(fics)):
    v = fics[fic]
    s = stats[fic]
    e = extras[fic]

    # get year of visit
    year = v.find('p', attrs={'class':'datetime'}).get_text()[7:]
    # 19 Dec 2024 -> take 2024 only

    # check for mystery work
    mystery = v.find('div', attrs={'class':'mystery header picture module'})

    # check for unrevealed work
    status = v.find('span', attrs={'class':'status'})

    # filtering
    if int(year) == int(wrapped_year)-1: # if last visit older than 2023, stop loop
      isDone = True
    elif int(year) > int(wrapped_year):
      pass
    elif mystery is not None:
      # filter out mystery work
      pass
    elif status == "Unrevealed:":
      # filter out unrevealed work that you can see, delete the line above and below this comment if you dont want to do so
      pass
    else:
      # fics
      heading = v.find('h4', attrs={'class':'heading'})
      title = heading.find(href=re.compile("works")).text
      author = heading.find('a', attrs={'rel':'author'})
      if author is None:
        author = ['Anonymous']
      else:
        author = author.text.replace('(','').replace(')', '').split(' ')

      fandom = [f.text for f in v.findAll('a', attrs={'class':"tag"})]

      rating = [v.findAll('a', attrs={'class':"help symbol question modal"})[0].text]

      # extras
      warning = [f.text for f in e.findAll('li' , attrs={'class':"warnings"})]

      relationship = [f.text for f in e.findAll('li' , attrs={'class':"relationships"})]

      character = [f.text for f in e.findAll('li' , attrs={'class':"characters"})]

      tag = [f.text for f in e.findAll('li' , attrs={'class':"freeforms"})]

      # stats
      word = s.find('dd', attrs={'class':"words"}).text
      if word and word.strip():
        word = int(word.replace(',',""))
      else:
        word = 0

      # record new information
      titles.append(title)
      authors.append(author)
      fandoms.append(fandom)
      ratings.append(rating)

      warnings.append(warning)
      ships.append(relationship)
      characters.append(character)
      tags.append(tag)

      words.append(word)

  p = p+1
  if isDone or p > last_page:
    break
  # open next page
  # update page link, can be different if you filter based on the tag
  new_url = tag_link + f"?page={p}"

  myfile = openLink(new_url, username, pwd)
  soup = BeautifulSoup(myfile, 'html.parser')

#### DATA PROCESSING -------------------------------

ficsTotal = len(titles)
wordsTotal = np.sum(words)

def findTop(a, nb):
  a = list(np.concatenate(a).flat)
  c= Counter(a)
  if len(a)> nb:
    return c.most_common(nb)
  else:
    return c.most_common()

def findTopAuthor(a, nb):
  a = list(np.concatenate(a).flat)
  a = list(filter(lambda x:x.lower() != 'anonymous' and x != "orphan_account", a))
  c= Counter(a)
  if len(a)> nb:
    return c.most_common(nb)
  else:
    return c.most_common()

def findTopTags(a, nb):
  a = list(np.concatenate(a).flat)
  a = list(filter(lambda x:x != 'AO3 Tags - Freeform', a))
  c= Counter(a)
  if len(a)> nb:
    return c.most_common(nb)
  else:
    return c.most_common()

# default to find everything, you can replace the second argument with a number
# (e.g. for top 5, topAuthors = findTopAuthor(authors, 5))
topAuthors = findTopAuthor(authors, len(authors))
topCharacters = findTop(characters, len(characters))
topFandoms = findTop(fandoms, len(fandoms))
topTags = findTopTags(tags, len(tags))
topWarnings = findTop(warnings, len(warnings))
topRating = findTop(ratings, len(ratings))
topShips = findTop(ships, len(ships))

print("total work produced: ", ficsTotal)
print("total words written: ", wordsTotal)

# functions to help writing to a csv file

# write the n-th item of a list. each item if a tuple of 2
def writeItemN(f, customList, n):
  if n > len(customList) - 1:
    # this list has run out of item
    f.write(",,")
  else:
    f.write(customList[n][0] + "," + f"{customList[n][1]}" + ",")

# write items in multiple lists to a file, lists are accessed based on the order they are parsed into the function
def writeMultipleLists(f, *args):
  # find longest list
  loop_lim = 0
  for item in args:
    if len(item) > loop_lim:
      loop_lim = len(item)

  # write data to file
  header_count = len(args)

  for i in range(loop_lim):
    for j in range(header_count):
      writeItemN(f, args[j], i)
    f.write("\n")

# write to csv file
f = open("tag_stats.csv", "a")
# extra info
f.write("Total work produced,"+f"{ficsTotal},"+"Total words written,"+f"{wordsTotal}"+"\n")
# headers
f.write("Top Author,Work Count,Top Characters,Work Count,Top Relationships,Work Count,Top Tags,Work Count,Top Warnings,Work Count\n")
# data
writeMultipleLists(f, topAuthors, topCharacters, topShips, topTags, topWarnings)
f.close()