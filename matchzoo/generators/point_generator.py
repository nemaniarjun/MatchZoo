"""Matchzoo point generator."""

import numpy as np
from matchzoo import engine
from matchzoo import tasks
from matchzoo.datapack import DataPack


class PointGenerator(engine.BaseGenerator):
    """PointGenerator for Matchzoo.

    Ponit generator can be used for classification as well as ranking.

    Examples:
        >>> data = [{
        ... 'text_left':[1,2],
        ... 'text_right': [3,4],
        ... 'label': 0,
        ... 'id_left': 'id0',
        ... 'id_right': 'id1'
        ... }]
        >>> input = DataPack(data)
        >>> task = tasks.Classification(num_classes=2)
        >>> from matchzoo.generators import PointGenerator
        >>> generator = PointGenerator(input, task, 1, True)
        >>> x, y = generator[0]

    """

    def __init__(
        self,
        inputs: DataPack,
        task: engine.BaseTask=tasks.Classification,
        batch_size: int=32,
        shuffle: bool=True
    ):
        """Construct the point generator.

        :param inputs: the output generated by :class:`DataPack`.
        :param task: the task is a instance of :class:`engine.BaseTask`.
        :param batch_size: number of instances in a batch.
        :param shuffle: whether to shuffle the instances while generating a
        batch.
        """
        self._task = task
        transformed_inputs = self.transform_data(inputs)
        self.x_left, self.x_right, self.y, self.id_left, self.id_right \
            = transformed_inputs
        super().__init__(batch_size, len(inputs.dataframe), shuffle)

    def transform_data(self, inputs: DataPack):
        """Obtain the transformed data from :class:`DataPack`.

        :param inputs: An instance of :class:`DataPack` to be transformed.
        :return: the output of all the transformed inputs.

        """
        data = inputs.dataframe
        x_left = np.asarray(data.text_left)
        x_right = np.asarray(data.text_right)
        y = np.asarray(data.label)
        id_left = np.asarray(data.id_left)
        id_right = np.asarray(data.id_right)
        return x_left, x_right, y, id_left, id_right

    def _get_batch_of_transformed_samples(self, index_array: list):
        """Get a batch of samples based on their ids.

        :param index_array: a list of instance ids.

        :return: A batch of transformed samples.

        """
        batch_size = len(index_array)
        batch_x_left = []
        batch_x_right = []
        batch_id_left = []
        batch_id_right = []
        if isinstance(self._task, tasks.Ranking):
            batch_y = self.y
        elif isinstance(self._task, tasks.Classification):
            batch_y = np.zeros((batch_size, self._task._num_classes),
                               dtype=np.int32)
            for i, label in enumerate(self.y[index_array]):
                batch_y[i, label] = 1
        else:
            msg = "{self._task} is not a valid target mode, "
            msg += ":class:`Ranking` and :class:`Classification` expected."
            raise ValueError(msg)

        for key, val in enumerate(index_array):
            batch_x_left.append(self.x_left[val])
            batch_x_right.append(self.x_right[val])
            batch_id_left.append(self.id_left[val])
            batch_id_right.append(self.id_right[val])

        return ({'x_left': np.array(batch_x_left), 'x_right':
                 np.array(batch_x_right), 'id_left':
                 batch_id_left, 'id_right': batch_id_right},
                np.array(batch_y))
