import warnings

from torch.nn import SyncBatchNorm

from ..factory import make_apex_ddp, make_pytorch_ddp
from .base import BaseClosureHook
from .priority import Priority
from .registry import HOOKS

try:
    from apex.parallel import convert_syncbn_model as apex_convert_sync_batchnorm
except ImportError as e:
    warnings.warn(
        f'Error "{e}" during importing apex library. To use mixed precison'
        " you should install it from https://github.com/NVIDIA/apex"
    )


@HOOKS.register_module
class ModelClosureHook(BaseClosureHook):
    @property
    def priority(self):
        return Priority.HIGH

    def before_run(self, runner):
        runner.model = self._func(runner.model)


@HOOKS.register_module
class PytorchDDPHook(ModelClosureHook):
    def __init__(self, **kwargs):
        super().__init__(make_pytorch_ddp, **kwargs)


@HOOKS.register_module
class ApexDDPHook(ModelClosureHook):
    def __init__(self, **kwargs):
        super().__init__(make_apex_ddp, **kwargs)


@HOOKS.register_module
class ApexSyncBNHook(ModelClosureHook):
    def __init__(self, **kwargs):
        super().__init__(apex_convert_sync_batchnorm, **kwargs)


@HOOKS.register_module
class PytorchSyncBNHook(ModelClosureHook):
    def __init__(self, **kwargs):
        super().__init__(SyncBatchNorm.convert_sync_batchnorm, **kwargs)
