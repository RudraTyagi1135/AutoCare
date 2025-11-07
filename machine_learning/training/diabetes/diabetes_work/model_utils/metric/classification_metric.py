#import
import sys
from machine_learning.training.diabetes.diabetes_work.entity.artifact_entity import ClassificationMetricArtifact
from autocare_utils.exception import AutoCareException
from sklearn.metrics import f1_score,precision_score,recall_score


def get_classification_score(y_true, y_pred) -> ClassificationMetricArtifact:  #type: ignore

    try:
        model_f1_score = f1_score(y_true , y_pred)
        model_recall_score = recall_score(y_true , y_pred)
        model_precision_score = precision_score(y_true , y_pred)


        classification_metric = ClassificationMetricArtifact(
            f1_score=model_f1_score,  #type: ignore
            recall_score=model_recall_score,     #type: ignore
            precision_score=model_precision_score    #type: ignore

        )
        return classification_metric
    except Exception as e:
        raise AutoCareException(e,sys)

  