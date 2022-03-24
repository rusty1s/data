# Copyright (c) Facebook, Inc. and its affiliates.
from typing import Optional, Sequence, TypeVar

from torch.utils.data.datapipes.datapipe import MapDataPipe


T = TypeVar("T")


# @functional_datapipe("unzip")  # This line must be kept for .pyi signature parser
class UnZipperMapDataPipe:
    """
    Takes in a DataPipe of Sequences, unpacks each Sequence, and return the elements in separate DataPipes
    based on their position in the Sequence. The number of instances produced equals to the sequence legnth
    minus the number of columns to skip.

    Note:
        Each sequence within the DataPipe should have the same length, specified by
        the input argument `sequence_length`.

    Args:
        source_datapipe: Iterable DataPipe with sequences of data
        sequence_length: Length of the sequence within the source_datapipe. All elements should have the same length.
        columns_to_skip: optional indices of columns that the DataPipe should skip (each index should be
            an integer from 0 to sequence_length - 1)

    Example:
        >>> from torchdata.datapipes.iter import SequenceWrapper
        >>> source_dp = SequenceWrapper([(i, i + 10, i + 20) for i in range(3)])
        >>> dp1, dp2, dp3 = source_dp.unzip(sequence_length=3)
        >>> list(dp1)
        [0, 1, 2]
        >>> list(dp2)
        [10, 11, 12]
        >>> list(dp3)
        [20, 21, 22]
    """

    def __new__(
        cls,
        source_datapipe: MapDataPipe[Sequence[T]],
        sequence_length: int,
        columns_to_skip: Optional[Sequence[int]] = None,
    ):
        if sequence_length < 1:
            raise ValueError(f"Expected `sequence_length` larger than 0, but {sequence_length} is found")
        if columns_to_skip is None:
            instance_ids = list(range(sequence_length))
        else:
            skips = set(columns_to_skip)
            instance_ids = [i for i in range(sequence_length) if i not in skips]

        if len(instance_ids) == 0:
            raise RuntimeError(
                f"All instances are being filtered out in {cls.__name__}. Please check"
                "the input `sequence_length` and `columns_to_skip`."
            )
        return [_UnZipperMapDataPipe(source_datapipe, i) for i in instance_ids]


class _UnZipperMapDataPipe(MapDataPipe[T]):
    def __init__(self, main_datapipe: MapDataPipe[Sequence[T]], instance_id: int):
        self.main_datapipe = main_datapipe
        self.instance_id = instance_id

    def __getitem__(self, index):
        return self.main_datapipe[index][self.instance_id]

    def __len__(self):
        return len(self.main_datapipe)


MapDataPipe.register_datapipe_as_function("unzip", UnZipperMapDataPipe)
