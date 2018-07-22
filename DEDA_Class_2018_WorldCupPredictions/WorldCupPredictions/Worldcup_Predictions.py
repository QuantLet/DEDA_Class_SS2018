# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 21:22:54 2018

@author: VWRZTS0
"""
#Import necessary packages
import pandas as pd
import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import random

#Disable warning
pd.options.mode.chained_assignment = None

#Load necessary files
worldcup = open('filepath/WorldCup2018.csv','r')
ranking = open('filepath/FIFA_Ranking.csv', "r")
hist_ranking  = open('filepath/fifa_ranking_1993-2018.csv', "r")
results = pd.read_csv('filepath/results.csv')

#Load information about the World Cup (rounds, teams etc.)
worldcup= worldcup.readlines()
worldcup = [i.replace('"',"") for i in worldcup]
worldcup = [i.replace("ï»¿","") for i in worldcup]
worldcup = [i.replace("\n","") for i in worldcup]
worldcup = [i.split(",") for i in worldcup]
worldcup = pd.DataFrame(worldcup)
worldcup.columns = worldcup.iloc[0]
worldcup = worldcup.drop(0)
worldcup = worldcup.drop(columns=['Date','Location','Result'])

#Create Worldcup Groups
Group_A=['Russia','Saudi Arabia','Uruguay','Egypt']
Group_B=['Portugal','Spain','Morocco','IR Iran']
Group_C=['France','Australia','Peru','Denmark']
Group_D=['Croatia','Nigeria','Iceland','Argentina']
Group_E=['Brazil','Switzerland','Serbia','Costa Rica']
Group_F=['Mexico','Germany','Sweden','Korea Republic']
Group_G=['England','Belgium','Tunisia','Panama']
Group_H=['Japan','Senegal','Colombia','Poland']

#Create list with World Cup Teams
worldcup_teams=Group_A+Group_B+Group_C+Group_D+Group_E+Group_F+Group_G+Group_H
df_worldcupteams=pd.DataFrame(worldcup_teams, columns={'worldcup_teams'})
df_worldcupteams['Points']=0

#Load current FIFA Rankings
ranking = ranking.readlines()
ranking = [i.replace('"', "") for i in ranking]
ranking = [i.split(",") for i in ranking]
ranking = pd.DataFrame(ranking)
ranking = ranking.drop(0)
ranking.columns = ['Position', 'Country', 'Points']
ranking['Position'] = ranking['Position'].apply(pd.to_numeric)
ranking['Points'] = ranking['Points'].apply(pd.to_numeric)

#Load historic FIFA Rankings
hist_ranking = hist_ranking.readlines()
hist_ranking  = [i.replace('"', "") for i in hist_ranking]
hist_ranking = [i.split(",") for i in hist_ranking]
hist_ranking = pd.DataFrame(hist_ranking)
hist_ranking.columns = hist_ranking.iloc[0]
hist_ranking  = hist_ranking[['rank','country_full','rank_date\n']]
hist_ranking.columns = ['rank_home','home_team','date']
hist_ranking = hist_ranking.drop(0)
hist_ranking['rank_home'] = hist_ranking['rank_home'].apply(pd.to_numeric)

#Create a column monthyear for later modification
month = []
for row in hist_ranking['date']:
    month.append(row[:7])
month=pd.Series(month)    
hist_ranking['monthyear'] = month
hist_ranking = hist_ranking.drop(columns=['date'])

#Create another FIFA Ranking dataframe for later modification
hist_ranking_away = hist_ranking.copy()
hist_ranking_away.columns = ['rank_away','away_team','monthyear']

#Establish Winner
winner = []
for i in range (len(results['home_team'])):
    if results ['home_score'][i] > results['away_score'][i]:
        winner.append(results['home_team'][i])
    elif results['home_score'][i] < results ['away_score'][i]:
        winner.append(results['away_team'][i])
    else:
        winner.append('Draw')
winner=pd.Series(winner)
results['winning_team'] = winner.values

#Filter games with World Cup Teams
participants=[]
for i in range(len(results['home_team'])):
    if results['home_team'][i] in worldcup_teams:
        participants.append('yes')
    elif results['away_team'][i] in worldcup_teams:
        participants.append('yes')
    else:
        participants.append('no')
participants=pd.Series(participants)        
results['participatinginWC'] = participants.values

df=results[(results['participatinginWC'] == 'yes')]
worldcupteam_matches = df.iloc[:]

#Transform date column into datetime
worldcupteam_matches['date'] = worldcupteam_matches['date'].astype('datetime64[ns]')
worldcupteam_matches['date'] = [time.date() for time in worldcupteam_matches['date']]

#Filter Data to games from Aug 1993 to recent matches
worldcupteam_matches = worldcupteam_matches[(worldcupteam_matches['date']>datetime.date(1993,7,31))]
relevant_matches=worldcupteam_matches
relevant_matches['date'] = worldcupteam_matches['date'].astype("str")

#Create column monthyear for later modification
monthyear = []
for row in relevant_matches['date']:
    monthyear.append(row[:7])
monthyear=pd.Series(monthyear)    
relevant_matches['monthyear'] = monthyear.values

#Add year and year_weight to include discount factor
year = []
for row in relevant_matches['date']:
    year.append(row[:4])
year=pd.Series(year)
relevant_matches['year'] = year.values
relevant_matches['year'] = worldcupteam_matches['year'].apply(pd.to_numeric)

year_weight = []
for row in relevant_matches['year']:
    if row <= 1998:
        year_weight.append(0.2)
    elif row <= 2003:
        year_weight.append(0.4)
    elif row <= 2008:
        year_weight.append(0.6)
    elif row <= 2012:
        year_weight.append(0.8)
    elif row <= 2017:
        year_weight.append(0.9)
    else:
        year_weight.append(1)
year_weight=pd.Series(year_weight)
relevant_matches['year_weight'] = year_weight.values

#add game_weight to include for importance factor
tournaments = relevant_matches['tournament'].drop_duplicates()

vi_tournament=['FIFA World Cup','UEFA Euro','FIFA World Cup qualification']
i_tournament=['Confederations Cup','African Cup of Nations','UEFA Euro qualification','AFC Asian Cup','Oceania Nations Cup']

game_weight =[]
for game in relevant_matches['tournament']:
    if game in vi_tournament:
        game_weight.append(1)
    elif game in i_tournament:
        game_weight.append(0.75)
    else:
        game_weight.append(0.5)
game_weight=pd.Series(game_weight)
relevant_matches['game_weight'] = game_weight.values

#Drop columns that are not needed for the multinomial logit regression
relevant_matches=relevant_matches.drop(columns=['date','city','country','neutral','participatinginWC','tournament'])
relevant_matches = relevant_matches.reset_index(drop=True)

#Add column that turns winning/draw/losing into integer (home perspective)
relevant_matches.loc[relevant_matches.winning_team == relevant_matches.home_team, 'winning_team_homeperspective'] = 2
relevant_matches.loc[relevant_matches.winning_team == 'Draw', 'winning_team_homeperspective'] = 1
relevant_matches.loc[relevant_matches.winning_team == relevant_matches.away_team, 'winning_team_homeperspective'] = 0

#Add column that turns winning/draw/losing into integer (away perspective)
relevant_matches.loc[relevant_matches.winning_team == relevant_matches.home_team, 'winning_team_awayperspective'] = 0
relevant_matches.loc[relevant_matches.winning_team == 'Draw', 'winning_team_awayperspective'] = 1
relevant_matches.loc[relevant_matches.winning_team == relevant_matches.away_team, 'winning_team_awayperspective'] = 2

#Data cleanin: Replace team names so that dataframes are compatible
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['Czechoslovakia'],'Czech Republic')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['Czechoslovakia'],'Czech Republic')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['China'],'China PR')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['China'],'China PR')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['Ireland'],'Republic of Ireland')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['Ireland'],'Republic of Ireland')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['Burma'],'Myanmar')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['Burma'],'Myanmar')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['French Guyana'],'Guyana')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['French Guyana'],'Guyana')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['Yemen DPR'],'Yemen')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['Yemen DPR'],'Yemen')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['French Guyana'],'Guyana')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['French Guyana'],'Guyana')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['Western Australia'],'Australia')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['Western Australia'],'Australia')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['Vietnam Republic'],'Vietnam')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['Vietnam Republic'],'Vietnam')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['Taiwan'],'Chinese Taipei')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['Taiwan'],'Chinese Taipei')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['North Vietnam'],'Vietnam')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['North Vietnam'],'Vietnam')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['St. Vincent and the Grenadines'],'St. Vincent / Grenadines')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['St. Vincent and the Grenadines'],'St. Vincent / Grenadines')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['Macedonia'],'FYR Macedonia')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['Macedonia'],'FYR Macedonia')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['German DR'],'Germany')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['German DR'],'Germany')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['French Guyana'],'Guyana')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['French Guyana'],'Guyana')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['East Timor'],'Timor-Leste')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['East Timor'],'Timor-Leste')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['Cape Verde'],'Cape Verde Islands')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['Cape Verde'],'Cape Verde Islands')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['Northern Cyprus'],'Cyprus')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['Northern Cyprus'],'Cyprus')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['Bosnia-Herzegovina'],'Bosnia and Herzegovina')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['Bosnia-Herzegovina'],'Bosnia and Herzegovina')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['Curaçao'],'CuraÃ§ao')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['Curaçao'],'CuraÃ§ao')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['Iran'],'IR Iran')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['Iran'],'IR Iran')
worldcup['Home Team'] = worldcup['Home Team'].replace(['Iran'],'IR Iran')
worldcup['Away Team'] = worldcup['Away Team'].replace(['Iran'],'IR Iran')
ranking['Country'] = ranking['Country'].replace(['Iran'], 'IR Iran')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['Ivory Coast'],'CÃ´te d\'Ivoire')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['Ivory Coast'],'CÃ´te d\'Ivoire')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['Kyrgyzstan'],'Kyrgyz Republic')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['Kyrgyzstan'],'Kyrgyz Republic')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['St. Kitts and Nevis'],'St Kitts and Nevis')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['St. Kitts and Nevis'],'St Kitts and Nevis')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['St. Lucia'],'St Lucia')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['St. Lucia'],'St Lucia')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['São Tomé and Príncipe'],'SÃ£o TomÃ© e PrÃ­ncipe')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['São Tomé and Príncipe'],'SÃ£o TomÃ© e PrÃ­ncipe')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['Brunei'],'Brunei Darussalam')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['Brunei'],'Brunei Darussalam')
relevant_matches['home_team'] = relevant_matches['home_team'].replace(['St. Vincent / Grenadines'],'St Vincent and the Grenadines')
relevant_matches['away_team'] = relevant_matches['away_team'].replace(['St. Vincent / Grenadines'],'St Vincent and the Grenadines')

#Drop matches against opponent without ranking index
relevant_matches=relevant_matches[relevant_matches.home_team != "Guadeloupe"]
relevant_matches=relevant_matches[relevant_matches.away_team != "Guadeloupe"]
relevant_matches=relevant_matches[relevant_matches.home_team != "Martinique"]
relevant_matches=relevant_matches[relevant_matches.away_team != "Martinique"]
relevant_matches=relevant_matches[relevant_matches.home_team != "CuraÃ§ao"]
relevant_matches=relevant_matches[relevant_matches.away_team != "CuraÃ§ao"]

#Define dataframes of home team and away team perspective
home_team_matches=relevant_matches[['home_team','away_team','winning_team_homeperspective','monthyear','home_score','away_score','year_weight','game_weight']]
away_team_matches=relevant_matches[['home_team','away_team','winning_team_awayperspective','monthyear','home_score','away_score','year_weight','game_weight']]

#Set goals scored and goales conceded for both dataframes
home_team_matches = home_team_matches.rename(columns={'home_score':'goals_scored', 'away_score':'goals_conceded'})
away_team_matches = away_team_matches.rename(columns={'away_score':'goals_scored', 'home_score':'goals_conceded'})

#Add Ranking for each country depending on date of the game
home_df1 = pd.merge(home_team_matches, hist_ranking, on=['home_team','monthyear'])
away_df1 = pd.merge(home_team_matches, hist_ranking_away, on=['away_team','monthyear'])
home_df2 = pd.merge(away_team_matches, hist_ranking, on=['home_team','monthyear'])
away_df2 = pd.merge(away_team_matches, hist_ranking_away, on=['away_team','monthyear'])

#Merge those Dataframes and add ranking difference
ht_matches= pd.merge(home_df1,away_df1)
ht_matches['ranking_difference']=ht_matches['rank_home']-ht_matches['rank_away']

at_matches= pd.merge(home_df2,away_df2)
at_matches['ranking_difference']=at_matches['rank_home']-at_matches['rank_away']

#Calculate weighted_goals scored and conceded (home)
wgoals_scored_home = ht_matches.goals_scored * ht_matches.year_weight * ht_matches.game_weight
wgoals_conceded_home = ht_matches.goals_conceded * ht_matches.year_weight * ht_matches.game_weight
ht_matches['scored_weighted_home'] = wgoals_scored_home
ht_matches['conceded_weighted_home'] = wgoals_conceded_home
home_ws_team = ht_matches.groupby('home_team', as_index=False)['scored_weighted_home'].mean()
home_cs_team = ht_matches.groupby('home_team',as_index=False)['conceded_weighted_home'].mean()
expectedgoals_home=pd.merge(home_ws_team,home_cs_team, on='home_team')
expectedgoals_home=expectedgoals_home.rename(columns={'home_team':'team'})

#Calculte weighted_goals scored and conceded (away)
wgoals_scored_away = at_matches.goals_scored * at_matches.year_weight * at_matches.game_weight
wgoals_conceded_away = at_matches.goals_conceded * at_matches.year_weight * at_matches.game_weight
at_matches['scored_weighted_away'] = wgoals_scored_away
at_matches['conceded_weighted_away'] = wgoals_conceded_away
away_ws_team = at_matches.groupby('away_team', as_index=False)['scored_weighted_away'].mean()
away_cs_team = at_matches.groupby('away_team',as_index=False)['conceded_weighted_away'].mean()
expectedgoals_away=pd.merge(away_ws_team,away_cs_team, on='away_team')
expectedgoals_away=expectedgoals_away.rename(columns={'away_team':'team'})

#Calculate weighted goal difference to account for home advantage (hypothesis: home_advantage shows no influence)
weightedgd = pd.merge(expectedgoals_home,expectedgoals_away, on='team')
weightedgd['weighted_scored'] = weightedgd['scored_weighted_home']*0.6 + weightedgd['scored_weighted_away']*0.4
weightedgd['weighted_conceded'] =weightedgd['conceded_weighted_home']*0.6 + weightedgd['conceded_weighted_away']*0.4
weightedgd=weightedgd.drop(columns=['scored_weighted_home','scored_weighted_away','conceded_weighted_away','conceded_weighted_home'])

#filter both dataframes regarding games with World Cup Teams (home perspective)
participants1=[]
for i in range(len(ht_matches['home_team'])):
    if ht_matches['home_team'][i] in worldcup_teams:
        participants1.append('yes')
    else:
        participants1.append('no')
participants1=pd.Series(participants1)
ht_matches['participatinginWC'] = participants1.values
df_hometeam=ht_matches[(ht_matches['participatinginWC'] == 'yes')]

#Insert expected goal scores (home)
df_hometeam.insert(0, 'expected_score_home', df_hometeam['home_team'].map(weightedgd.set_index('team')['weighted_scored']))
df_hometeam.insert(1, 'expected_conceded_away', df_hometeam['away_team'].map(weightedgd.set_index('team')['weighted_conceded']))
df_hometeam['offensive_ability'] = df_hometeam['expected_score_home']-df_hometeam['expected_conceded_away']

df_hometeam.insert(1, 'expected_score_away', df_hometeam['away_team'].map(weightedgd.set_index('team')['weighted_scored']))
df_hometeam.insert(3, 'expected_conceded_home', df_hometeam['home_team'].map(weightedgd.set_index('team')['weighted_conceded']))
df_hometeam['defensive_ability'] = df_hometeam['expected_score_away']-df_hometeam['expected_conceded_home']

#Drop unnecessary columns (home)
df_hometeam=df_hometeam.drop(columns=['participatinginWC','away_team','scored_weighted_home','conceded_weighted_home'],axis=1)
df_hometeam=df_hometeam.drop(columns=['expected_score_home','expected_conceded_away','expected_score_away','expected_conceded_home'],axis=1)
df_hometeam=df_hometeam.rename(index=str, columns={"home_team":"team", 'winning_team_homeperspective':'winning_team'})
df_hometeam=df_hometeam.drop(columns=['rank_home','rank_away','monthyear','goals_scored','goals_conceded','year_weight','game_weight'])

#filter both dataframes regarding games with World Cup Teams (away perspective)
participants2=[]
for i in range(len(at_matches['home_team'])):
    if at_matches['away_team'][i] in worldcup_teams:
        participants2.append('yes')
    else:
        participants2.append('no')
participants2=pd.Series(participants2)
at_matches['participatinginWC'] = participants2.values
df_awayteam=at_matches[(at_matches['participatinginWC'] == 'yes')]

#Insert expected goal scores (away)
df_awayteam.insert(0, 'expected_score_home', df_awayteam['away_team'].map(weightedgd.set_index('team')['weighted_scored']))
df_awayteam.insert(1, 'expected_conceded_away', df_awayteam['home_team'].map(weightedgd.set_index('team')['weighted_conceded']))
df_awayteam['offensive_ability'] = df_awayteam['expected_score_home']-df_awayteam['expected_conceded_away']

df_awayteam.insert(1, 'expected_score_away', df_awayteam['home_team'].map(weightedgd.set_index('team')['weighted_scored']))
df_awayteam.insert(3, 'expected_conceded_home', df_awayteam['away_team'].map(weightedgd.set_index('team')['weighted_conceded']))
df_awayteam['defensive_ability'] = df_awayteam['expected_score_away']-df_awayteam['expected_conceded_home']

#Drop unnecessary columns (away)
df_awayteam=df_awayteam.drop(columns=['participatinginWC','home_team','scored_weighted_away','conceded_weighted_away'],axis=1)
df_awayteam=df_awayteam.drop(columns=['expected_score_home','expected_conceded_away','expected_score_away','expected_conceded_home'],axis=1)
df_awayteam=df_awayteam.rename(index=str, columns={"away_team":"team", 'winning_team_awayperspective':'winning_team'})
df_awayteam=df_awayteam.drop(columns=['rank_home','rank_away','monthyear','goals_scored','goals_conceded','year_weight','game_weight'])

#Bring both dataframes together
dataframes=[df_hometeam,df_awayteam]
all_matches=pd.concat(dataframes)
all_matches=all_matches.dropna()

#Create Dummies to apply Logistic Regression
final=pd.get_dummies(all_matches,prefix=None, columns=['team'])

# Separate X and y sets
X = final.drop(['winning_team'], axis=1)
y = final["winning_team"]

# Separate train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=40)

#Train algorithm with data and test 5t
logreg = LogisticRegression()
logreg.fit(X_train, y_train)
score = logreg.score(X_train, y_train)
score2 = logreg.score(X_test, y_test)

#Sh6w accuracy of training and test set
print("Training set accuracy: ", '%.3f'%(score))
print("Test set accuracy: ", '%.3f'%(score2))

#Store Group Stage Games
pred_set_group = []

# We only need the group stage games, so we have to slice the dataset
wc_group = worldcup.iloc[:48, :]
worldcup_16=worldcup.iloc[48:56,:]
worldcup_quarter=worldcup.iloc[56:60]
worldcup_semi=worldcup.iloc[60:62]
worldcup_playoff3rd=worldcup.iloc[62:63]
worldcup_final=worldcup.iloc[63:64]

#Reference Set to know the games and the respective teams
reference_set=wc_group.drop(columns=['Round Number','Group'])

#Ranking difference as a predictor for game outcome
wc_group.insert(0, 'ranking_home', worldcup['Home Team'].map(ranking.set_index('Country')['Position']))
wc_group.insert(2, 'ranking_away', worldcup['Away Team'].map(ranking.set_index('Country')['Position']))
wc_group['ranking_difference']=wc_group['ranking_home']-wc_group['ranking_away']

#Expected goal difference for game outcome
wc_group.insert(0, 'expected_score_home', worldcup['Home Team'].map(weightedgd.set_index('team')['weighted_scored']))
wc_group.insert(1, 'expected_conceded_away', worldcup['Away Team'].map(weightedgd.set_index('team')['weighted_conceded']))
wc_group['offensive_ability'] = wc_group['expected_score_home']-wc_group['expected_conceded_away']

wc_group.insert(1, 'expected_score_away', wc_group['Away Team'].map(weightedgd.set_index('team')['weighted_scored']))
wc_group.insert(3, 'expected_conceded_home', wc_group['Home Team'].map(weightedgd.set_index('team')['weighted_conceded']))
wc_group['defensive_ability'] = wc_group['expected_score_away']-wc_group['expected_conceded_home']

# Loop to add teams to new prediction dataset
for index, row in wc_group.iterrows():
    pred_set_group.append({'team': row['Home Team'], 'ranking_difference': row['ranking_difference'], 'winning_team': None, 'offensive_ability': row['offensive_ability'],'defensive_ability': row['defensive_ability']})
pred_set_group = pd.DataFrame(pred_set_group)


# Get dummy variables and drop winning_team column
pred_set_group = pd.get_dummies(pred_set_group, prefix=None, columns=['team'])


# Add missing columns compared to the model's training dataset
missing_cols = set(final.columns) - set(pred_set_group.columns)
for c in missing_cols:
    pred_set_group[c] = 0
pred_set_group = pred_set_group[final.columns]

# Remove winning team column
pred_set_group = pred_set_group.drop(['winning_team'], axis=1)

#Group matches and add points based on results
predictions = logreg.predict(pred_set_group)
for i in range(wc_group.shape[0]):
    print(reference_set.iloc[i, 0] + " vs. " + reference_set.iloc[i, 1])
    if predictions[i] == 2:
        print("Winner: " + reference_set.iloc[i, 0])
        df_worldcupteams.loc[df_worldcupteams.worldcup_teams == reference_set.iloc[i,0],'Points'] += 3
    elif predictions[i] == 1:
        print("Draw")
        df_worldcupteams.loc[df_worldcupteams.worldcup_teams == reference_set.iloc[i,0],'Points'] += 1
        df_worldcupteams.loc[df_worldcupteams.worldcup_teams == reference_set.iloc[i,1],'Points'] += 1
    elif predictions[i] == 0:
        print("Winner: " + reference_set.iloc[i, 1])
        df_worldcupteams.loc[df_worldcupteams.worldcup_teams == reference_set.iloc[i,1],'Points'] += 3
    print('Probability of ' + reference_set.iloc[i, 0] + ' winning: ', '%.3f'%(logreg.predict_proba(pred_set_group)[i][2]))
    print('Probability of Draw: ', '%.3f'%(logreg.predict_proba(pred_set_group)[i][1]))
    print('Probability of ' + reference_set.iloc[i, 1] + ' winning: ', '%.3f'%(logreg.predict_proba(pred_set_group)[i][0]))
    print("")
    
#Create Dataframe for Teams and their respective Points in the Groups
Groups=[]
for i in range(len(df_worldcupteams['worldcup_teams'])):
    if df_worldcupteams['worldcup_teams'][i] in Group_A:
        Groups.append('A')
    elif df_worldcupteams['worldcup_teams'][i] in Group_B:
        Groups.append('B')
    elif df_worldcupteams['worldcup_teams'][i] in Group_C:
        Groups.append('C')
    elif df_worldcupteams['worldcup_teams'][i] in Group_D:
        Groups.append('D')
    elif df_worldcupteams['worldcup_teams'][i] in Group_E:
        Groups.append('E')
    elif df_worldcupteams['worldcup_teams'][i] in Group_F:
        Groups.append('F')
    elif df_worldcupteams['worldcup_teams'][i] in Group_G:
        Groups.append('G')
    elif df_worldcupteams['worldcup_teams'][i] in Group_H:
        Groups.append('H')
Groupinfo=pd.Series(Groups)
df_worldcupteams['Group'] = Groupinfo.values

#Filter Dataframe to Teams that pass on to the Knockout Rounds (highest Points)
df_groupwinners=df_worldcupteams.iloc[df_worldcupteams.reset_index().groupby(['Group']).Points.nlargest(2).index.levels[1]]
df_groupwinners=df_groupwinners.groupby(["Group"], sort=False).apply(lambda x: x.sort_values(["Points"],ascending=False)).reset_index(drop=True)

#Add Group Rank to each tean
df_groupwinners['group_rank'] = "Winner Group" + " " + df_groupwinners['Group']
df_groupwinners.loc[1::2,"group_rank"] = "Second Group" + " " + df_groupwinners['Group']

#Prepare new dataset for predictions
worldcup_16.insert(0, 'home_team',worldcup_16['Home Team'].map(df_groupwinners.set_index('group_rank')['worldcup_teams']))
worldcup_16.insert(1, 'away_team',worldcup_16['Away Team'].map(df_groupwinners.set_index('group_rank')['worldcup_teams']))

#Get rid of unnecessary data
worldcup_16=worldcup_16.drop(columns=['Round Number','Home Team','Away Team','Group'])

#Add rankings to Teams
worldcup_16.insert(0, 'ranking_home', worldcup_16['home_team'].map(ranking.set_index('Country')['Position']))
worldcup_16.insert(2, 'ranking_away', worldcup_16['away_team'].map(ranking.set_index('Country')['Position']))
worldcup_16['ranking_difference'] = worldcup_16['ranking_home']-worldcup_16['ranking_away']

#expected goal difference for game outcome
worldcup_16.insert(0, 'expected_score_home', worldcup_16['home_team'].map(weightedgd.set_index('team')['weighted_scored']))
worldcup_16.insert(1, 'expected_conceded_away', worldcup_16['away_team'].map(weightedgd.set_index('team')['weighted_conceded']))
worldcup_16['offensive_ability'] = worldcup_16['expected_score_home']-worldcup_16['expected_conceded_away']

worldcup_16.insert(1, 'expected_score_away', worldcup_16['away_team'].map(weightedgd.set_index('team')['weighted_scored']))
worldcup_16.insert(3, 'expected_conceded_home', worldcup_16['home_team'].map(weightedgd.set_index('team')['weighted_conceded']))
worldcup_16['defensive_ability'] = worldcup_16['expected_score_away']-worldcup_16['expected_conceded_home']

#Reference set
reference_set_16 = worldcup_16.drop(columns=['ranking_home','ranking_away','ranking_difference','expected_score_home','expected_conceded_away', 'expected_score_away', 'expected_conceded_home'])


#Prepare new predicition container
pred_set_16=[]

# Loop to add teams to new prediction dataset based on the ranking position of each team
for index, row in worldcup_16.iterrows():
    pred_set_16.append({'team': row['home_team'], 'ranking_difference': row['ranking_difference'], 'winning_team': None, 'offensive_ability': row['offensive_ability'],'defensive_ability': row['defensive_ability']})
    
pred_set_16 = pd.DataFrame(pred_set_16)

# Get dummy variables and drop winning_team column
pred_set_16 = pd.get_dummies(pred_set_16, prefix=None, columns=['team'])

# Add missing columns compared to the model's training dataset
missing_cols = set(final.columns) - set(pred_set_16.columns)
for c in missing_cols:
    pred_set_16[c] = 0
pred_set_16 = pred_set_16[final.columns]

# Remove winning team column
pred_set_16 = pred_set_16.drop(['winning_team'], axis=1)

# Create container for winners
winner_16=[]

#group matches and add points based on results
predictions_16 = logreg.predict(pred_set_16)
print("BEST OF 16")
print("")
for i in range(worldcup_16.shape[0]):
    print(reference_set_16.iloc[i, 0] + " vs. " + reference_set_16.iloc[i, 1])
    if predictions_16[i] == 2:
        winner_16.append(reference_set_16.iloc[i,0])
        print("Winner: " + reference_set_16.iloc[i, 0])
    elif predictions_16[i] == 0:
        winner_16.append(reference_set_16.iloc[i,1])
        print("Winner: " + reference_set_16.iloc[i, 1])
    else:
        random_winner = random.choice([reference_set_16.iloc[i,0],reference_set_16.iloc[i,1]])
        print("Penalty Shootout! Lucky Winner: " + random_winner )
        winner_16.append(random_winner)
   
    print('Probability of ' + reference_set_16.iloc[i, 0] + ' winning: ', '%.3f'%(logreg.predict_proba(pred_set_16)[i][2]))
    print('Probability of P-Shootout: ', '%.3f'%(logreg.predict_proba(pred_set_16)[i][1]))
    print('Probability of ' + reference_set_16.iloc[i, 1] + ' winning: ', '%.3f'%(logreg.predict_proba(pred_set_16)[i][0]))
    print("")
    
#add winner column to dataset
reference_set_16['winner'] = winner_16

#Prepare dataset for quarterfinals
match_16_index=['W49','W50','W51','W52','W53','W54','W55','W56']
reference_set_16['match_index']=match_16_index

#Add Teams into quarterfinal
worldcup_quarter.insert(0, 'home_team',worldcup_quarter['Home Team'].map(reference_set_16.set_index('match_index')['winner']))
worldcup_quarter.insert(1, 'away_team',worldcup_quarter['Away Team'].map(reference_set_16.set_index('match_index')['winner']))
worldcup_quarter = worldcup_quarter.drop(columns=['Round Number','Home Team','Away Team','Group'])

#Add rankings to dataset
worldcup_quarter.insert(0, 'ranking_home', worldcup_quarter['home_team'].map(ranking.set_index('Country')['Position']))
worldcup_quarter.insert(2, 'ranking_away', worldcup_quarter['away_team'].map(ranking.set_index('Country')['Position']))
worldcup_quarter['ranking_difference'] = worldcup_quarter['ranking_home']-worldcup_quarter['ranking_away']

#expected goal difference for game outcome
worldcup_quarter.insert(0, 'expected_score_home', worldcup_quarter['home_team'].map(weightedgd.set_index('team')['weighted_scored']))
worldcup_quarter.insert(1, 'expected_conceded_away', worldcup_quarter['away_team'].map(weightedgd.set_index('team')['weighted_conceded']))
worldcup_quarter['offensive_ability'] = worldcup_quarter['expected_score_home']-worldcup_quarter['expected_conceded_away']

worldcup_quarter.insert(1, 'expected_score_away', worldcup_quarter['away_team'].map(weightedgd.set_index('team')['weighted_scored']))
worldcup_quarter.insert(3, 'expected_conceded_home', worldcup_quarter['home_team'].map(weightedgd.set_index('team')['weighted_conceded']))
worldcup_quarter['defensive_ability'] = worldcup_quarter['expected_score_away']-worldcup_quarter['expected_conceded_home']

#Build reference Set
reference_set_quarter = worldcup_quarter.drop(columns=['ranking_home','ranking_away','ranking_difference','expected_score_home','expected_conceded_away', 'expected_score_away', 'expected_conceded_home'])

#Prepare new predicition container
pred_set_quarter=[]

# Loop to add teams to new prediction dataset based on the ranking position of each team
for index, row in worldcup_quarter.iterrows():
    pred_set_quarter.append({'team': row['home_team'], 'ranking_difference': row['ranking_difference'], 'winning_team': None, 'offensive_ability': row['offensive_ability'],'defensive_ability': row['defensive_ability']})
    
pred_set_quarter = pd.DataFrame(pred_set_quarter)

# Get dummy variables and drop winning_team column
pred_set_quarter = pd.get_dummies(pred_set_quarter, prefix=None, columns=['team'])

# Add missing columns compared to the model's training dataset
missing_cols = set(final.columns) - set(pred_set_quarter.columns)
for c in missing_cols:
    pred_set_quarter[c] = 0
pred_set_quarter = pred_set_quarter[final.columns]

# Remove winning team column
pred_set_quarter = pred_set_quarter.drop(['winning_team'], axis=1)

# Create container to store Quarterfinal Winners
winner_quarter=[]

#group matches and add points based on results
predictions_quarter = logreg.predict(pred_set_quarter)
print("QUARTERFINALS")
print("")
for i in range(worldcup_quarter.shape[0]):
    print(reference_set_quarter.iloc[i, 0] + " vs. " + reference_set_quarter.iloc[i, 1])
    if predictions_quarter[i] == 2:
        print("Winner: " + reference_set_quarter.iloc[i, 0])
        winner_quarter.append(reference_set_quarter.iloc[i,0])
    elif predictions_quarter[i] == 0:
        winner_quarter.append(reference_set_quarter.iloc[i,1])
        print("Winner: " + reference_set_quarter.iloc[i, 1])
    else:
        random_winner = random.choice([reference_set_quarter.iloc[i,0],reference_set_quarter.iloc[i,1]])
        print("Penalty Shootout! Lucky Winner: " + random_winner )
        winner_quarter.append(random_winner)
        
    print('Probability of ' + reference_set_quarter.iloc[i, 0] + ' winning: ', '%.3f'%(logreg.predict_proba(pred_set_quarter)[i][2]))
    print('Probability of P-Shootout: ', '%.3f'%(logreg.predict_proba(pred_set_quarter)[i][1]))
    print('Probability of ' + reference_set_quarter.iloc[i, 1] + ' winning: ', '%.3f'%(logreg.predict_proba(pred_set_quarter)[i][0]))
    print("")
    
#add winner column to dataset
reference_set_quarter['winner'] = winner_quarter

#Prepare dataset for quarterfinals
match_quarter_index=['W57','W58','W59','W60']
reference_set_quarter['match_index']=match_quarter_index

#Aad winning teams to semifinal games
worldcup_semi.insert(0, 'home_team',worldcup_semi['Home Team'].map(reference_set_quarter.set_index('match_index')['winner']))
worldcup_semi.insert(1, 'away_team',worldcup_semi['Away Team'].map(reference_set_quarter.set_index('match_index')['winner']))
worldcup_semi = worldcup_semi.drop(columns=['Round Number','Home Team','Away Team','Group'])

#Add rankings to dataset
worldcup_semi.insert(0, 'ranking_home', worldcup_semi['home_team'].map(ranking.set_index('Country')['Position']))
worldcup_semi.insert(2, 'ranking_away', worldcup_semi['away_team'].map(ranking.set_index('Country')['Position']))
worldcup_semi['ranking_difference'] = worldcup_semi['ranking_home']-worldcup_semi['ranking_away']

#expected goal difference for game outcome
worldcup_semi.insert(0, 'expected_score_home', worldcup_semi['home_team'].map(weightedgd.set_index('team')['weighted_scored']))
worldcup_semi.insert(1, 'expected_conceded_away', worldcup_semi['away_team'].map(weightedgd.set_index('team')['weighted_conceded']))
worldcup_semi['offensive_ability'] = worldcup_semi['expected_score_home']-worldcup_semi['expected_conceded_away']

worldcup_semi.insert(1, 'expected_score_away', worldcup_semi['away_team'].map(weightedgd.set_index('team')['weighted_scored']))
worldcup_semi.insert(3, 'expected_conceded_home', worldcup_semi['home_team'].map(weightedgd.set_index('team')['weighted_conceded']))
worldcup_semi['defensive_ability'] = worldcup_semi['expected_score_away']-worldcup_semi['expected_conceded_home']

#Build reference Set
reference_set_semi = worldcup_semi.drop(columns=['ranking_home','ranking_away','ranking_difference','expected_score_home','expected_conceded_away', 'expected_score_away', 'expected_conceded_home'])


#Prepare new predicition container
pred_set_semi=[]

# Loop to add teams to new prediction dataset based on the ranking position of each team
for index, row in worldcup_semi.iterrows():
    pred_set_semi.append({'team': row['home_team'], 'ranking_difference': row['ranking_difference'], 'winning_team': None, 'offensive_ability': row['offensive_ability'],'defensive_ability': row['defensive_ability']})
  
pred_set_semi = pd.DataFrame(pred_set_semi)

# Get dummy variables and drop winning_team column
pred_set_semi = pd.get_dummies(pred_set_semi, prefix=None, columns=['team'])

# Add missing columns compared to the model's training dataset
missing_cols = set(final.columns) - set(pred_set_semi.columns)
for c in missing_cols:
    pred_set_semi[c] = 0
pred_set_semi = pred_set_semi[final.columns]

# Remove winning team column
pred_set_semi = pred_set_semi.drop(['winning_team'], axis=1)

# Build container to store winner and loser
winner_semi=[]
loser_semi=[]
#group matches and add points based on results
predictions_semi = logreg.predict(pred_set_semi)
print("SEMIFINALS")
print("")
for i in range(worldcup_semi.shape[0]):
    print(reference_set_semi.iloc[i, 0] + " vs. " + reference_set_semi.iloc[i, 1])
    if predictions_semi[i] == 2:
        print("Winner: " + reference_set_semi.iloc[i, 0])
        winner_semi.append(reference_set_semi.iloc[i,0])
        loser_semi.append(reference_set_semi.iloc[i,1])
    elif predictions_semi[i] == 0:
        winner_semi.append(reference_set_semi.iloc[i,1])
        loser_semi.append(reference_set_semi.iloc[i,0])
        print("Winner: " + reference_set_semi.iloc[i, 1])
    else:
        random_winner = random.choice([reference_set_semi.iloc[i,0],reference_set_semi.iloc[i,1]])
        print("Penalty Shootout! Lucky Winner: " + random_winner )
        winner_semi.append(random_winner)
           
    print('Probability of ' + reference_set_semi.iloc[i, 0] + ' winning: ', '%.3f'%(logreg.predict_proba(pred_set_semi)[i][2]))
    print('Probability of P-Shootout: ', '%.3f'%(logreg.predict_proba(pred_set_semi)[i][1]))
    print('Probability of ' + reference_set_semi.iloc[i, 1] + ' winning: ', '%.3f'%(logreg.predict_proba(pred_set_semi)[i][0]))
    print("")
    

#add winner and loser column to dataset
reference_set_semi['winner'] = winner_semi
reference_set_semi['loser'] = loser_semi

#Prepare dataset for Finals and Playoff 3rd Place
match_semi_index_win=['W61','W62']
reference_set_semi['match_index_win']=match_semi_index_win
match_semi_index_lose=['L61','L62']
reference_set_semi['match_index_lose']=match_semi_index_lose

#Get teams in both finals and playoff from the Semifinals and add them to the Worldcup final datasets
worldcup_playoff3rd.insert(0, 'home_team',worldcup_playoff3rd['Home Team'].map(reference_set_semi.set_index('match_index_lose')['loser']))
worldcup_playoff3rd.insert(1, 'away_team',worldcup_playoff3rd['Away Team'].map(reference_set_semi.set_index('match_index_lose')['loser']))
worldcup_playoff3rd = worldcup_playoff3rd.drop(columns=['Round Number','Home Team','Away Team','Group'])

worldcup_final.insert(0, 'home_team',worldcup_final['Home Team'].map(reference_set_semi.set_index('match_index_win')['winner']))
worldcup_final.insert(1, 'away_team',worldcup_final['Away Team'].map(reference_set_semi.set_index('match_index_win')['winner']))
worldcup_final = worldcup_final.drop(columns=['Round Number','Home Team','Away Team','Group'])


#Add rankings to dataset
worldcup_playoff3rd.insert(0, 'ranking_home', worldcup_playoff3rd['home_team'].map(ranking.set_index('Country')['Position']))
worldcup_playoff3rd.insert(2, 'ranking_away', worldcup_playoff3rd['away_team'].map(ranking.set_index('Country')['Position']))
worldcup_playoff3rd['ranking_difference'] = worldcup_playoff3rd['ranking_home']-worldcup_playoff3rd['ranking_away']


worldcup_final.insert(0, 'ranking_home', worldcup_final['home_team'].map(ranking.set_index('Country')['Position']))
worldcup_final.insert(2, 'ranking_away', worldcup_final['away_team'].map(ranking.set_index('Country')['Position']))
worldcup_final['ranking_difference'] = worldcup_final['ranking_home']-worldcup_final['ranking_away']

#expected goal difference for game outcome
worldcup_playoff3rd.insert(0, 'expected_score_home', worldcup_playoff3rd['home_team'].map(weightedgd.set_index('team')['weighted_scored']))
worldcup_playoff3rd.insert(1, 'expected_conceded_away', worldcup_playoff3rd['away_team'].map(weightedgd.set_index('team')['weighted_conceded']))
worldcup_playoff3rd['offensive_ability'] = worldcup_playoff3rd['expected_score_home']-worldcup_playoff3rd['expected_conceded_away']

worldcup_playoff3rd.insert(1, 'expected_score_away', worldcup_playoff3rd['away_team'].map(weightedgd.set_index('team')['weighted_scored']))
worldcup_playoff3rd.insert(3, 'expected_conceded_home', worldcup_playoff3rd['home_team'].map(weightedgd.set_index('team')['weighted_conceded']))
worldcup_playoff3rd['defensive_ability'] = worldcup_playoff3rd['expected_score_away']-worldcup_playoff3rd['expected_conceded_home']

worldcup_final.insert(0, 'expected_score_home', worldcup_final['home_team'].map(weightedgd.set_index('team')['weighted_scored']))
worldcup_final.insert(1, 'expected_conceded_away', worldcup_final['away_team'].map(weightedgd.set_index('team')['weighted_conceded']))
worldcup_final['offensive_ability'] = worldcup_final['expected_score_home']-worldcup_final['expected_conceded_away']

worldcup_final.insert(1, 'expected_score_away', worldcup_final['away_team'].map(weightedgd.set_index('team')['weighted_scored']))
worldcup_final.insert(3, 'expected_conceded_home', worldcup_final['home_team'].map(weightedgd.set_index('team')['weighted_conceded']))
worldcup_final['defensive_ability'] = worldcup_final['expected_score_away']-worldcup_final['expected_conceded_home']

#Build reference Set
reference_set_playoff3rd = worldcup_playoff3rd.drop(columns=['ranking_home','ranking_away','ranking_difference','expected_score_home','expected_conceded_away', 'expected_score_away', 'expected_conceded_home'])
reference_set_final= worldcup_final.drop(columns=['ranking_home','ranking_away','ranking_difference','expected_score_home','expected_conceded_away', 'expected_score_away', 'expected_conceded_home'])

#Prepare new predicition container
pred_set_playoff3rd=[]
pred_set_final=[]

# Loop to add teams to new prediction dataset based on the ranking position of each team
for index, row in worldcup_playoff3rd.iterrows():
    pred_set_playoff3rd.append({'team': row['home_team'], 'ranking_difference': row['ranking_difference'], 'winning_team': None, 'offensive_ability': row['offensive_ability'],'defensive_ability': row['defensive_ability']})
   
pred_set_playoff3rd = pd.DataFrame(pred_set_playoff3rd)

for index, row in worldcup_final.iterrows():
    pred_set_final.append({'team': row['home_team'], 'ranking_difference': row['ranking_difference'], 'winning_team': None, 'offensive_ability': row['offensive_ability'],'defensive_ability': row['defensive_ability']})
     
pred_set_final = pd.DataFrame(pred_set_final)

# Get dummy variables and drop winning_team column
pred_set_playoff3rd= pd.get_dummies(pred_set_playoff3rd, prefix=None, columns=['team'])
pred_set_final = pd.get_dummies(pred_set_final, prefix=None, columns=['team'])

# Add missing columns compared to the model's training dataset
missing_cols = set(final.columns) - set(pred_set_playoff3rd.columns)
for c in missing_cols:
    pred_set_playoff3rd[c] = 0
pred_set_playoff3rd = pred_set_playoff3rd[final.columns]


missing_cols = set(final.columns) - set(pred_set_final.columns)
for c in missing_cols:
    pred_set_final[c] = 0
pred_set_final = pred_set_final[final.columns]

# Remove winning team column
pred_set_playoff3rd = pred_set_playoff3rd.drop(['winning_team'], axis=1)
pred_set_final = pred_set_final.drop(['winning_team'], axis=1)


#group matches and add points based on results
predictions_playoff3rd = logreg.predict(pred_set_playoff3rd)
print ('PLAY-OFF FOR THIRD PLACE')
print("")
for i in range(worldcup_playoff3rd.shape[0]):
    print(reference_set_playoff3rd.iloc[i, 0] + " vs. " + reference_set_playoff3rd.iloc[i, 1])
    if predictions_playoff3rd[i] == 2:
        print("Winner: " + reference_set_playoff3rd.iloc[i, 0])
    elif predictions_playoff3rd[i] == 0:
        print("Winner: " + reference_set_playoff3rd.iloc[i, 1])
    else:
        print("No Winner")
        random_winner = random.choice([reference_set_playoff3rd.iloc[i,0],reference_set_playoff3rd.iloc[i,1]])
        print("Penalty Shootout! Lucky Winner: " + random_winner )
            
print('Probability of ' + reference_set_playoff3rd.iloc[i, 0] + ' winning: ', '%.3f'%(logreg.predict_proba(pred_set_playoff3rd)[i][2]))
print('Probability of P-Shootout: ', '%.3f'%(logreg.predict_proba(pred_set_playoff3rd)[i][1]))
print('Probability of ' + reference_set_playoff3rd.iloc[i, 1] + ' winning: ', '%.3f'%(logreg.predict_proba(pred_set_playoff3rd)[i][0]))
print("")

#group matches and add points based on results
predictions_final = logreg.predict(pred_set_final)
print("FINAL")
print("")
for i in range(worldcup_final.shape[0]):
    print(reference_set_final.iloc[i, 0] + " vs. " + reference_set_final.iloc[i, 1])
    if predictions_final[i] == 2:
        print("Winner: " + reference_set_final.iloc[i, 0])
    elif predictions_final[i] == 0:
        print("Winner: " + reference_set_final.iloc[i, 1])
    else:
        print("No Winner")
        random_winner = random.choice([reference_set_final.iloc[i,0],reference_set_final.iloc[i,1]])
        print("Penalty Shootout! Lucky Winner: " + random_winner ) 
print('Probability of ' + reference_set_final.iloc[i, 0] + ' winning: ', '%.3f'%(logreg.predict_proba(pred_set_final)[i][2]))
print('Probability of P-Shootout: ', '%.3f'%(logreg.predict_proba(pred_set_final)[i][1]))
print('Probability of ' + reference_set_final.iloc[i, 1] + ' winning: ', '%.3f'%(logreg.predict_proba(pred_set_final)[i][0]))
print("")
