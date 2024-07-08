from django.db import models
from django.utils.translation import gettext_lazy as _


class Node(models.Model):
    """
        Class for Casper Node
    """
    ip = models.GenericIPAddressField(_("IP Address"), max_length=16)
    public_key = models.CharField(_("Public Key"), max_length=128, default='')
    height = models.BigIntegerField(_("Height"), default=0)
    network_weight = models.BigIntegerField(_("Network Weight"), default=0)
    total_stake = models.BigIntegerField(_("Total Stake"), default=0)
    active_bid = models.BooleanField(_("Active Bid"), default=False)
    percent_of_network = models.FloatField(_("Percent Of Network"), default=0)

    class Meta:
        ordering = ('-total_stake', '-height',)
        verbose_name = _("Node")
        verbose_name_plural = _("Nodes")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.public_key}"


class Score(models.Model):
    """
        Class for Casper Node 5 Minute Score
    """
    node = models.ForeignKey(Node, on_delete=models.CASCADE, verbose_name=(_("Node")))
    current_block = models.BigIntegerField(_("Current Block"), default=0)
    network_weight = models.BigIntegerField(_("Network Weight"), default=0)
    total_stake = models.BigIntegerField(_("Total Stake"), default=0)
    active_bid = models.BooleanField(_("Active Bid"), default=False)
    percent_of_network = models.FloatField(_("Percent Of Network"), default=0)
    active = models.BooleanField(_("Active"), default=False)
    timestamp = models.DateTimeField(_("Timestamp"), auto_now_add=True)

    class Meta:
        ordering = ('-current_block', '-total_stake',)
        verbose_name = _("Score")
        verbose_name_plural = _("Scores")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.node.public_key}"


class Scoring(models.Model):
    """
        Class for Casper Node Scoring
    """
    TYPE_CHOICES = [
        ('D', 'Day'),
        ('W', 'Week'),
        ('Q', 'Quarter')
    ]

    public_key = models.CharField(_("Public Key"), max_length=128, default='')
    type = models.CharField(_("Type"), max_length=1, choices=TYPE_CHOICES, default='D')
    score = models.FloatField(_("Score"), default=0)
    longevity = models.FloatField(_("Longevity"), default=0)
    stake_over = models.BooleanField(_("Stake Over"), default=False)
    eligible_for_rewards = models.BooleanField(_("Eligible for Rewards"), default=False)
    timestamp = models.CharField(_("Timestamp"), max_length=128)

    class Meta:
        ordering = ('-score', '-longevity',)
        verbose_name = _("Scoring")
        verbose_name_plural = _("Scoring")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.public_key}"
