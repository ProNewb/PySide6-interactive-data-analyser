import pandas as pd
import plotly.graph_objects as go

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget
)

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    ExtraTreesClassifier,
    ExtraTreesRegressor,
    RandomForestClassifier,
    RandomForestRegressor
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    explained_variance_score,
    median_absolute_error
)
from sklearn.model_selection import (
    KFold,
    StratifiedKFold,
    cross_val_predict,
    train_test_split
)
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC, SVR

from ui.graph.graph_widget import GraphWidget


class ModelTab(QWidget):
    """Train, evaluate, and inspect a supervised prediction model."""

    def __init__(self, dataframe_provider, parent=None):
        super().__init__(parent)
        self.dataframe_provider = dataframe_provider
        self.dataframe = None
        self.model = None
        self.pipeline = None
        self.predictions = None
        self.prediction_graph = GraphWidget()
        
        self.build_ui()
        self.refresh_data()

    def build_ui(self):
        outer_layout = QVBoxLayout(self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        scroll_area.setWidget(content_widget)
        outer_layout.addWidget(scroll_area)

        controls = QHBoxLayout()
        data_group = QGroupBox("Model data")
        data_form = QFormLayout(data_group)
        self.dataset_combo = QComboBox()
        self.task_combo = QComboBox()
        self.task_combo.addItem("Classification", "classification")
        self.task_combo.addItem("Regression", "regression")
        self.target_combo = QComboBox()
        self.missing_combo = QComboBox()
        self.missing_combo.addItem("Impute missing values", "impute")
        self.missing_combo.addItem("Drop rows with missing values", "drop")
        self.test_size = QSpinBox()
        self.test_size.setRange(10, 50)
        self.test_size.setValue(20)
        self.random_state = QSpinBox()
        self.random_state.setRange(0, 999999)
        self.random_state.setValue(42)
        self.validation_combo = QComboBox()
        self.validation_combo.addItem("Holdout split", "holdout")
        self.validation_combo.addItem("K-fold cross-validation", "kfold")
        self.folds_spin = QSpinBox()
        self.folds_spin.setRange(2, 10)
        self.folds_spin.setValue(5)
        self.stratify_check = QCheckBox("Stratify classification split")
        self.full_predictions_check = QCheckBox("Show full-dataset predictions")
        self.full_predictions_check.setChecked(True)
        data_form.addRow("Dataset", self.dataset_combo)
        data_form.addRow("Task", self.task_combo)
        data_form.addRow("Target", self.target_combo)
        data_form.addRow("Missing values", self.missing_combo)
        data_form.addRow("Test size (%)", self.test_size)
        data_form.addRow("Random state", self.random_state)
        data_form.addRow("Validation", self.validation_combo)
        data_form.addRow("Folds", self.folds_spin)
        data_form.addRow(self.stratify_check)
        data_form.addRow(self.full_predictions_check)
        controls.addWidget(data_group)

        model_group = QGroupBox("Model")
        model_form = QFormLayout(model_group)
        self.model_combo = QComboBox()
        self.model_combo.addItem("Logistic regression", "logistic")
        self.model_combo.addItem("Random forest", "random_forest")
        self.model_combo.addItem("Extra trees", "extra_trees")
        self.model_combo.addItem("K-nearest neighbours", "knn")
        self.model_combo.addItem("Support vector machine", "svm")
        self.model_combo.addItem("Linear regression", "linear")
        self.model_combo.addItem("K-nearest neighbours regressor", "knn_regressor")
        self.model_combo.addItem("Support vector regressor", "svm_regressor")
        self.model_combo.addItem("Random forest regressor", "random_forest_regressor")
        self.model_combo.addItem("Extra trees regressor", "extra_trees_regressor")
        model_form.addRow("Algorithm", self.model_combo)
        self.scale_check = QCheckBox("Scale numeric features")
        self.scale_check.setChecked(True)
        model_form.addRow(self.scale_check)
        controls.addWidget(model_group)
        layout.addLayout(controls)

        features_group = QGroupBox("Features")
        features_layout = QVBoxLayout(features_group)
        self.feature_widget = QWidget()
        self.feature_grid = QGridLayout(self.feature_widget)
        features_layout.addWidget(self.feature_widget)
        layout.addWidget(features_group)

        actions = QHBoxLayout()
        self.train_button = QPushButton("Train model")
        self.refresh_button = QPushButton("Refresh datasets")
        actions.addWidget(self.train_button)
        actions.addWidget(self.refresh_button)
        actions.addStretch()
        layout.addLayout(actions)

        self.metrics_output = QTextEdit()
        self.metrics_output.setReadOnly(True)
        self.metrics_output.setPlaceholderText("Training metrics and validation details")
        layout.addWidget(self.metrics_output)

        self.prediction_table = QTableWidget()
        self.prediction_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.prediction_table.setMinimumHeight(280)
        layout.addWidget(self.prediction_table)
        layout.addWidget(QLabel("Prediction plot"))
        layout.addWidget(self.prediction_graph)

        self.dataset_combo.currentIndexChanged.connect(self.refresh_data)
        self.target_combo.currentIndexChanged.connect(self.rebuild_features)
        self.task_combo.currentIndexChanged.connect(self.update_models)
        self.task_combo.currentIndexChanged.connect(self.rebuild_targets)
        self.validation_combo.currentIndexChanged.connect(self.update_validation_controls)
        self.model_combo.currentIndexChanged.connect(self.update_model_options)
        self.refresh_button.clicked.connect(self.refresh_data)
        self.train_button.clicked.connect(self.train_model)
        self.update_models()
        self.update_validation_controls()

    def update_validation_controls(self):
        is_kfold = self.validation_combo.currentData() == "kfold"
        self.test_size.setEnabled(not is_kfold)
        self.folds_spin.setEnabled(is_kfold)

    def refresh_data(self):
        frames = self.dataframe_provider()
        current = self.dataset_combo.currentData()
        self.dataset_combo.blockSignals(True)
        self.dataset_combo.clear()
        for key, label, dataframe in frames:
            if dataframe is not None:
                self.dataset_combo.addItem(label, key)
        self.dataset_combo.blockSignals(False)
        if current is not None:
            index = self.dataset_combo.findData(current)
            if index >= 0:
                self.dataset_combo.setCurrentIndex(index)
        self.load_selected_dataframe()

    def load_selected_dataframe(self):
        frames = {
            key: dataframe
            for key, _, dataframe in self.dataframe_provider()
        }
        self.dataframe = frames.get(self.dataset_combo.currentData())
        self.rebuild_targets()
        self.rebuild_features()

    def rebuild_targets(self):
        current = self.target_combo.currentData()
        self.target_combo.blockSignals(True)
        self.target_combo.clear()
        if self.dataframe is not None:
            for column in self.dataframe.columns:
                series = self.dataframe[column]
                classification = (
                    self.task_combo.currentData() == "classification"
                )
                numeric = pd.api.types.is_numeric_dtype(series)
                if classification:
                    allowed = (
                        not numeric
                        or series.nunique(dropna=True)
                        <= max(20, int(len(series) * 0.2))
                    )
                else:
                    allowed = numeric and not pd.api.types.is_bool_dtype(series)
                if allowed:
                    self.target_combo.addItem(str(column), column)
        self.target_combo.blockSignals(False)
        if current is not None:
            index = self.target_combo.findData(current)
            if index >= 0:
                self.target_combo.setCurrentIndex(index)
        if self.target_combo.currentIndex() < 0 and self.target_combo.count():
            self.target_combo.setCurrentIndex(0)

    def rebuild_features(self):
        while self.feature_grid.count():
            item = self.feature_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if self.dataframe is None:
            return
        target = self.target_combo.currentData()
        self.feature_checks = []
        for index, column in enumerate(self.dataframe.columns):
            if column == target:
                continue
            check = QCheckBox(str(column))
            check.setChecked(True)
            self.feature_grid.addWidget(check, index // 4, index % 4)
            self.feature_checks.append((column, check))

    def update_models(self):
        classification = self.task_combo.currentData() == "classification"
        classification_models = {
            "logistic", "random_forest", "extra_trees", "knn", "svm"
        }
        regression_models = {
            "linear", "knn_regressor", "svm_regressor",
            "random_forest_regressor", "extra_trees_regressor"
        }
        allowed = classification_models if classification else regression_models
        for index in range(self.model_combo.count()):
            value = self.model_combo.itemData(index)
            self.model_combo.model().item(index).setEnabled(
                classification == (value in allowed)
            )
        if not classification:
            self.model_combo.setCurrentIndex(
                self.model_combo.findData("linear")
            )
        else:
            self.model_combo.setCurrentIndex(
                self.model_combo.findData("logistic")
            )
        self.update_model_options()

    def update_model_options(self):
        classification = self.task_combo.currentData() == "classification"
        self.stratify_check.setEnabled(classification)

    def selected_features(self):
        return [column for column, check in self.feature_checks if check.isChecked()]

    def make_estimator(self):
        name = self.model_combo.currentData()
        state = self.random_state.value()
        if name == "logistic":
            return LogisticRegression(max_iter=1000, random_state=state)
        if name == "random_forest":
            return RandomForestClassifier(n_estimators=200, random_state=state)
        if name == "extra_trees":
            return ExtraTreesClassifier(n_estimators=200, random_state=state)
        if name == "knn":
            return KNeighborsClassifier()
        if name == "svm":
            return SVC(probability=True, random_state=state)
        if name == "linear":
            return LinearRegression()
        if name == "knn_regressor":
            return KNeighborsRegressor()
        if name == "svm_regressor":
            return SVR()
        if name == "random_forest_regressor":
            return RandomForestRegressor(n_estimators=200, random_state=state)
        return ExtraTreesRegressor(n_estimators=200, random_state=state)

    def train_model(self):
        if self.dataframe is None:
            self.show_error("Load a dataset before training a model.")
            return
        target = self.target_combo.currentData()
        features = self.selected_features()
        if target is None or not features:
            self.show_error("Choose a target and at least one feature.")
            return
        try:
            data = self.dataframe[features + [target]].copy()
            if self.missing_combo.currentData() == "drop":
                data = data.dropna()
            X = data[features]
            y = data[target]
            classification = self.task_combo.currentData() == "classification"
            if classification and y.nunique() < 2:
                raise ValueError("Classification requires at least two target classes.")
            if classification and pd.api.types.is_numeric_dtype(y):
                if y.nunique() > max(20, int(len(y) * 0.2)):
                    raise ValueError(
                        "This target looks continuous. Select Regression "
                        "instead of Classification."
                    )
            if not classification and not pd.api.types.is_numeric_dtype(y):
                raise ValueError(
                    "Regression requires a numeric target column."
                )
            if len(data) < 4:
                raise ValueError("At least four usable rows are required.")
            numeric = X.select_dtypes(include="number").columns.tolist()
            categorical = [column for column in features if column not in numeric]
            steps_numeric = [("imputer", SimpleImputer(strategy="median"))]
            if self.scale_check.isChecked():
                steps_numeric.append(("scale", StandardScaler()))
            numeric_pipeline = Pipeline(steps_numeric)
            categorical_pipeline = Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encode", OneHotEncoder(handle_unknown="ignore"))
            ])
            transformers = []
            if numeric:
                transformers.append(("numeric", numeric_pipeline, numeric))
            if categorical:
                transformers.append(("categorical", categorical_pipeline, categorical))
            preprocessor = ColumnTransformer(transformers=transformers)
            estimator = self.make_estimator()
            self.pipeline = Pipeline([
                ("preprocess", preprocessor),
                ("model", estimator)
            ])
            stratify = y if classification and self.stratify_check.isChecked() else None
            if self.validation_combo.currentData() == "kfold":
                if classification:
                    splitter = StratifiedKFold(
                        n_splits=self.folds_spin.value(),
                        shuffle=True,
                        random_state=self.random_state.value()
                    )
                else:
                    splitter = KFold(
                        n_splits=self.folds_spin.value(),
                        shuffle=True,
                        random_state=self.random_state.value()
                    )
                predictions = cross_val_predict(
                    self.pipeline,
                    X,
                    y,
                    cv=splitter
                )
                X_eval, y_eval = X, y
                self.pipeline.fit(X, y)
            else:
                try:
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y,
                        test_size=self.test_size.value() / 100,
                        random_state=self.random_state.value(),
                        stratify=stratify
                    )
                except ValueError as split_error:
                    if stratify is None:
                        raise
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y,
                        test_size=self.test_size.value() / 100,
                        random_state=self.random_state.value(),
                        stratify=None
                    )
                    self.metrics_output.setPlainText(
                        f"Stratified split unavailable; used a random split.\n"
                        f"Reason: {split_error}"
                    )
                self.pipeline.fit(X_train, y_train)
                predictions = self.pipeline.predict(X_test)
                X_eval, y_eval = X_test, y_test
            self.model = self.pipeline
            self.predictions = predictions
            if classification:
                metrics = (
                    f"Accuracy: {accuracy_score(y_eval, predictions):.4f}\n"
                    f"Balanced accuracy: {balanced_accuracy_score(y_eval, predictions):.4f}\n"
                    f"Precision (weighted): {precision_score(y_eval, predictions, average='weighted', zero_division=0):.4f}\n"
                    f"Recall (weighted): {recall_score(y_eval, predictions, average='weighted', zero_division=0):.4f}\n"
                    f"F1 (weighted): {f1_score(y_eval, predictions, average='weighted', zero_division=0):.4f}\n"
                    f"Evaluated rows: {len(y_eval)}"
                )
            else:
                metrics = (
                    f"R²: {r2_score(y_eval, predictions):.4f}\n"
                    f"Explained variance: {explained_variance_score(y_eval, predictions):.4f}\n"
                    f"MAE: {mean_absolute_error(y_eval, predictions):.4f}\n"
                    f"Median absolute error: {median_absolute_error(y_eval, predictions):.4f}\n"
                    f"RMSE: {mean_squared_error(y_eval, predictions) ** 0.5:.4f}\n"
                    f"Evaluated rows: {len(y_eval)}"
                )
            self.metrics_output.setPlainText(metrics)
            if self.validation_combo.currentData() == "kfold" or self.full_predictions_check.isChecked():
                all_predictions = self.pipeline.predict(X)
                if self.validation_combo.currentData() == "kfold":
                    self.display_predictions(X, y, predictions)
                else:
                    self.display_predictions(X, y, all_predictions)
            else:
                self.display_predictions(X_eval, y_eval, predictions)
            try:
                self.display_prediction_graph(y_eval, predictions, classification)
            except (ValueError, TypeError) as graph_error:
                self.metrics_output.append(
                    f"Prediction graph unavailable: {graph_error}"
                )
        except (ValueError, TypeError, KeyError) as error:
            self.show_error(str(error))

    def display_predictions(self, X_test, y_test, predictions):
        output = X_test.copy()
        output["actual"] = y_test.to_numpy()
        output["predicted"] = predictions
        self.prediction_table.setRowCount(len(output))
        self.prediction_table.setColumnCount(len(output.columns))
        self.prediction_table.setHorizontalHeaderLabels([str(column) for column in output.columns])
        for row in range(len(output)):
            for column in range(len(output.columns)):
                self.prediction_table.setItem(
                    row, column, QTableWidgetItem(str(output.iat[row, column]))
                )

    def display_prediction_graph(self, actual, predicted, classification):
        if classification:
            figure = go.Figure()
            figure.add_trace(go.Scatter(
                x=list(range(len(actual))),
                y=actual,
                mode="markers",
                name="Actual"
            ))
            figure.add_trace(go.Scatter(
                x=list(range(len(predicted))),
                y=predicted,
                mode="markers",
                name="Predicted"
            ))
            figure.update_layout(
                title="Actual versus predicted classes",
                xaxis_title="Test row",
                yaxis_title="Class"
            )
        else:
            actual_values = pd.to_numeric(actual)
            predicted_values = pd.to_numeric(predicted)
            low = min(actual_values.min(), predicted_values.min())
            high = max(actual_values.max(), predicted_values.max())
            figure = go.Figure()
            figure.add_trace(go.Scatter(
                x=actual_values,
                y=predicted_values,
                mode="markers",
                name="Predictions"
            ))
            figure.add_trace(go.Scatter(
                x=[low, high],
                y=[low, high],
                mode="lines",
                name="Ideal"
            ))
            figure.update_layout(
                title="Actual versus predicted values",
                xaxis_title="Actual",
                yaxis_title="Predicted"
            )
        self.prediction_graph.display_graph(figure)

    def show_error(self, message):
        self.metrics_output.setPlainText(f"Error: {message}")
        self.prediction_table.clearContents()
        self.prediction_table.setRowCount(0)
