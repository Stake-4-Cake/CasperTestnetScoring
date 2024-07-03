from django.contrib import admin

from src.core import models


@admin.register(models.Node)
class NodeAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('public_key', 'height', 'network_weight', 'total_stake', 'active_bid', 'percent_of_network',)
    list_display_links = ('public_key',)
    search_fields = ('public_key',)
    list_filter = ('height', 'active_bid', )
    list_per_page = 1_000
    list_max_show_all = 10_000


@admin.register(models.Score)
class ScoreAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('node', 'current_block', 'network_weight', 'total_stake', 'active_bid', 'percent_of_network',
                    'active', 'timestamp',)
    list_display_links = ('node',)
    search_fields = ('node__public_key', 'current_block', 'timestamp',)
    list_filter = ('active_bid', 'active', 'timestamp',)
    list_per_page = 1_000
    list_max_show_all = 10_000


@admin.register(models.Scoring)
class ScoringAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('node', 'score', 'longevity', 'type', 'stake_over', 'eligible_for_rewards', 'timestamp',)
    list_display_links = ('node',)
    search_fields = ('node__public_key', 'timestamp',)
    list_filter = ('type', 'stake_over', 'eligible_for_rewards', 'timestamp',)
    list_per_page = 1_000
    list_max_show_all = 10_000
