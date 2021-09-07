"""EGBAD experiments suite."""

from pathlib import Path
from typing import Dict

import tensorflow as tf

from anomaly_toolbox.datasets.dataset import AnomalyDetectionDataset
from anomaly_toolbox.experiments.experiment import Experiment
from anomaly_toolbox.hps import hparam_parser
from anomaly_toolbox.trainers import EGBAD


class EGBADExperiment(Experiment):
    """
    EGBAD experiment.
    """

    def __init__(self, hparams_path: Path, log_dir: Path):
        super().__init__(hparams_path, log_dir)

        # Get the hyperparameters
        self._hps = hparam_parser(
            hparams_path,
            "egbad",
            list(self.hyperparameters().union(EGBAD.hyperparameters())),
        )

    def experiment(
        self, hps: Dict, log_dir: Path, dataset: AnomalyDetectionDataset
    ) -> None:
        """Experiment execution - architecture specific.
        Args:
            hps: Dictionary with the parameters to use for the current run.
            log_dir: Where to store the tensorboard logs.
            dataset: The dataset to use for model training and evaluation.
        """
        print("Running EGBAD experiment...")

        summary_writer = tf.summary.create_file_writer(str(log_dir))
        new_size = (28, 28)

        # Create the dataset with the requested sizes (requested by the model architecture)
        dataset.configure(
            anomalous_label=hps["anomalous_label"],
            class_label=hps["class_label"],
            batch_size=hps["batch_size"],
            new_size=new_size,
            shuffle_buffer_size=hps["shuffle_buffer_size"],
        )

        # Create the EGBAD trainer
        trainer = EGBAD(
            dataset=dataset,
            hps=hps,
            summary_writer=summary_writer,
            log_dir=log_dir,
        )

        # Train the EGBAD model
        trainer.train(
            epochs=hps["epochs"],
            step_log_frequency=hps["step_log_frequency"],
        )

        # Test on test dataset and put the results in the json file (the same file used inside the
        # training for the model selection)
        trainer.test()
