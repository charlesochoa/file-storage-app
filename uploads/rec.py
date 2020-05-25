import mysql.connector

from cmd import Cmd
from lenskit.datasets import *
from lenskit import batch, topn, util
from lenskit import crossfold as xf
from lenskit.algorithms import Recommender, als, funksvd, basic, user_knn as uknn,  item_knn as iknn
import pandas as pd

def load_reviews_from_csv():
  path = "C:\\Users\\rheligon\\Desktop\\Sesion3\\ml-latest-small"
  movie_lens = MovieLens(path)
  return movie_lens.ratings

def load_reviews_from_table():
  conn = mysql.connector.connect(
  user='root', 
  password='gabo110991', 
  host='localhost', 
  database='movies', 
  auth_plugin='mysql_native_password')

  try:
    query = pd.read_sql_query(
    '''
      select userId, review.movieId, rating, dateId, timeId
      from review
      group by dateId, timeId, userId
      limit 100000
    ''', conn)

    df = pd.DataFrame(query, columns=['userId','movieId', 'rating'])
    df.rename(columns={'userId': 'user','movieId': 'item'}, inplace=True)
    return df
  finally:
    conn.close()

def load_user_reviews_from_table(userId):
  conn = mysql.connector.connect(
  user='root', 
  password='gabo110991', 
  host='localhost', 
  database='movies', 
  auth_plugin='mysql_native_password')

  try:
    query = pd.read_sql_query(
    '''
      select userId, review.movieId, rating, dateId, timeId 
      from review
      where userId='''+str(userId)+'''
      group by dateId, timeId, userId
    ''', conn)

    df = pd.DataFrame(query, columns=['userId','movieId', 'rating'])
    df.rename(columns={'userId': 'user','movieId': 'item'}, inplace=True)
    return df
  finally:
    conn.close()

def batch_eval(aname, algo, train, test):
  fittable = util.clone(algo)
  fittable = Recommender.adapt(fittable)
  fittable.fit(train)
  users = test.user.unique()
  # Now we run the recommender
  recs = batch.recommend(fittable, users, 10)
  # Add the algorithm name for analyzability
  recs['Algorithm'] = aname
  return recs

def user_eval(aname, algo, train, userId):
  fittable = util.clone(algo)
  fittable = Recommender.adapt(fittable)
  fittable.fit(train)
  #user_ratings = load_user_reviews_from_table(userId)

  # Now we run the recommender
  recs = fittable.recommend(userId, 10)
  #recs = fittable.recommend(userId, 10, ratings=user_ratings)
  # Add the algorithm name for analyzability
  recs['Algorithm'] = aname
  return recs

def all_movie_recommends(ratings, optionList):
  all_recs = []
  test_data = []

  #Declare algorithm models
  basic_bias_model = basic.Bias()
  knn_model = iknn.ItemItem(20)
  knn_u_model = uknn.UserUser(20)
  als_b_model = als.BiasedMF(50)
  als_i_model = als.ImplicitMF(50)
  funk_model = funksvd.FunkSVD(50)

  for train, test in xf.partition_users(ratings[['user', 'item', 'rating']], 5, xf.SampleFrac(0.2)):
    test_data.append(test)
    
    for option in optionList:
      if option == 1:
        all_recs.append(batch_eval('BasicBias', basic_bias_model, train, test))
      if option == 2: 
        all_recs.append(batch_eval('ItemItem', knn_model, train, test))
      if option == 3: 
        all_recs.append(batch_eval('UserUser', knn_u_model, train, test))
      if option == 4: 
        all_recs.append(batch_eval('ALS-Biased', als_b_model, train, test))
      if option == 5: 
        all_recs.append(batch_eval('ALS-Implicit', als_i_model, train, test))
      if option == 6: 
        all_recs.append(batch_eval('FunkSVD', funk_model, train, test))

  all_recs = pd.concat(all_recs, ignore_index=True)
  test_data = pd.concat(test_data, ignore_index=True)

  return all_recs, test_data

