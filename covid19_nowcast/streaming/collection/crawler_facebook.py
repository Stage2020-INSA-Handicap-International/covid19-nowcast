from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import progressbar
from streaming.models.facebook import Post,Comment,Response
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
        author=None
        created_at=None
        full_text=None
        comments_count=0
        shares_count=0
        comments_section = parse_comments_section(post)
        reactions=None#._7a9u (always present) or more precisely ._68wo (optional)
        parsed_posts.append(Post(author,created_at,full_text, comments_count, shares_count, reactions, comments_section))
    return parsed_posts

def parse_comments_section(element, selector="._7a9a"):
    comments_section = element.find_elements(By.CSS_SELECTOR, selector)
    assert(len(comments_section) in [0,1])
    comments_section = comments_section[0] if len(comments_section)==1 else None
    print("Comment Section" if comments_section is not None else "No comments")
    return parse_comment_threads(comments_section) if comments_section is not None else None

def parse_comment_threads(element, selector="._7a9a > li"):
    comments = element.find_elements(By.CSS_SELECTOR, selector)
    print("comments",len(comments))
    return [parse_comment(
                    comment_thread,
                    [parse_response(response) for response in parse_responses(comment_thread)]
                ) 
            for comment_thread in comments]

def parse_comment(element, responses, selector="div[aria-label='Commenter']"):
    comment=element.find_element(By.CSS_SELECTOR,selector)
    try:
        print(comment.find_element(By.CSS_SELECTOR, "._3l3x > span").text)
    except:
        print("N/A")
    author, created_at, full_text, reactions = parse_comment_infos(comment)
    parsed_comment=Comment(author, created_at, full_text, reactions, responses)
    return parsed_comment

def parse_comment_infos(element, selector=None):
    author = None
    created_at = None
    full_text = None
    return author, created_at, full_text, parse_reactions(None)

def parse_reactions(element, selector=None):
    return None

def parse_responses(element, selector="div[aria-label='Réponse au commentaire']"):
    responses=element.find_elements(By.CSS_SELECTOR, selector)
    parsed_responses=[]
    print(len(responses))
    return parsed_responses

def parse_response(element):
    return Response(parse_comment_infos(element))

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