#!/usr/bin/env python
# coding: utf-8

# # International Big Men

# ## Summary 

# Even casuals may have noticed the increase in international stars in the NBA. The current MVP race and recent MVP awards (Jokic '21, Giannis '19 & '20) reflect the increase in international superstars. [Plenty of people have noticed](https://www.nba.com/news/international-big-men-rule-nba-with-their-all-around-skills) that the increase seems to be bigger for big men than for other positions, so I figured let's look into the data!

# There are lots of ways to cut up the data, and I decided to simply look at the proportion of minutes played by international/American players stratified by listed position. I may break it down by heights later, but for now, this is the easiest data to work with. I know that positionless basketball is popular and what a player is listed as doesn't always reflect their role on the court, or their size, but this is a first look.

# Special shoutout to [Sports Reference](https://www.sports-reference.com/) (SR), specifically [Basketball Reference](https://www.basketball-reference.com/) (BR), for all of the data on the players' minutes played, positions, and birth places. 

# In[2]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup as BS


# # Create a dictionary of which players are international

# We'll go through the list of countries in [this list](https://www.basketball-reference.com/friv/birthplaces.fcgi?country=CA&state=) one by one and add the players to a list of international players

# In[3]:


#create a dictionary of foreign born players
international_players = {}                  #List of players born outside of the U.S.

#Estonia has one player
#populate the dictionary with that one player, use that country page to collect the rest of the countries
international_players['Martin Müürsepp'] = "EE"

#use that site to get a list of all the countries represented
r = requests.get('https://www.basketball-reference.com/friv/birthplaces.fcgi?country=EE&state=') 
soup = BS(r.content, 'html.parser')                                #all of the HTML code
all_country_soup = soup.find_all(id="birthplace_2")                #just the column with links to the countries
cleaner_country_soup = BS(str(all_country_soup)).find_all('a')     #links with the countries

#Initialize a list of the HTMLs then populate it
country_htmls = []
for i in range(len(cleaner_country_soup)):
    country_string = "https://www.basketball-reference.com"
    ind1 = str(cleaner_country_soup[i]).index("\"")
    ind2 = str(cleaner_country_soup[i])[ind1 + 1:].index("\"")
    country_string += str(cleaner_country_soup[i])[ind1 + 1: ind2 + ind1 + 1]
    country_htmls.append(country_string)

#Go through the urls and add the players with their names as the key and country as value
for url in country_htmls:
    r = requests.get(url) 
    country_Soup = BS(r.content, 'html.parser')
    country_tables = pd.read_html(url)
    country_table = country_tables[0]
    for i in country_table['Unnamed: 1_level_0', "Player"]:
        international_players[i] = 1                               #will change this later to get the country value


# In[4]:


len(international_players)


# # Create an array of minutes distribution

# We'll create some arrays that we're going to want to populate. We'll look at the 22 year span from the '00-'01 season to the '21-'22 season. For each season, we'll have two arrays (for U.S. vs. international) of five categories (five positions). For players with multiple positions listed, we'll just split the minutes evenly between those positions. In reality, lots of players play multiple positions and at uneven distributions, but BR has one position listed for a vast majority for the players, and for this project, we'll just split the minutes 50-50 for the few players who are listed with multiple positions.

# In[5]:


num_of_seasons = 30
starting_year = 1992
minutes_Totals = np.zeros((num_of_seasons,2,5))         #initialize the array of minutes. 


# We'll define some helper functions that we'll call below which will help us fill in the data for each season

# In[7]:


def fill_minutes_from_season(tbl, yr):
    """
    A helper function which takes in a table for the stats for the year and one by one
    calls another helper function to input the minutes into the right array.
    Note that when a player is traded during the season and has minutes for both teams, we have additional rows
    for that player. We keep only the first row, the total minutes. Returns nothing
    """
    seen_this_season = [" "]                 #keep a list of the players we've seen so we don't double count
    num_of_players = len(tbl)
    #print("The number of players who played in", starting_year + i, "was", num_of_players)
    for k in range(num_of_players): 
        player = tbl.iloc[k][["Player", "MP", "Pos"]]
        if player["Player"] != seen_this_season[-1]:           #checks if this player has multiple rows.
            seen_this_season.append(str(player["Player"]))
            fill_minutes(player, yr)                           #helper function


# In[8]:


def fill_minutes(plyr, ano):
    """
    Takes in a player database which includes the player's name, minutes, and position(s). Returns an arr, 
    """
    positions = get_position(plyr)             
    for position in positions:
        if plyr["Player"] in international_players.keys():
            minutes_Totals[ano][0][position] += int(plyr["MP"])/len(positions)
        else:
            minutes_Totals[ano][1][position] += int(plyr["MP"])/len(positions)


# In[9]:


def get_position(guy):
    """
    Converts the string of positions into a list of the positions as integers
    """
    out = []
    s = guy["Pos"]
    string_list_of_pos = s.split("-")
    for a in string_list_of_pos:
        if a == "C":
            out.append(4)
        elif a == "PF":
            out.append(3)
        elif a == "SF":
            out.append(2)
        elif a == "SG":
            out.append(1)
        elif a == "PG":
            out.append(0)
        else:
            print("we have an error with", guy, "and", s, a)
    return out


# In[10]:


for i in range(num_of_seasons):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(starting_year + i) + "_totals.html#totals_stats::7"
    tables = pd.read_html(url) 
    table = pd.DataFrame(tables[0])                      #This gives the desired table
    clean_Table = table[["Player", "Pos", "MP"]]         #Select the relevant columns
    clean_Table = clean_Table[clean_Table.Pos != 'Pos']  #Eliminate bad rows
    fill_minutes_from_season(clean_Table, i)             #Call helper functions


# # Now that we have our data, let's graph it

# In[11]:


#compute the percentages of minutes played by international players
ratios = 100*minutes_Totals[:,0]/(minutes_Totals[:,0] + minutes_Totals[:,1])

#find the totals agnostic to position
positionless_minutes = 100*np.sum(minutes_Totals[:,0], axis = 1) / np.sum(minutes_Totals, axis = (1,2))


# In[12]:


#useful arrays for graphs
position_names = ["PG", "SG", "SF", "PF", "C"]
years = np.arange(starting_year, starting_year + num_of_seasons, 1)


# In[13]:


fig, ax = plt.subplots(figsize=(15, 8.1))
for i in range(5):
    ax.plot(years, ratios[:,i], label = position_names[i])
ax.plot(years, positionless_minutes, label = "Total", color = "black")
ax.set_xlabel('Year')  # Add an x-label to the axes.
ax.set_ylabel('Percentage')  # Add a y-label to the axes.
ax.set_title("Percentage of Minutes Played by Foreign-born NBA Players by Position, '"+ str(starting_year)[2:] + "-'" +str(starting_year + num_of_seasons)[2:])  # Add a title to the axes.
plt.legend()
plt.show()


# In[69]:


fig, ax = plt.subplots(figsize=(15, 8.1))
for i in range(5):
    ax.plot(years, ratios[:,i], label = position_names[i])
ax.plot(years, positionless_minutes, label = "Total", color = "black")
ax.set_xlabel('Year')  # Add an x-label to the axes.
ax.set_ylabel('Percentage')  # Add a y-label to the axes.
ax.set_title("Percentage of Minutes Played by Foreign-born NBA Players by Position, '"+ str(starting_year)[2:] + "-'" +str(starting_year + num_of_seasons)[2:])  # Add a title to the axes.
plt.legend()
plt.show()

