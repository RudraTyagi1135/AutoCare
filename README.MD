machine_learning/
└── training/
    └── diabetes/
        └── diabetes_work/
            ├── logs/
            │   └── diabetes_training_<timestamp>.log        # Pipeline logs for each run
            │
            ├── Artifacts/
            │   └── <timestamp>/
            │       ├── data_ingestion/                      # Raw, train, test data
            │       ├── data_validation/                     # Drift reports, validated data
            │       ├── data_transformation/                 # Transformed data + preprocessor object
            │       └── model_trainer/                       # Trained model checkpoints
            │
            ├── model_processor/
            │   ├── model.pkl                                # Final trained model
            │   └── preprocessor.pkl                          # Corresponding preprocessing object
            │
            ├── schema/
            │   └── diabetes_schema.yaml                     # Validation schema for dataset
            │
            ├── components/                                  # Core pipeline components
            │   ├── data_ingestion.py
            │   ├── data_validation.py
            │   ├── data_transformation.py
            │   └── model_trainer.py
            │
            ├── entity/                                      # Configuration & artifact entities
            ├── test.py                                      # Pipeline runner
            └── constant/                                    # Constant values & file names


🧩 New Enhancements

✅ Logs are now pipeline-specific (diabetes_work/logs)
✅ Artifacts are saved under their respective pipeline folder
✅ Model and preprocessor stored together in model_processor/
✅ Detailed logs include:

GridSearchCV best parameters

F1, precision, recall for train/test

Model comparison summary
✅ Fully modular for extending to heart and stroke datasets later


Run the Training Pipeline
python machine_learning/training/diabetes/diabetes_work/test.py