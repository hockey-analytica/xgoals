# Contents
- [Introduction](#introduction)
- [Article](#article)
  - [The Bold Claim](#the-bold-claim)
  - [Feature Dictionary](#feature-dictionary)
  - [Model Pipeline](#model-pipeline)
  - [Training Results](#training-results)
- [Developers](#developers)
  - [Requirements](#requirements)
  - [Getting Started](#getting-started)
  - [Short Instructions](#short-instructions)

# Introduction
Welcome to the [hockeyanalytica.com](https://hockeyanalytica.com/) open-source Expected Goals (xG) model! For general readers, this document includes an article dedicated to how we built our xGoals model, what we learned, and how it performed. For developers looking to experiment with our model, there is a developers segment at the end which documents what you need to work with our repository. Input from both general readers and developers is welcomed!

# Article
Expected Goals (xGoals) calculates the probability of any given shot resulting in a goal. Typically, this statistic is referenced for assessing shot quality and a player/team's ability to generate scoring chances. However, it is our opinion that many models have shifted their focus away from shot-quality and toward raw goal probability. Admittedly, this statement sounds contradictory, but please allow us to explain before brushing off our claim. Keep in mind we are not trying to argue that our theory is correct. The purpose of this article is to open discussion about xGoals in case our theory is correct.

## The Bold Claim
The main value in xGoals is that it helps us evaluate shot quality. We theorize that shot quality is being misrepresented by xGoals models using features unrelated to shot quality. Some such features we have identified to (maybe) distort shot quality include the period, remaining time, home/away identifiers, and score states. These features certainly affect the probability of a shot being a goal, which is why they help models match actual goals scored more closely. But xGoals is not supposed to be an exact match to actual goals scored—that would be redundant. The true value of xGoals is that it tells us the quality of any given shot—even if the shot quality contradicts the actual outcome.

This idea has prompted us to ask some very important questions that we hope will get the hockey stats community thinking:
* How can we prove or disprove that there is a difference between features that are better for goal probability vs shot quality in xGoals models?
* If such a difference is proven to exist, how do we distinguish features that accurately represent shot quality in xGoals models from features that misrepresent shot quality?
* If goal probability is the sole determining factor for shot quality, how can any feature that affects goal probability misrepresent shot quality?
* Do any of the features we identified as misrepresentative of shot quality actually act as proxies for factors that do affect shot quality? Such as strategy changes based on score state that may alter shot quality.
* If these features are indeed proxies, is there still a risk of misrepresentation of shot quality?

Perhaps these questions have already been answered, or perhaps we are the first ones to ask such questions. Regardless, we want to ensure that our xGoals model is optimized to accurately represent shot quality, so we stuck with a conservative feature set that we believe represents our theory well.

## Feature Dictionary
We have selected 20 features for our first xGoals model, all of which we feel have a real impact on shot quality. During our testing, we have experimented with all sorts of approaches: one model per situation, models for different groupings of situations, and we even ventured into the darkness of the dreaded "one model to rule them all" approach. Throughout all these methods, we used the same 20 features for the training of all our models. Yes... even our model for empty-net-only situations used the empty net indicator during training. Fortunately, XGBoost is good at identifying features that fail to provide any value, and it reliably removes them from having any impact on the model.

| Feature        | Description |
|----------------|-------------|
| Advantage      | The number of skaters the shooting team has compared to defending team. Positive values mean there were x skaters greater than the defending team (power-play). Negative values mean there were x skaters less than the defending team (short-handed). |
| Angle RoC      | Finds the angle between a shot and its previous event, and divides that angle by the time taken between both events. |
| Behind Net     | Indicates if a shot was behind the net. |
| Distance RoC   | Finds the distance between a shot and its previous event, and divides that distance by the time taken between both events. |
| Empty Net      | Indicates if a shot was on an empty net. |
| Event Angle    | The angle between a shot and its previous event. |
| Event Distance | The distance between a shot and its previous event. |
| Offwing        | If the shooter was on their offwing. |
| Prev Event     | The type of event that occurred before a shot. |
| Rebound        | If a shot came on a rebound opportunity. Rebounds in this model are defined as any shot that came within 3 seconds of a previous shot attempt. |
| Rush           | If a shot came on a rush opportunity. Rush attempts in this model are defined as any shot that came within 3 seconds of an event from the neutral zone, or any shot that came within 5 seconds of an event from the defensive zone. |
| Shot           | The type of shot. |
| Shot Angle     | The angle of a shot relative to the center of the goal. A shot directly on the line between the center faceoff dot and the center of the goal has a 0 degree angle. A shot from the goal line has a 90 degree angle. |
| Shot Distance  | Distance between a shot and the center of the goal. |
| Time Change    | Difference in time between a shot and its previous event. |
| Total          | The total number of skaters on the ice. 5v5 = 10 skaters, 5v4 = 9 skaters, 3v3 = 6 skaters, etc. |
| X Change       | The length-wise difference between a shot and its previous event. |
| X Flip         | If a shot and its previous event were on opposite sides of the goal line. |
| Y Change       | The width-wise difference between a shot and its previous event. |
| Y Flip         | If a shot and its previous event crossed the vector between both goals. |

## Model Pipeline
In case you missed it from earlier, for our model we used the xGoals gold standard: XGBoost—we love how fitting that name is. Our pipeline is pretty basic, the main thing worth noting is that our data is split into three sets: 70% train, 15% validation, and 15% test.

The only other thing worth mentioning is that our pipeline can be pretty flexible when defining our scope of data to use for training. We can tell it to train one model for all situations or train situation-specific models, and we can tell it to use our full history of samples or to favor more recent samples. We narrowed things down to two approaches: all situations in one model, and three models split between full strength situations, special teams, and empty net situations.

## Training Results
Before we present our results, we want to set expectations by stating that our results are likely to look less appealing than some of the more reputable models that already exist. But this is expected since we have limited our feature set to exclude features that may favor goal probability over shot quality. We are going to keep our results concise by showing the results of only our best performing model.

Surprisingly, we found the best results came from one model for all situations and seasons. Perhaps there really should be "one model to rule them all." We added a few features to help the model distinguish different game situations—such as the shooting team's advantage, total skaters on the ice, and empty net status—so we feel confident that our model could accurately adjust for those changes in gameplay. One area for improvement is that all seasons were weighted equally, so there is a risk that seasons with API or rule changes affecting shot quality are misrepresented.

We can see from the below graph that our model's training and validation loss converged closely and consistently, differing by just `0.001 Log Loss` on the best iteration: ![Loss Curve](images/fit.png)

When testing the model on our test set, it achieved a `0.21439 Log Loss`, `0.78043 AUC`, and a `100.45% Calibration`—which are the results we expect based on the training and validation set results. We also feel that this shows our model is competitive with some of the more reputable models that exist at the time of this writing, especially when we consider the limitations we placed on our feature set.

As for our feature importances, we see the same pattern as many other models. Empty nets, rebounds, and shot distance are our most important features. We also noticed that the model found the count of total skaters on the ice to be the fourth most important feature, which suggests it appropriately adjusts for the diversity in strengths. If you need a reference as to what each feature means, please reference our [Feature Dictionary](#feature-dictionary) that was presented earlier. ![Feature Importances](images/importance.png)

Finally, we will present the seasonal results of our model. Unfortunately, these metrics were not exclusively calculated on our test set because our database has no way to identify what records were from what set. But since our model converged nicely, we expect the results to be similar if we had a way to reduce the scope to just the test set. We define `difference` as the number of xGoals greater than or less than actual goals. Whereas `calibration` represents the percent of xGoals greater than or less than actual goals. Here are the results of all situations across each season. We will go through what we found and areas for improvement afterward. Log Loss and AUC are our main concerns here, calibration is somewhat useful but should be considered less important since we expect shot quality to be different from actual goals scored.

**All Strengths:**
| Season | Difference | Calibration | Log Loss | AUC |
|--------|------------|-------------|----------|-----|
|20252026| 340.83     | 3.86        | 0.236    |0.768|
|20242025| -60.55     | -0.7        | 0.226    |0.779|
|20232024| 85.79      | 0.98        | 0.223    |0.782|
|20222023| 185.47     | 2.05        | 0.231    |0.774|
|20212022| 9.7        | 0.11        | 0.223    |0.779|
|20202021| -112.72    | -2          | 0.217    |0.792|
|20192020| -16.67     | -0.23       | 0.218    |0.79 |
|20182019| -363.25    | -4.4        | 0.218    |0.786|
|20172018| -217.03    | -2.65       | 0.217    |0.786|
|20162017| 10.36      | 0.14        | 0.215    |0.789|
|20152016| 86.62      | 1.19        | 0.212    |0.792|
|20142015| 51.65      | 0.7         | 0.207    |0.789|
|20132014| 0.09       | 0           | 0.208    |0.79 |
|20122013| -51.21     | -1.14       | 0.208    |0.787|
|20112012| 20.96      | 0.28        | 0.206    |0.795|
|20102011| 65.35      | 0.87        | 0.215    |0.789|

**Full Strength (5v5 with both goalies) Results:**
| Season | Difference | Calibration | Log Loss | AUC |
|--------|------------|-------------|----------|-----|
|20252026| 50.27      | 0.89        | 0.209    |0.764|
|20242025| -47.81     | -0.86       | 0.199    |0.773|
|20232024| -8.27      | -0.15       | 0.198    |0.78 |
|20222023| 175.17     | 3.02        | 0.207    |0.768|
|20212022| 4.56       | 0.08        | 0.201    |0.772|
|20202021| -25.51     | -0.69       | 0.193    |0.788|
|20192020| -0.39      | -0.01       | 0.195    |0.786|
|20182019| -169.22    | -3.13       | 0.191    |0.782|
|20172018| -65.43     | -1.26       | 0.19     |0.779|
|20162017| 58.37      | 1.22        | 0.193    |0.785|
|20152016| 133.09     | 2.92        | 0.189    |0.785|
|20142015| 6.72       | 0.14        | 0.185    |0.781|
|20132014| -29.22     | -0.62       | 0.186    |0.782|
|20122013| 2.37       | 0.08        | 0.186    |0.779|
|20112012| 21.71      | 0.46        | 0.185    |0.785|
|20102011| 21.97      | 0.46        | 0.186    |0.786|

**Special Teams (all strengths except full strength and empty net) Results:**
| Season | Difference | Calibration | Log Loss | AUC |
|--------|------------|-------------|----------|-----|
|20252026| 243.02     | 9.3         | 0.31     |0.709|
|20242025| -16.3      | -0.66       | 0.308    |0.714|
|20232024| 99.09      | 3.75        | 0.298    |0.722|
|20222023| 11.85      | 0.43        | 0.302    |0.727|
|20212022| 38.74      | 1.51        | 0.291    |0.728|
|20202021| -69.14     | -4.18       | 0.289    |0.742|
|20192020| -40.21     | -1.81       | 0.282    |0.747|
|20182019| -168.05    | -6.99       | 0.299    |0.727|
|20172018| -137.36    | -5.31       | 0.3      |0.744|
|20162017| -38.37     | -1.68       | 0.288    |0.745|
|20152016| -23.29     | -1          | 0.282    |0.749|
|20142015| 44.11      | 1.88        | 0.274    |0.759|
|20132014| 19.88      | 0.79        | 0.272    |0.766|
|20122013| -43.8      | -3.01       | 0.277    |0.761|
|20112012| 18.56      | 0.76        | 0.267    |0.775|
|20102011| 37.22      | 1.46        | 0.273    |0.756|

**Empty Net (all strengths shooting on an empty net) Results:**
| Season | Difference | Calibration | Log Loss | AUC |
|--------|------------|-------------|----------|-----|
|20252026| 47.53      | 8.71        | 0.789    |0.789|
|20242025| 3.56       | 0.63        | 0.713    |0.758|
|20232024| -5.03      | -1.04       | 0.737    |0.752|
|20222023| -1.56      | -0.34       | 0.742    |0.75 |
|20212022| -33.6      | -6.46       | 0.655    |0.718|
|20202021| -18.08     | -6.19       | 0.903    |0.669|
|20192020| 23.93      | 6.72        | 0.844    |0.688|
|20182019| -25.99     | -5.92       | 0.88     |0.697|
|20172018| -14.24     | -3.69       | 0.62     |0.649|
|20162017| -9.64      | -3.07       | 0.578    |0.718|
|20152016| -23.18     | -5.87       | 0.576    |0.74 |
|20142015| 0.82       | 0.26        | 0.62     |0.671|
|20132014| 10.43      | 4.21        | 0.591    |0.729|
|20122013| -9.78      | -6.65       | 0.555    |0.757|
|20112012| -19.31     | -7.54       | 0.582    |0.722|
|20102011| 6.16       | 2.54        | 0.606    |0.697|

Unfortunately, we see a pattern that the best results are coming from older seasons, and recent seasons seem to be less reliable. This indicates that we should build separate models for different seasons so our website's xGoals can better represent shot quality—which likely has been done by the time you read this! Our model performs best at full strength, and worst at empty net situations. However, since special teams make up so many more shots than empty net situations, we should focus our attention on improving our special teams results. There is plenty of room for improvement. But for our first xGoals model, we think these are acceptable results. We will be making improvements that are beyond the scope of this article, with a prioritization on enhancing our model for recent seasons.

Notably, this model built purely on shot-intrinsic features may also serve as a baseline for testing our [Bold Claim](#the-bold-claim). A natural next step would be to train a comparison model that includes our excluded features, and use both models to test if shot quality really can be misrepresented by our excluded features. Thank you for reading, and please let us know what you think at connect@hockeyanalytica.com.

# Developers
This repository is (mostly) a copy + paste of the actual code used by the server running [hockeyanalytica.com](https://hockeyanalytica.com/). Irrelevant directories and files have been removed and modifications have been made to potentially sensitive information, but everything used for our xGoals model is an exact copy.

If you prefer instant gratification or are eager to start, you can skip to the [Short Instructions](#short-instructions) segment.

## Requirements
The only requirements for this repository are `Docker`, which can be installed on your machine from [https://docs.docker.com/get-started/get-docker/](https://docs.docker.com/get-started/get-docker/), and `Git LFS` (for the data) from [https://git-lfs.com/](https://git-lfs.com/). If you are not using linux, you may need to change the image used inside the [Dockerfile](backend/Dockerfile) to avoid errors.

```bash
# Docker Installation Command (Linux)
sudo curl -fsSL https://get.docker.com | sh

# Git LFS Installation Command (Any)
git lfs install

# Clone Repository
git clone https://github.com/hockey-analytica/xgoals.git
```

## Getting Started
This repository has two parts: a [Database](database/) to store our data, and a [Backend](backend/) for processing that data. Because the backend performs all the data processing, we will prioritize our understanding of the backend. Docker is simply used to run and manage both the database and backend services.

| Service  | Runtime   | Description |
|----------|-----------|-------------|
| Docker   | Permanent | Separates runtime environments for both our database and backend. |
| Database | Permanent | Stores our data for the xGoals model. Extra data is included for those looking to experiment with more features! |
| Backend  | Temporary | Processes our data for both model training and model inference. Stops immediately once its shell session is exited. |

To begin experimenting we must use docker to start our database, insert data into our database, then start running commands inside the backend's shell. The below commands can be used to do all this. Note that linux users may need to use `sudo` for all docker commands.

```bash
# Starts the Database
docker compose up -d

# Inserts Data into the Database
docker compose exec -T database pg_restore -U postgres -d database < data.dump

# Starts the Backend in an Active Shell (Closes Only When Exited)
docker compose run --rm backend sh

# Runs Backend Commands in a Detatched Shell (Closes When Command Completes)
docker compose run -d --rm backend sh -c "<command>"
```

If you wish to export the database data to a csv file, you can use the below placeholder query. To run queries on your machine outside the docker environments, we suggest installing [pgAdmin](https://www.pgadmin.org/).

```bash
COPY (PASTE QUERY TEXT HERE) 
TO '/absolute/path/to/output.csv' 
WITH (FORMAT csv, HEADER true);
```

To start training or making inferences, we need to use the [train](backend/train.py) and [main](backend/main.py) modules from inside the backend's shell as shown below. It is worth noting that the command line supports any model as an input. However, xgoals is currently the only existing model.

```bash
# Trains a Model
python -m train model

# Makes Inferences using a Trained Model
python -m main model
```

Both the [train](backend/train.py) and [main](backend/main.py) modules support inputs. In fact, xGoals already accepts parameters as shown below. Excluding any of the input parameters will result in their default values being used.

```bash
# Training
python -m train xgoals '{"type": "string", "grace": integer, "decay": float}'

# Inference
python -m main xgoals '{"type": "string"}'
```

| Parameter | Values | Description |
|-----------|--------|-------------|
| type      | None   | Sets the models scope to all strengths/situations/types. None is the default. |
| type      | "fs"   | Sets the models scope to 5 on 5 situations with both goalies. |
| type      | "st"   | Sets the models scope to all situations except full strength and empty net situations. |
| type      | "en"   | Sets the models scope to only empty net situations. |
| decay     | 0-1    | Determines the decay rate of samples pulled from older seasons. Decay of 1 means all samples of all seasons are used for training. Lower decay rates means older seasons are exponentially smaller. 1 is the default. |
| grace     | int    | Determines how many seasons will get to keep their full set of samples before we start to remove/decay samples. 5 is the default (5 most recent seasons). |

The [config.json](backend/config.json) file is used to set each model's configurations, including the SQL query used to source data for the model. All transformations for the model's data are done inside this SQL query. To examine or modify the features used in our model, find the `query` key for `xgoals` inside [config.json](backend/config.json).

The logic used for our training and inference pipelines can be found inside [xgoals.py](backend/nhl/xgoals.py). To add new models, one can simply append a new configuration inside [config.json](backend/config.json), add a new file `./backend/nhl/model.py` with the model's pipeline logic, and import that file inside [init.py](backend/nhl/__init__.py).

You should run `truncate public.logs` on the database between each new round of inferences to ensure all xgoals values are overwritten in the database. Training is unaffected by the logs table. The logs table is included so developers can verify that generating inferences succeeded.

You can use the [evaluation.sql](evaluation.sql) script to observe the evaluation metrics of the inference data. This is the same script we used for evaluating our model results.

## Short Instructions
### Install Docker and Git LFS
`Docker` installation can be found at [https://docs.docker.com/get-started/get-docker/](https://docs.docker.com/get-started/get-docker/). `Git LFS` installation can be found at [https://git-lfs.com/](https://git-lfs.com/).

```bash
# Docker Installation Command (Linux)
sudo curl -fsSL https://get.docker.com | sh

# Git LFS Installation Command (Any)
git lfs install
```

### Setup Database
```bash
# Starts the Database
docker compose up -d

# Inserts Data into the Database
docker compose exec -T database pg_restore -U postgres -d database < data.dump
```

### Start Backend
```bash
docker compose run --rm backend sh
```

### Train and Infer
```bash
# Trains a Model
python -m train xgoals

# Makes Inferences using a Trained Model
python -m main xgoals
```
