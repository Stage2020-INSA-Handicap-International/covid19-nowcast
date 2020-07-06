class Post():
    def __init__(self, author, created_at, full_text=None, comments_count=0, shares_count=0, reactions={}, comments=[]):
        self.author = author
        self.created_at =created_at
        self.full_text = full_text 
        self.comments = comments
        self.shares_count = shares_count
        self.comments_count = comments_count
        self.reactions = reactions

class Comment():
    def __init__(self, author, created_at, full_text=None, reactions=None, responses=None):
        self.author = author
        self.created_at =created_at
        self.full_text = full_text 
        self.responses = responses
        self.reactions = reactions

class Response(Comment):
    def __init__ (self,author, created_at, full_text=None, reactions=None):
        super().__init__(author, created_at, full_text, reactions)
