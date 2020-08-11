import pymongo
from covid19_nowcast.streaming.storage.config_mongodb import *
from covid19_nowcast.streaming.storage import tweets 
import copy
import progressbar
def init_database(connection_url=connection_url, db_name=db_name):
    db=pymongo.MongoClient(connection_url)[db_name]
    tweets.init_collection(db)
    return db

def connect_database(connection_url=connection_url, db_name=db_name):
    db=pymongo.MongoClient(connection_url)[db_name]
    return db

try:
    db=connect_database()
    tweets.init_collection(db)
except Exception as e:
    print("DB error: ",e)

class TimeInterval():
    def __init__(self,date_from,date_to):
        # assert [date_from;date_to[ is not empty
        assert date_from<date_to, "Beginning date {} after or same as end date {}".format(date_from,date_to)
        self.date_from=date_from
        self.date_to=date_to

    def intersect(self, time_interval):
        A1=self.date_from
        A2=self.date_to
        B1=time_interval.date_from
        B2=time_interval.date_to
        #Empty intersection
        if A2<=B1 or B2<=A1: # equals because X2 is an excluded boundary
            return None
        #Inclusion
        if A1>=B1 and A2<=B2:
            return copy.deepcopy(self)
        if B1>=A1 and B2<=A2:
            return copy.deepcopy(time_interval)
        #Left intersection
        if A1<B1 and A2<B2: #A2>B1 is True due to empty intersection test
            return TimeInterval(B1,A2)
        if B1<A1 and B2<A2: #B2>A1 is True due to empty intersection test
            return TimeInterval(A1,B2)
        #Right intersection
        if A1<B2 and A2>B2:
            return TimeInterval(A1,B2)
        if B1<A2 and B2>A2:
            return TimeInterval(B1,A2)
        raise ValueError("No intersection value was found")

    def union(self, time_interval):
        A1=self.date_from
        A2=self.date_to
        B1=time_interval.date_from
        B2=time_interval.date_to

        #Inclusion : take the surrounding interval
        if A1>=B1 and A2<=B2:
            return [copy.deepcopy(time_interval)]
        if B1>=A1 and B2<=A2:
            return [copy.deepcopy(self)]
        #Exclusion
        if A2<B1 or B2<A1: #No equals on X2 this time because it is another case where intervals will be joined together
            return [copy.deepcopy(self),copy.deepcopy(time_interval)]
        #Intervals meet (intersection isn't None or not included boundary meets included boundary)
        #Left
        if A1<B1 and A2>=B1:
            return [TimeInterval(A1,B2)]
        if B1<A1 and B2>=A1:
            return [TimeInterval(B1,A2)]
        #Right
        if A1>B1 and A2>B2:
            return [TimeInterval(B1,A2)]
        if B1>A1 and B2>A2:
            return [TimeInterval(A1,B2)]
        raise ValueError("No union value was found")

    def minus(self, time_interval):
        A1=self.date_from
        A2=self.date_to
        B1=time_interval.date_from
        B2=time_interval.date_to
        #No intersection
        if A2<=B1 or B2<=A1:
            return copy.deepcopy(self) #No interval reduction
        #Full intersection
        if A1>=B1 and A2<=B2:
            return None #No interval left
        #inner minus: A1<B1<B2<A2
        if A1<B1 and A2>B2:
            return [TimeInterval(A1,B1),TimeInterval(B2,A2)]
        #Partial intersection
        #left
        if A1>=B1 and A2>B2:
            return TimeInterval(B2,A2)
        #right
        if A1<B1 and A2>B1:
            return TimeInterval(A1,B1)
        raise ValueError("No minus value was found")

    def __str__(self):
        return "({},{})".format(self.date_from,self.date_to)

