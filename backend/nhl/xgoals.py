from utility import REGISTRY, Table
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, log_loss
from xgboost.sklearn import XGBClassifier
import joblib
import numpy


class xGoals(Table):
    def request(self, params: dict = {}, train = False):
        params.update({"train": 'train'}) if train else params.update({"train": None})
        self.prefix = params.setdefault('type', None)
        params.setdefault('grace', 5)
        params.setdefault('decay', 1)
        super().request(params)
        
    def digest(self):
        self.data = self.response.mappings().all()
    
    def train(self):
        data = numpy.array(object=[[record.get(key) for key in record.keys()] for record in self.data])

        input_train, input_validation, output_train, output_validation = train_test_split(
            data[:, 4:data.shape[1] - 1], 
            data[:, -1].astype(int), 
            test_size=0.3
        )

        input_validation, input_test, output_validation, output_test = train_test_split(
            input_validation, 
            output_validation, 
            test_size=0.5
        )

        model = XGBClassifier(
            scale_pos_weight=1, # Balances class imbalances (1 makes no change)
            eval_metric='logloss', # Performance evaluation metric
            reg_lambda=1, # Penalizes large weights
            max_depth=4, # Max tree depth. Higher depth risks overfitting
            learning_rate=0.1, # Shrinks each tree's contribution
            n_estimators=1000, # Number of trees to build
            subsample=0.8, # Fraction of training samples used per tree. Adds randomness by changing samples
            colsample_bytree=0.8, # Fraction of features used per sample. Adds randomness by changing sample features
            min_child_weight=10, # Min sum of weights in a child node
            early_stopping_rounds=25 # Introduces early stopping if metric does not improve after n estimators
        )
        
        model.fit(
            input_train, 
            output_train,
            eval_set=[ (input_train, output_train), (input_validation, output_validation) ]
        )

        predictions = model.predict(input_test)
        probabilities = model.predict_proba(input_test)
        
        print('\n'.join(f"{feature}: {weight:.5f}" for feature, weight in sorted(zip([key for key in list(self.data[0].keys())[4:data.shape[1] - 1]], model.feature_importances_), key=lambda x: x[1], reverse=True)))
        print(classification_report(output_test, predictions))
        print(confusion_matrix(output_test, predictions))
        print("Loss:", log_loss(output_test, probabilities[:, 1]))
        print("ROC AUC:", roc_auc_score(output_test, probabilities[:, 1]))
        print(f"Calibration: {(100 * probabilities[:, 1].sum() / output_test.sum()) - 100}%")

        joblib.dump(model, f"/models/{self.prefix}-xgoals.gz" if self.prefix else "/models/xgoals.gz")
        self.response.close()

    def transform(self):
        if self.data:
            data = numpy.array(object=[[record.get(key) for key in record.keys()] for record in self.data])
            model: XGBClassifier = joblib.load(f"/models/{self.prefix}-xgoals.gz" if self.prefix else "/models/xgoals.gz")
            probabilities = model.predict_proba(data[:, 4:data.shape[1] - 1])

            self.data = [dict(zip(["season_uid", "season_type", "game_uid", "sequence"], [int(value) for value in record])) for record in data[:, :4]]
            for i, record in enumerate(self.data):
                record["xgoals"] = float(probabilities[i, -1])

        super().transform()

REGISTRY["xgoals"] = xGoals(key="xgoals", limit=None)