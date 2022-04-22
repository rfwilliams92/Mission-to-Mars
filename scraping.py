#Importing Modules and Libraries Needed
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    #Instantiating the browser object using Splinter and Selenium webdriver for deployment
    executable_path = {"executable_path" : ChromeDriverManager().install()}
    browser = Browser("chrome", **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    #Running all scraping functions below and storing in a dict
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_update": dt.datetime.now(),
        "hemispheres": mars_hemispheres(browser)
    }

    browser.quit()
    return data


def mars_news(browser):
    #Directing Automated browser to URL
    url = "https://redplanetscience.com/"
    browser.visit(url)

    browser.is_element_present_by_css('div.list_text', wait_time=1)

    #Convert to HTML
    html = browser.html
    news_soup = soup(html, "html.parser")

    #Parsing out the newest article title and article teaser with error handling in function
    try:
        slide_elem = news_soup.select_one("div.list_text")
        news_title = slide_elem.find("div", class_="content_title").get_text()

        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None
    
    return news_title, news_p
#JPL Space Images Featured Image
def featured_image(browser):

    #Directing Automated browser to URL
    url = "https://spaceimages-mars.com/"
    browser.visit(url)

    #Directing Automated browser to click to on full image button
    full_image_elem = browser.find_by_tag("button")[1]
    full_image_elem.click()

    #Convert to HTML
    html = browser.html
    img_soup = soup(html, "html.parser")

    #finding relative image url & creating an absolute url with error handling
    try:
        img_url_rel = img_soup.find("img", class_="fancybox-image").get("src")
    
    except AttributeError:
        return None   
    
    img_url = f"https://spaceimages-mars.com/{img_url_rel}" 
    
    return img_url

def mars_facts():
    #Using Pandas function .read_html to pull the Mars Facts table into a DataFrame
    try:
        df = pd.read_html("https://galaxyfacts-mars.com/")[0]
    except BaseException:
        return None
    
    df.columns=["description", "Mars", "Earth"]
    df.set_index("description", inplace=True)

    #DataFrame back into html format
    return df.to_html()

def mars_hemispheres(browser):
    # Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # retrieve the image urls and titles for each hemisphere.
    html = browser.html
    html_soup = soup(html, 'html.parser')
    div_results = html_soup.find('div', class_="collapsible results")
    items = div_results.find_all('div', "item")

    for item in items:
        title = item.find("h3").text
        href_url = item.find("a")["href"]
        browser.visit(url + href_url)
        html = browser.html
        img_soup = soup(html, "html.parser")
    
        img_div = img_soup.find("div", class_="downloads")
        img_url = img_div.find("a")["href"]
    
        hemispheres = dict({
            "img_url": f"{url}{img_url}",
            "title": title
        })
        hemisphere_image_urls.append(hemispheres)

    return hemisphere_image_urls

if __name__ == "__main__":
    print(scrape_all())