*Linna Qiao, Project 2, SI 508*

#Project Overview
This project is about getting various kinds of information about national sites in different states.

Here you can:

*  get a list of all the national sites in a state by providing the state's abbreviation.
*  plot all the national sites in the state you just indicate on a map.
*  get a list of 20 nearby places of a national site by providing the sequence number of that site in the previous national sites list.
*  plot all the  nearby places of a national site you just find on a map.

#Introduction to the Files
There are a total of 4 python files you need to run this program and do the things mentioned above. These files are:
*  `alternate_advanced_caching.py`
*  `pro2_nps.py`
*  `states_dict.py`
*  `secrets.py`
Of those 4 files, `pro2_nps.py` is the main file you should run to perform all the functions. All the other three files are all supporting files. The detail about how to interact with the program will be talked in the *Instructions* section.

There are also 3 JSON files that will be generated during you run the main file. These files are just used for caching purpose and will not affect running the main file in any way.

#All Dependencies to Install Before You Run the Code
1. Google API Key
To run this program and do all functions described in the project overview, you need to set up your access for the Google Places API. You will need to get a Google API key following instructions on this website:
https://developers.google.com/places/web-service/get-api-key

After you get the Google API key, you should copy & paste the key into the `secrets.py`, and you are all set.

2. Plot.ly
Plotly is a graphing service that you can work with from Python. It allows you to create many different kinds of graphs, including the ones we will see in this program.

First, you need to go to the official site of Plot.ly: https://plot.ly/ and create an account. You also need to make sure to click on the confirmation email that Plot.ly sends after you create an account, since without this you won’t be able to get an API key that will be needed in this program.

To be able to use Plot.ly from your python programs, you will need to install the Plot.ly module and set up your installation with your private API key. Here are the instructions:

##Installation
To install Plotly's python package, use the package manager pip inside your terminal.
If you don't have pip installed on your machine, click https://pip.pypa.io/en/latest/installing/ for pip's installation instructions.

`$ pip install plotly`
or
`$ sudo pip install plotly`

## Set Credentials
After installing the Plot.ly package, you're ready to fire up python:
`$ python`
and set your credentials:
```python
import plotly
plotly.tools.set_credentials_file(username='DemoAccount', api_key='lr1c37zw81')
```
You'll need to replace 'DemoAccount' and 'lr1c37zw81' with your Plotly username and API key.
Find your API key here https://plot.ly/Auth/login/?next=%2Fsettings%2Fapi.

The initialization step places a special .plotly/.credentials file in your home directory. Your ~/.plotly/.credentials file should look something like this:
```JSON
{
    "username": "DemoAccount",
    "stream_ids": ["ylosqsyet5", "h2ct8btk1s", "oxz4fm883b"],
    "api_key": "lr1c37zw81"
}
```

3. Having BeautifulSoup on Your Computer:
Since you should already set up `pip` when you finish setting up the Plot.ly. You can also use `pip` to install BeautifulSoup if you don't have it on your computer.

Open your terminal window and type in:
`pip install beautifulsoup4`
and you are all set!

#Instructions
Great! Now you are ready to explore and use the program.
This program is interactive. When you run it in the terminal, you can type in different commands to instruct the program to do things you want it to do. Here's a list of commands that you can enter and their corresponding results:

* list <stateabbr> - e.g. list MI
This command lists all the national sites in the state you indicate, with numbers beside them.

* nearby <national_site_number> - e.g. nearby 2
This command lists at most 20 nearby places of the national site with the sequence number in
the national sites list. This command is only available if you have already input list <stateabbr>.

* map - e.g. map
This command displays national sites or nearby places on a map. Whether it displays national
sites or nearby places depends on the last list you searched. If you have not searched for
anything, this command shows nothing.

* exit - e.g. exit
This command exits the program.

* help - e.g. help
This command lists all available commands you can input right now.

The introduction of the program and all instructions will appear again when you run the program so that you don't have to refer back and forth.


#Now you have grasped all the things you need to run this program! Feel free to explore it and get all interesting results you want!
