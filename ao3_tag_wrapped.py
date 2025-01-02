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
from collections import defaultdict

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
wrapped_year = int(input("Enter year: "))

filterable_answer = input("Can your tag be filtered on? (y/n) ")

# default to False
isFilterable = False

if (filterable_answer == 'y'):
  isFilterable = True
elif (filterable_answer == 'n'):
  isFilterable = False
else:
  print("Invalid answer.")
  exit()

tag_link = input("Link to the tag's page: ")

if isFilterable:
  filter_suffix = "?commit=Sort+and+Filter&page=1&work_search%5Bcomplete%5D=&work_search%5Bcrossover%5D=&work_search%5Bdate_from%5D=&work_search%5Bdate_to%5D=&work_search%5Bexcluded_tag_names%5D=&work_search%5Blanguage_id%5D=&work_search%5Bother_tag_names%5D=&work_search%5Bquery%5D=&work_search%5Bsort_column%5D=created_at&work_search%5Bwords_from%5D=&work_search%5Bwords_to%5D="
  tag_link = tag_link + filter_suffix

myfile = openLink(tag_link, username, pwd)

soup = BeautifulSoup(myfile, 'html.parser')

# find total number of pages
nav = soup.find("ol", attrs={"role":"navigation"})
if nav is None:
  last_page = 1
else:
  pages = nav.findAll("a")
  last_page = int(pages[-2].text)

### A work is broken down into 3 main components
# fics: name, author, fandom, 4 squares in front, completion status, datetime
titles = []
authors = []
fandoms = []
ratings = []
if isFilterable:
  monthly_count = defaultdict(int)

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

    # get month and year
    year = v.find('p', attrs={'class':'datetime'}).get_text()[7:]
    month = v.find('p', attrs={'class':'datetime'}).get_text()[3:6]

    # check for mystery work
    mystery = v.find('div', attrs={'class':'mystery header picture module'})

    # check for unrevealed work
    status = v.find('span', attrs={'class':'status'})

    # filtering
    if int(year) == int(wrapped_year)-1: # if last update older than 2023, stop loop
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
      if isFilterable:
        monthly_count[month] += 1
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
  
  # update page link
  if isFilterable:
    index = tag_link.find("&page=")
    new_url = tag_link[:index+6] + f"{p}" + tag_link[index+7:]
  else:
    new_url = tag_link + f"?page={p}"
  
  # open next page
  myfile = openLink(new_url, username, pwd)
  soup = BeautifulSoup(myfile, 'html.parser')

#### DATA PROCESSING -------------------------------

ficsTotal = len(titles)
wordsTotal = np.sum(words)

# get 3 longest works
first = second = third = float('-inf')
index_1 = index_2 = index_3 = 0
    
for i in range(len(words)):
  # If current element is greater than first
  if words[i] > first:
    third = second
    index_3 = index_2
    
    second = first
    index_2 = index_1

    first = words[i]
    index_1 = i
        
  # If words[i] is in between first and second then update second
  elif words[i] > second and words[i] != first:
    third = second
    index_3 = index_2

    second = words[i]
    index_2 = i
        
  elif words[i] > third and words[i] != second and words[i] != first:
    third = words[i]
    index_3 = i

# list of tuple of 3 in (word count, title, author) format in descending order
top3LongestWork = [(words[index_1], titles[index_1], authors[index_1][0]), (words[index_2], titles[index_2], authors[index_2][0]), (words[index_3], titles[index_3], authors[index_3][0])]

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

#### DATA FILE -------------------------------
f = open("tag_data.csv", "a")
# headers
f.write("Top Author,Work Count,Top Characters,Work Count,Top Fandoms,Work Count,Top Tags,Work Count,Top Warnings,Work Count,Top Ratings,Work Count,Top Relationships,Work Count\n")
# data
writeMultipleLists(f, topAuthors, topCharacters, topFandoms, topTags, topWarnings, topRating, topShips)
f.close()

#### ANALYSIS FILE -------------------------------
f = open("tag_analysis.csv", "a")
# trivia
f.write("Total work produced,"+f"{ficsTotal}\n"+"Total words written,"+f"{wordsTotal}"+"\n")

# top 3 longest works
f.write("Top 3 Longest Work\nWork Count,Title,Author\n")
for item in top3LongestWork:
  f.write(f"{item[0]},{item[1]},{item[2]}\n")

if isFilterable:
  # work count by month
  f.write("Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec\n")
  f.write(f"{monthly_count['Jan']},{monthly_count['Feb']},{monthly_count['Mar']},{monthly_count['Apr']},{monthly_count['May']},{monthly_count['Jun']},{monthly_count['Jul']},{monthly_count['Aug']},{monthly_count['Sep']},{monthly_count['Oct']},{monthly_count['Nov']},{monthly_count['Dec']},")
f.close()