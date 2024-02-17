from typing import Any, Optional

import matplotlib.ticker
from icecream import ic
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from path import Path


class Graph:
    def __init__(
        self,
        name: str,
        main_axis: list[int],
        *,
        horizontal: bool = False,
        other_axis: Optional[list[int]] = None,
        main_ticks: Optional[list[int]] = None,
        other_ticks: Optional[list[int]] = None,
        xtick_labels: Optional[list[Any]] = None,
        ytick_labels: Optional[list[Any]] = None,
        tick_pad: int = 20,
        tick_size: int = 35,
        xlabel: str = '',
        ylabel: str = '',
        label_size: int = 60,
        label_pad: int = 60,
        text_and_borders_color: str = 'white',
        background_color: str = '#1f262b',
        bar_color: str = 'cyan',
        figsize: tuple[int, int] = (40, 25),
        xposition: float = 0.105,
        yposition: float = 0.15,
    ) -> None:
        self.fig: Figure = plt.subplots(figsize=figsize)[0]
        self.ax: Axes = self.fig.axes[0]

        self.name = name
        self.tick_pad = tick_pad
        self.text_and_borders_color = text_and_borders_color
        self.background_color = background_color
        self.bar_color = bar_color
        self.tick_size = tick_size

        position = self.ax.get_position()
        position.x0 = xposition  # pyright: ignore
        position.y0 = yposition  # pyright: ignore
        self.ax.set_position(position)

        self.ax.set_xlabel(xlabel, color=self.text_and_borders_color, fontsize=label_size, labelpad=label_pad)
        self.ax.set_ylabel(ylabel, color=self.text_and_borders_color, fontsize=label_size, labelpad=label_pad)

        if other_axis is None:
            other_axis = list(range(len(main_axis)))
        self.y, self.x = main_axis, other_axis

        yticks, xticks = main_ticks, other_ticks
        if xticks is None:
            xticks = list(range(len(self.x)))
        if yticks is None:
            yticks = _few_ticks(max(self.y))

        if horizontal:
            self.y, self.x = self.x, self.y
            yticks, xticks = xticks, yticks
            self._barh()
        else:
            self._bar()

        self.ax.set_xticks(xticks, xtick_labels)
        self.ax.set_yticks(yticks, ytick_labels)
        self._prettify()

    def _bar(self) -> None:
        self.ax.bar(height=self.y, x=self.x, color=self.bar_color, align='center', width=0.75)

        for annotation_x, annotation_y in zip(self.x, self.y):
            self.ax.annotate(
                str(annotation_y),
                xy=(annotation_x, annotation_y + max(self.y) / 100),
                ha='center',
                fontsize=self.tick_size,
                color=self.text_and_borders_color,
            )

    def _barh(self) -> None:
        self.ax.barh(width=self.x, y=self.y, color=self.bar_color, align='center', height=0.75)

        for annotation_x, annotation_y in zip(self.x, self.y):
            self.ax.annotate(
                str(annotation_x),
                xy=(annotation_x + max(self.x) / 150, annotation_y),
                va='center',
                fontsize=self.tick_size,
                color=self.text_and_borders_color,
            )

    def _prettify(self) -> None:
        self.fig.set_facecolor(self.background_color)
        self.ax.set_facecolor(self.background_color)
        self.ax.tick_params(axis='y', colors=self.text_and_borders_color, labelsize=self.tick_size, pad=self.tick_pad)
        self.ax.tick_params(axis='x', colors=self.text_and_borders_color, labelsize=self.tick_size, pad=self.tick_pad)
        self.ax.spines['top'].set_color(self.text_and_borders_color)
        self.ax.spines['right'].set_color(self.text_and_borders_color)
        self.ax.spines['bottom'].set_color(self.text_and_borders_color)
        self.ax.spines['left'].set_color(self.text_and_borders_color)

    def save(self, dir_: str) -> None:
        self.fig.savefig(Path(dir_) / self.name + '.png')


def _few_ticks(max_tick: int, min_tick: int = 0) -> list[int]:
    auto_locator = matplotlib.ticker.AutoLocator()
    auto_locator.create_dummy_axis()
    return list(map(int, auto_locator.tick_values(min_tick, max_tick)))
