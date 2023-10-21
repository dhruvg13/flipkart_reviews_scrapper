from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import requests
import logging
from flask import Flask, render_template, request

logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app = Flask(__name__)
@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)

            flipkart_html = bs(flipkartPage, "html.parser")
            x = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del x[0:3]
            cnt = 0
            for i in x:
                productLink = "https://www.flipkart.com" + x.div.div.div.a['href']
                prodRes = requests.get(productLink)
                prod_html = bs(prodRes.text, "html.parser")              
                commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})
                reviews = []
                for commentbox in commentboxes:
                    try:
                        name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                    except:
                        logging.info("name")

                    try:
                        rating = commentbox.div.div.div.div.text
                    except:
                        rating = 'No Rating'
                        logging.info("rating")
                    
                    try:
                        commentHead = commentbox.div.div.div.p.text
                    except:
                        commentHead = 'No Comment Heading'
                        logging.info(commentHead)
            
                    try:
                        comtag = commentbox.div.div.find_all('div', {'class': ''})
                        custComment = comtag[0].div.text
                    except Exception as e:
                        custComment = "no Comment content"
                        logging.info(custComment)
                    
                    cnt = cnt + 1
                    mydict = {"S.no": cnt, "Product": "searchString", "Name": name, "Rating": rating, "CommentHead": commentHead, "Comment": custComment}
                    reviews.append(mydict)

            for data in reviews:
                fw.writerow(data)
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
        
    else:
        return render_template('index.html')
