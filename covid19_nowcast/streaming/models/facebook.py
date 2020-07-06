class Post():
    def __init__(self, author, created_at, full_text=None, comments_count=0, shares_count=0, reactions={}, comments=[]):
        self.author = author
        self.created_at =created_at
        self.full_text = full_text 
        self.comments = comments
        self.shares_count = shares_count
        self.comments_count = comments_count
        self.reactions = reactions

    def __str__(self):
        return "Post(author = "+str(self.author)+", created_at = "+str(self.created_at)+", full_text = "+str(self.full_text)+", comments_count = "+str(self.comments_count)+", shares_count = "+str(self.shares_count)+", reactions = "+str(self.reactions)+", comments = "+str([str(comment) for comment in self.comments])+")"
    def to_dict(self):
        return {"author":self.author, "created_at":self.created_at, "full_text":self.full_text, "reactions": self.reactions, "comments_count":self.comments_count, "shares_count":self.shares_count,"comments":[comment.to_dict() for comment in self.comments]}

class Response():
    def __init__ (self,author, created_at, full_text=None, reactions=None):
        self.author = author
        self.created_at =created_at
        self.full_text = full_text 
        self.reactions = reactions
    def __str__(self):
        return "Response(author = "+str(self.author)+", created_at = "+str(self.created_at)+", full_text = "+str(self.full_text)+", reactions = "+str(self.reactions)+")"
    def to_dict(self):
        return {"author":self.author, "created_at":self.created_at, "full_text":self.full_text, "reactions": self.reactions}

class Comment(Response):
    def __init__(self, author, created_at, full_text=None, reactions=None, responses=None):
        super().__init__(author, created_at, full_text, reactions)
        self.responses = responses

    def to_dict(self):
        ret = super().to_dict()
        ret["responses"]=[response.to_dict() for response in self.responses]
        return ret
    def __str__(self):
        return "Comment(author = "+str(self.author)+", created_at = "+str(self.created_at)+", full_text = "+str(self.full_text)+", reactions = "+str(self.reactions)+", responses = "+str([str(comment) for comment in self.responses])+")"

