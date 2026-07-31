# Contents
- [Introduction](#introduction)
- [Article (Work-In-Progress)](#article)
  - [Feature Dictionary](#feature-dictionary)
- [Developers](#developers)
  - [Requirements](#requirements)
  - [Getting Started](#getting-started)
  - [Short Instructions](#short-instructions)

# Introduction
Welcome to the [hockeyanalytica.com](https://hockeyanalytica.com/) open-source xGoals model! For general readers, this document includes an article (work-in-progress) dedicated to how we built our xGoals model, what we learned, and how it performed. For developers looking to experiment with our model, there is a developers segment at the end which documents what you need to work with our repository. Input from both general readers and developers is welcomed!

# Article
This article is a work-in-progress, but will be updated. The only content currently present in this segment is the [Feature Dictionary](#feature-dictionary).

## Feature Dictionary
It is worth noting that all 20 features are used regardless of whether the model is configured to train on data from all situations or specific situations like even strength, power-play, empty net, etc. Features that do not provide any new information are handled well by XGBoost and are given no weight to impact the model. For example, when we trained a model using data for only empty net situations, the feature indicating an empty net was given a weight of 0 which completely removed the feature from impacting the final output.

| Feature        | Description |
|----------------|-------------|
| Advantage      | The number of skaters the shooting team has compared to defending team. Positive values means there were x skaters greater than the defending team (power-play). Negative values means there were x skaters less than the defending team (short-handed). |
| Angle RoC      | Finds the angle between a shot and its previous event, and divides that angle by the time taken between both events. |
| Behind Net     | Indicates if a shot was behind the net. |
| Distance RoC   | Finds the distance between a shot and its previous event, and divides that distance by the time taken between both events. |
| Empty Net      | Indicates if a shot was on an empty net. |
| Event Angle    | The angle between a shot and its previous event. |
| Event Distance | The distance between a shot and its previous event. |
| Offwing        | If the shooter was on their offwing. |
| Prev Event     | The type of event that occured before a shot. |
| Rebound        | If a shot came on a rebound opportunity. Rebounds in this model are defined as any shot that came within 3 seconds of a previous shot attempt. |
| Rush           | If a shot came on a rush opportunity. Rush attempts in this model are defined as any shot that came within 3 seceonds of an event from the neutral zone, or any shot that came within 5 seconds of an event from the defenzive zone. |
| Shot           | The type of shot. |
| Shot Angle     | The angle of a shot relative to the center of the goal. A shot directly on the line between the center faceoff dot and the center of the goal has a 0 degree angle. A shot from the goal line have a 90 degree angle. |
| Shot Distance  | Distance between a shot and the center of the goal. |
| Time Change    | Difference in time between a shot and its previous event. |
| Total          | The total number of skaters on the ice. 5v5 = 10 skaters, 5v4 = 9 skaters, 3v3 = 6 skaters, etc. |
| X Change       | The length-wise difference between a shot and its previous event. |
| X Flip         | If a shot and its previous event were on opposite sides of the goal line. |
| Y Change       | The width-wise difference between a shot and its previous event. |
| Y Flip         | If a shot and its previous event crossed the vector between both goals. |

# Developers
This repository is (mostly) a copy + paste of the actual code used by the server running [hockeyanalytica.com](https://hockeyanalytica.com/). Irrelavent directories and files have been removed and modifications have been made to potentially sensitive information, but everything used for our xGoals model is an exact copy.

If you prefer instant gratification or are eager to start, you can skip to the [Short Instructions](#short-instructions) segment.

## Requirements
The only requirements for this repository are `Docker`, which can be installed on your machine from [https://docs.docker.com/get-started/get-docker/](https://docs.docker.com/get-started/get-docker/), and `Git LFS` (for the data) from [https://git-lfs.com/](https://git-lfs.com/). If you are not using linux, you may need to change the image used inside the [Dockerfile](backend/Dockerfile) to avoid errors.

```bash
# Docker Installation Command (Linux)
sudo curl -fsSL https://get.docker.com | sh

# Git LFS Installation Command (Any)
git lfs install
```

## Getting Started
This repository has two parts: a [Database](database/) to store our data, and a [Backend](backend/) for processing that data. Because the backend performs all the data processing, we will prioritize our understanding of the backend. Docker is simply used to run and manage both the database and backend services.

| Service  | Runtime   | Description |
|----------|-----------|-------------|
| Docker   | Permanent | Separates runtime environments for both our database and backend. |
| Database | Permanent | Stores our data for the xGoals model. Extra data is included for those looking to experiment with more featres! |
| Backend  | Temporary | Processes our data for both model training and model inference. Stops immediately once it's shell session is exited. |

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

To start training or making inferences, we need to use the [train](backend/train.py) and [main](backend/main.py) modules from inside the backend's shell as shown below. It is worth noting that the command line supports any model as an input. However, xgoals is currently the only existing model.

```bash
# Trains a Model
python -m train model

# Makes Inferences using a Trained Model
python -m main model
```

Both the [train](backend/train.py) and [main](backend/main.py) modules support inputs. In fact, xGoals already accepts parameters as shown below. Discluding any of the input parameters will result in thier default values being used.

```bash
# Training
python -m train xgoals '{"type": "string", "scale": float, "decay": float}'

# Inference
python -m train xgoals '{"type": "string"}'
```

| Parameter | Values | Description |
|-----------|--------|-------------|
| type      | None   | Sets the models scope to all strengths/situations/types. None is the default. |
| type      | "fs"   | Sets the models scope to 5 on 5 situations with both goalies. |
| type      | "st"   | Sets the models scope to all situations except full strength and empty net situations. |
| type      | "en"   | Sets the models scope to only empty net situations. |
| scale     | 1+     | Weights imbalanced classes so the occurances of the minority class more closely matches the occurances of the majority class. Scale of 1 means keep the natural distribution of classes. 1 is the default. |
| decay     | 0-1    | Determines the decay rate of samples pulled from later seasons. Decay of 1 means all samples of all seasons are used for training. Lower decay rates means older seasons are exponentially smaller. 1 is the default. |

The [config.json](backend/config.json) file is used to set each model's configurations, including the SQL query used to source data for the model. All transformations for the model's data are done inside this SQL query. To examine or modify the features used in our model, find the `query` key for `xgoals` inside [config.json](backend/config.json).

The logic used for our training and inference pipelines can be found inside [xgoals.py](backend/nhl/xgoals.py). To add new models, one can simply append a new configuration inside [config.json](backend/config.json), add a new file `./backend/nhl/model.py` with the model's pipeline logic, and import that file inside [init.py](backend/nhl/__init__.py).

You should run `truncate public.logs` on the database between each new round of inferences to ensure all xgoals values are overwritten in the database. Training is unaffected by the logs table. The logs table is included so developers can verify that generating inferences succeeded.

You can use the [evaluation.sql](evaluation.sql) script to observe the evalution metrics of the inference data. This is the same script we used for evaluating our model results.

## Short Instructions
### Install Docker
Use this link to install: `https://docs.docker.com/get-started/get-docker/`.

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