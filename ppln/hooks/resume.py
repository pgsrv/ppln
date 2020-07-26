from ..utils.checkpoint import load_checkpoint
from .base import BaseHook
from .priority import Priority
from .registry import HOOKS


@HOOKS.register_module
class ResumeHook(BaseHook):
    def __init__(
        self,
        checkpoint,
        resume_optimizer=True,
        resume_scheduler=True,
        resume_iter=True,
        strict=False,
        map_location="cpu",
        ignore_loaded_keys=(),
    ):
        self.checkpoint = checkpoint
        self.resume_optimizer = resume_optimizer
        self.resume_scheduler = resume_scheduler
        self.resume_iter = resume_iter
        self.strict = strict
        self.map_location = map_location
        self.ignore_loaded_keys = ignore_loaded_keys

    @property
    def priority(self):
        return Priority.HIGHEST

    def before_run(self, runner):
        runner.logger.info(f"Resume from {self.checkpoint}")
        checkpoint = load_checkpoint(
            runner.model,
            self.checkpoint,
            map_location=self.map_location,
            strict=self.strict,
            optimizer=runner.optimizer if self.resume_optimizer else None,
            scheduler=runner.scheduler if self.resume_scheduler else None,
            ignore_loaded_keys=self.ignore_loaded_keys,
        )

        if self.resume_iter:
            runner.epoch = checkpoint["meta"]["epoch"]
            runner.iter = checkpoint["meta"]["iter"]
            runner.logger.info(f"Resumed epoch: {runner.epoch}, iter: {runner.iter}")
