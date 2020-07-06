from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import progressbar
from streaming.models.facebook import Post,Comment,Response
import re
def search(query, count):
    driver = webdriver.Firefox()
    driver.get(query) 
    with open("covid19_nowcast/streaming/collection/expandall.js", "r") as file:
        code=file.read()

        scroll(driver,count)

        driver.execute_script(code)
        thing = WebDriverWait(driver, timeout=6000).until(lambda d: d.find_element(By.CSS_SELECTOR, "html > p"))
        print(thing.text)

        posts = parse_posts(driver)
        
        # hover = ActionChains(driver).move_to_element(posts[0])
        # hover.perform()

        # tooltip = driver.find_element_by_id("js_31")
        # print(tooltip.text)
    #driver.quit()

def parse_posts(element, selector="._4-u2 ._4-u8"):
    posts = element.find_elements(By.CSS_SELECTOR, selector)
    parsed_posts=[]
    for post in posts:
        author=parse_author(post, "span[class='fwb fcg'] > a") # "span[class='fwb fcg'] > a"
        created_at=parse_date(element,attribute="title") # ".livetimestamp" get_attribute("title")
        full_text=parse_full_text(post, default="N/A", selector="div[data-testid='post_message']") # div[data-testid='post_message']
        comments_count=parse_comments_count(post) # "._1whp ._4vn2"
        shares_count=parse_shares_count(post) # ._355t ._4vn2
        comments_section = parse_comments_section(post)
        reactions=None#._7a9u (always present) or more precisely ._68wo (optional)
        parsed_posts.append(Post(author,created_at,full_text, comments_count, shares_count, reactions, comments_section))
    [print(post.to_dict()) for post in parsed_posts]
    return parsed_posts

def parse_comments_count(element, selector = "._1whp ._4vn2"):
    count=0
    try: 
        count=re.findall("^[0-9].*",element.find_element(By.CSS_SELECTOR, selector))[0] 
    except: 
        pass
    return count

def parse_shares_count(element, selector = "._355t ._4vn2"):
    count=0
    try: 
        count=re.findall("^[0-9].*",element.find_element(By.CSS_SELECTOR, selector))[0] 
    except: 
        pass
    return count

def parse_comments_section(element, default=[], selector="._7a9a"):
    comments_section = element.find_elements(By.CSS_SELECTOR, selector)
    assert(len(comments_section) in [0,1])
    return parse_comment_threads(comments_section[0]) if len(comments_section)==1 else default

def parse_comment_threads(element, selector="._7a9a > li"):
    comments = element.find_elements(By.CSS_SELECTOR, selector)

    return [parse_comment(
                    comment_thread,
                    [parse_response(response) for response in parse_responses(comment_thread)]
                ) 
            for comment_thread in comments]

def parse_comment(element, responses, selector="div[aria-label='Commenter']"):
    comment=element.find_element(By.CSS_SELECTOR,selector)

    parsed_comment=Comment(*parse_comment_infos(comment), responses)
    return parsed_comment

def parse_comment_infos(element):
    author = parse_author(element)
    full_text = parse_full_text(element, "N/A")
    created_at = parse_date(element)
    return author, created_at, full_text, parse_reactions(None)

def parse_author(element, selector="._6qw4"):
    return element.find_element(By.CSS_SELECTOR, selector).text

def parse_full_text(element, default=None, selector="._3l3x > span"):
    full_text=default
    try:
        full_text=element.find_element(By.CSS_SELECTOR, selector).text
    except:
        pass
    return full_text

def parse_date(element, selector = ".livetimestamp", attribute = "data-tooltip-content"):
    return element.find_element(By.CSS_SELECTOR, selector).get_attribute(attribute)

def parse_reactions(element, selector=None):
    return "N/A"

def parse_responses(element, selector="div[aria-label='Réponse au commentaire']"):
    return element.find_elements(By.CSS_SELECTOR, selector)

def parse_response(element):
    return Response(*parse_comment_infos(element))

def scroll(driver,count):
    SCROLL_PAUSE_TIME = 0.5
    posts=driver.find_elements(By.CSS_SELECTOR, "._4-u2 ._4-u8")

    with progressbar.ProgressBar(max_value=count, prefix="Posts: ") as bar:
        while len(posts)<count:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)
            WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.CSS_SELECTOR, "._52jv :not(.async_saving)"))
            posts=driver.find_elements(By.CSS_SELECTOR, "._4-u2 ._4-u8")
            bar.update(min(len(posts),count))