class TimeSubsets():
    def __init__(self,time_intervals):
        assert type(time_intervals) is list 
        self.intervals=[t for t in time_intervals if t is not None]

    def intersect(self, time_subsets):
        if time_subsets.intervals==[]:
            return time_subsets

        intervals=[time_subsets.intersect_interval(interval) for interval in self.intervals]
        flat_intervals=[]
        for i in intervals:
            if type(i) is TimeSubsets:
                flat_intervals.extend(i.intervals)
            else:
                raise TypeError
        inter_subset = TimeSubsets(flat_intervals) 
        return inter_subset

    def intersect_interval(self, time_interval):
        intervals=[time_interval.intersect(interval) for interval in self.intervals]
        inter_subset = TimeSubsets(intervals) 
        return inter_subset

    def union(self, time_subsets):
        if time_subsets.intervals==[]:
            return self
        if self.intervals==[]:
            return time_subsets
        
        union_subset=copy.deepcopy(self)
        union_subset.intervals.extend(time_subsets.intervals)
        old_len=len(union_subset.intervals)
        new_len=-1
        while old_len!=new_len and new_len!=1: #self and time_subsets intervals are not empty so union cannot be empty
            intervals=[]
            old_len=len(union_subset.intervals)
            for index,intervalA in enumerate(union_subset.intervals[:-1]):
                for intervalB in union_subset.intervals[index+1:]:
                    new_intervals=intervalA.union(intervalB)
                    for i in new_intervals:
                        if intervals==[] or not(any([f.date_from==i.date_from and f.date_to==i.date_to for f in intervals])):
                            intervals.append(i)
            if len(intervals)>1:
                intervals_includers=[i for i in intervals if not(any([f!=i and f.date_from<=i.date_from and f.date_to>=i.date_to for f in intervals]))]
                intervals=intervals_includers
            new_len=len(intervals)
            union_subset=TimeSubsets(intervals)
        return union_subset

    def union_interval(self, time_interval):
        intervals=[time_interval.union(interval) for interval in self.intervals]
        flat_intervals=[]
        for i in intervals:
            if type(i) is TimeInterval:
                flat_intervals.append(i)
            elif type(i) is list:
                flat_intervals.extend(i)
            else:
                raise TypeError
        union_subset = TimeSubsets(flat_intervals) 
        return union_subset

    def minus(self, time_subsets):
        if time_subsets.intervals==[]:
            return self
        min_subset=copy.deepcopy(self)
        for interval in time_subsets.intervals:
            min_subset=min_subset.minus_interval(interval)
        return min_subset

    def minus_interval(self, time_interval):
        intervals=[interval.minus(time_interval) for interval in self.intervals]
        flat_intervals=[]
        for i in intervals:
            if type(i) is TimeInterval:
                flat_intervals.append(i)
            elif type(i) is list:
                flat_intervals.extend(i)
            elif i is None:
                pass
            else:
                raise TypeError
        min_subset = TimeSubsets(flat_intervals) 
        return min_subset

    def to_tuples(self):
        return [(t.date_from,t.date_to) for t in self.intervals]

    def __str__(self):
        return "TimeSubsets(["+",".join([str(i) for i in self.intervals])+"])"

class DBTimeSubset():
    def __init__(self,country,source,lang):
        time_subsets=[]
        try:
            db=connect_database()
            time_subsets=list(db[col_timesubsets].find({"country":country,"source":source,"lang":lang},{"_id":0}))
        except Exception as e:
            print(e)
        self.country=country
        self.source=source
        self.lang=lang
        self.subsets=TimeSubsets([TimeInterval(t["date_from"],t["date_to"]) for t in time_subsets])

    def subsets_status(self,date_from, date_to):
        new_subset=TimeSubsets([TimeInterval(date_from,date_to)])
        present_subsets=new_subset.intersect(self.subsets)
        missing_subsets=new_subset.minus(present_subsets)
        return present_subsets,missing_subsets

    def insert_data(self,data,time_subsets):
        self.subsets=self.subsets.union(time_subsets)
        db=connect_database()
        if data!=[]:
            data=[{**d, "country":self.country,"source":self.source,"lang":self.lang} for d in data]
            tweets.save(data,db)
        for d in data:
            if d.get("_id",None) is not None:
                del d["_id"]
        #Remove old subsets
        db[col_timesubsets].delete_many({"country":self.country,"source":self.source,"lang":self.lang})
        #Insert union of new ones
        [
            db[col_timesubsets].insert(
                {
                    "country":self.country,"source":self.source,"lang":self.lang,
                    "date_from":interval.date_from,"date_to":interval.date_to
                }
            )
            for interval in self.subsets.intervals
        ]
        return data
    def get_data(self, present_subsets):
        data=[]
        if present_subsets.intervals != []:
            db=connect_database()
            with progressbar.ProgressBar(max_value=len(present_subsets.intervals), prefix="DB subsets: ") as bar:
                i=0
                bar.update(i)
                for date_from, date_to in present_subsets.to_tuples():
                    bar.prefix="Subset {} to {}:".format(date_from,date_to)
                    bar.update(i)
                    data.extend(db[col_data_analyses].find({"country":self.country,
                                                            "source":self.source,
                                                            "lang":self.lang,
                                                            "created_at": {
                                                                "$gte": date_from,
                                                                "$lt": date_to
                                                            }},{"_id":0}))
                    i+=1
                    bar.update(i)
        return data

def get_alarm_words():
    db=connect_database()
    alarms_words=[word["word"] for word in db[col_alarm_words].find({},{"_id":0})]
    return alarms_words