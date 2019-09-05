from pyfpl import datasets
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.metrics import brier_score_loss as bsl
from sklearn.model_selection import cross_val_score


class BaselinePredictor(BaseEstimator, ClassifierMixin):

       '''
       Baseline Predictor specific to whether a player starts or not.
       Uses start_prev and status as predictors
       '''

       def fit(self, X, y):
              pass

       def predict_proba(self, X):

              y = self.predict(X)
              p = sum(y)/X.shape[0]

              y[y==True] = p
              y[y==False] = 1-p

              return y

       def predict(self, X):
              return X['start_prev'] & (X['status'] == 'a')

       def score(self, X, y, sample_weight=None):
              return bsl(y_true=y, y_prob=self.predict_proba(X))

       def accuracy(self, X, y):
              return sum(y == self.predict(X))/y.shape[0]



# - Load dataset
cols = ['element', 'clubid', 'matchid', 'GW', 'was_sub',
       'in_squad', 'minutes',  'web_name', 'value', 'match_no',
       'status', 'position', 'chance_of_playing_this_round', 'chance_of_playing_next_round']

sd = datasets.seasonData(season=2018, cols=cols)


# - Create started column
sd['start'] = (True ^ sd['was_sub']) & sd['in_squad']

# - Create started previous game column
alt_df = sd[['element', 'match_no', 'start']]
alt_df = alt_df.rename(columns={'start': 'start_prev'})
alt_df['match_no'] += 1

sd = sd.merge(alt_df, on=['element', 'match_no'], how='left')
sd = sd.drop(sd[sd['match_no']==1].index)
sd = sd.reset_index(drop=True)

# - Create input and output variables
X = sd[['start_prev', 'status']]
y = sd['start']

# - Look at model outputs for whole data
model = BaselinePredictor()

print('Brier score = {:.3f}'.format(model.score(X, y)))
print('Accuracy = {:.3f}'.format(model.accuracy(X, y)))


# - See what happens when we perform cross validation
score = cross_val_score(model, X, y, cv=3)
print('Cross validation results: ', score)