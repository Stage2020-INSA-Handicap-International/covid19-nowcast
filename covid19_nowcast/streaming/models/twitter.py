class Tweet():
    def __init__(self, id_str, user, created_at, full_text=None, retweet_count=0, favorite_count=0, replies=[]):
        self.id_str=id_str
        self.user = user
        self.created_at =created_at
        self.full_text = full_text 
        self.replies = replies
        self.retweet_count = retweet_count
        self.favorite_count = favorite_count

    def __str__(self):
        return "Tweet(id_str = "+str(self.id_str)+", user = "+str(self.user)+", created_at = "+str(self.created_at)+", full_text = "+str(self.full_text)+", retweet_count = "+str(self.retweet_count)+", favorite_count = "+str(self.favorite_count)+", replies = "+str(self.replies)+")"#[str(comment) for comment in self.replies]+")"
    def to_dict(self):
        return {"id_str":self.id_str, "created_at":self.created_at, "full_text":self.full_text, "user":self.user, "retweet_count": self.retweet_count, "favorite_count":self.favorite_count,"replies":self.replies}#[comment.to_dict() for comment in self.replies]}