def user_movie_recommend(ratings, optionList, userId):
  all_recs = []

  for option in optionList:
    if option == 1:
      basic_bias_model = basic.Bias()
      all_recs.append(user_eval('BasicBias', basic_bias_model, ratings, userId))
    if option == 2:
      knn_model = iknn.ItemItem(20)
      all_recs.append(user_eval('ItemItem', knn_model, ratings, userId))
    if option == 3:
      knn_u_model = uknn.UserUser(20)
      all_recs.append(user_eval('UserUser', knn_u_model, ratings, userId))
    if option == 4:
      als_b_model = als.BiasedMF(50)
      all_recs.append(user_eval('ALS-Biased', als_b_model, ratings, userId))
    if option == 5: 
      als_i_model = als.ImplicitMF(50)
      all_recs.append(user_eval('ALS-Implicit', als_i_model, ratings, userId))
    if option == 6: 
      funk_model = funksvd.FunkSVD(50)
      all_recs.append(user_eval('FunkSVD', funk_model, ratings, userId))

  all_recs = pd.concat(all_recs, ignore_index=True)
  
  return all_recs

def metrics(recs, truth):
  rla = topn.RecListAnalysis()
  rla.add_metric(topn.ndcg)
  rla.add_metric(topn.precision)
  results = rla.compute(recs, truth)
  #results.head()

  print(results.groupby('Algorithm').precision.mean())
  print(results.groupby('Algorithm').ndcg.mean())


class MyPrompt(Cmd):
  prompt = 'mrecs> '
  intro = "Welcome! Type ? to list commands"
  ratings = load_reviews_from_table()

  def do_compare(self, args):
    try:
      algoInputList = list(map(int, args.rsplit(",")))
    except:
      print("There has been an error in the parameters. Type 'help compare' for help.")
      return
    recs, test_data = all_movie_recommends(self.ratings, algoInputList)
    metrics(recs, test_data)

  def help_compare(self):
    print("Will execute different algorithms that recommend movies for users and compare them. e.g: 'compare 2,3,4'")
    print("Args: Algorithms (int,int,int)")
    self.algorithm_options()

  def do_add_review(self, args):
    try:
      user, item, rating = args.rsplit(" ", 2)
      user = int(user)
      item = int(item)
      rating = float(rating)
    except:
      print("There has been an error in the parameters. Type 'help add_review' for help.")
      return
    review = pd.DataFrame.from_records([{'user': user, 'item':item, 'rating':rating}])
    self.ratings = self.ratings.append(review, ignore_index = True)
    print("Added Review -> User: "+str(user)+", Movie: "+str(item)+", Rating: "+str(rating))

  def help_add_review(self):
    print("Will add a review for a certain item from the specified user. e.g: 'add_review 1 10 5")
    print("Args: UserId (int), MovieId (int), Rating (float)")
    self.algorithm_options()

  def do_recommend(self, args):
    try:
      userId, algoInputList = args.rsplit(" ", 1)
      algoList = list(map(int, algoInputList.rsplit(",")))
      userId = int(userId)
    except:
      print("There has been an error in the parameters. Type 'help recommend' for help.")
      return
    
    recs = user_movie_recommend(self.ratings, algoList, userId)
    print(recs)
    print("User: "+str(userId)+", Agorithms: "+', '.join(map(str,algoList)))

  def help_recommend(self):
    print("Will execute an algorithm and recommend movies for the user. e.g: 'recommend 5 2,3,4'")
    print("Args: UserId (int), Algorithms (int,int,int)")

  def algorithm_options(self):
    print("========================================")
    print("Algorithms options for recommending are:")
    print("1) BasicBias")
    print("2) ItemItem")
    print("3) UserUser")
    print("4) ALS-Biased")
    print("5) ALS-Implicit")
    print("6) FunkSVD")

  # End prompt
  def do_exit(self, inp):
        print("Bye")
        return True
    
  def help_exit(self):
    print('Exit the application. Shorthand: x q Ctrl-D.')

  def default(self, inp):
    if inp == 'x' or inp == 'q':
      return self.do_exit(inp)

    #Do default
    print("Not recognized: {}".format(inp))

  do_EOF = do_exit
  help_EOF = help_exit
 
if __name__ == '__main__':
    MyPrompt().cmdloop()