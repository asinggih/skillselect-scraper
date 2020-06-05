## SkillSelect Latest Invitation Round Scraper

My first attempt at using BeautifulSoup4 and Selenium to scrape a website. It's scraping the occupations and minimum points needed for [latest available invitation round of SkillSelect](https://immi.homeaffairs.gov.au/visas/working-in-australia/skillselect/invitation-rounds).

Running the program will create `current_list.txt` , which consists of the latest **invitation round date** and details of the **pro rata occupations**. Everytime we execute `./ss_scrape.py`, it will cross check the live site's date with the date inside `current_list.txt`. If they're different, it will update the text file.

##### Example Content of `current_list.txt`

```txt
11 September 2018

                               name                           minimum_point    date_of_effect
id
2211  Accountants                                                  80        25/05/2018 9:59am
2212  Auditors, Company Secretaries and Corporate Treasurers       80        1/05/2018 10:54am
2334  Electronics Engineer                                         70        15/11/2017 10:32am
2335  Industrial, Mechanical and Production Engineers              70        18/01/2018 9:55pm
2339  Other Engineering Professionals                              75        3/07/2018 6:37pm
2611  ICT Business and System Analysts                             75        28/05/2018 6:25pm
2613  Software and Applications Programmers                        75        20/08/2018 3:13pm
2631  Computer Network Professionals                               70        17/01/2018 11:36am


The data in this table is licenced under a Creative Commons attribution 3.0 Australia licence,
attributed to Australian Government Department of Home Affairs
```

### How to Run The Script

0. install chromedriver using your OS' package manager (e.g., brew)
1. install python 3
2. `virtualenv env -p python3`
3. `source ./env/bin/activate`
4. `pip install -r requirements.txt`
5. `./ss_scrape.py`

##### TODO

-   [x] automatically send me an email if there's changes
-   [x] add this script into crontab
-   []  find better way to send email
