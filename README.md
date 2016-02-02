#Hypemachine Python Downloader
hypme.py is a Python script to bulk download songs from [HypeMachine](http://hypem.com). The script is fairly
simple to use.

I try to keep this up to date to make note of how HypeMachine is delivering their content so others may learn!
I normally document all my investigations on my personal blog at [blog.fzakaria.com](http://blog.fzakaria.com). I
appreciate all feedback, criticism and help!


##How To Use

1. Make sure you have Python installed (2.7~)

2. Make sure you have [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) installed. I haven't figured out
how to deploy with dependencies yet

3. Open hypeme.py and modify the script to your choosing!

    `AREA_TO_SCRAPE:` Set this variable to what you'd like to scrape. i.e. popular or a username.

    `NUMBER_OF_PAGES:` Number of pages to scrape. For initial download you can set this number really high and later just cron job the script set to 1.


4. Launch the script `python hypeme.py`
